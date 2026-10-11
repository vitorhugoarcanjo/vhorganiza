# rotas/pasta_categorias/crud/pasta_edit/edit_categoria.py
# ==========================================================
# EDITAR CATEGORIA - VIEW FUNCS
# ==========================================================

import json
import logging
from flask import request, session, jsonify, render_template

from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_categorias.services_auditoria import AuditoriaCategoriasService
from utils.database.conexao_global import ini_conexao

from .services import EditarCategoriaService
from .validacoes import validar_dados_edicao
from rotas.pasta_categorias.formatters import CategoriasFormatters

logger = logging.getLogger(__name__)


# ==========================================================
# 1. GET - RETORNA O HTML DO MODAL COM DADOS
# ==========================================================
@login_required
def editar_categoria_modal(categoria_id):
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        categoria_raw = EditarCategoriaService.buscar_categoria_por_id(cursor, categoria_id, usuario_id)
        if not categoria_raw:
            return '', 404

        categoria = CategoriasFormatters.formatar_detalhes(categoria_raw)

        return render_template(
            'pasta_categorias/modais/modal_editar_categoria.html.jinja',
            categoria=categoria
        )
    finally:
        conexao.close()


# ==========================================================
# 2. POST - SALVA A EDIÇÃO (JSON) + AUDITORIA
# ==========================================================
@login_required
def salvar_edicao_categoria(categoria_id):
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        payload = request.json or {}

        dados = {
            'nome': (payload.get('nome') or '').strip(),
            'cor':  (payload.get('cor') or '#CCCCCC').strip(),
        }

        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        resultado = EditarCategoriaService.atualizar_categoria(cursor, categoria_id, usuario_id, dados)
        if not resultado['success']:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado['error']}), 400

        # 🔥 Auditoria — monta diff
        alteracoes = _montar_diff(resultado['dados_antes'], resultado['dados_depois'])

        if alteracoes:
            AuditoriaCategoriasService.registrar(
                categoria_id=resultado['id_interno'],
                acao='editada',
                campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'].lower(),
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Categoria "{dados["nome"]}" atualizada com sucesso!',
        }), 200

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao editar categoria id={categoria_id} usuario_id={usuario_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao editar a categoria.',
            'details': str(e)
        }), 500
    finally:
        conexao.close()


def _montar_diff(antes, depois):
    """Monta a lista de alterações [{campo, antes, depois}]"""
    alteracoes = []

    if antes.get('nome') != depois.get('nome'):
        alteracoes.append({
            'campo': 'Nome',
            'antes': antes.get('nome') or '(vazio)',
            'depois': depois.get('nome') or '(vazio)',
        })

    if antes.get('cor') != depois.get('cor'):
        alteracoes.append({
            'campo': 'Cor',
            'antes': antes.get('cor') or '(vazio)',
            'depois': depois.get('cor') or '(vazio)',
        })

    return alteracoes