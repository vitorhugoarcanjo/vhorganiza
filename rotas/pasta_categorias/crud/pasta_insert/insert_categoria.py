# rotas/pasta_categorias/crud/pasta_insert/insert_categoria.py
# ==========================================================
# INSERIR CATEGORIA - VIEW FUNCS
# ==========================================================

import json
import logging
from flask import request, session, jsonify, render_template

from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_categorias.services_auditoria import AuditoriaCategoriasService
from utils.database.conexao_global import ini_conexao

from .services import InserirCategoriaService
from .validacoes import validar_dados_insercao

logger = logging.getLogger(__name__)


# ==========================================================
# 1. GET - RETORNA O HTML DO MODAL
# ==========================================================
@login_required
def nova_categoria_modal():
    modulo = request.args.get('modulo', 'tarefas')
    if modulo not in ('tarefas', 'financas'):
        modulo = 'tarefas'

    return render_template(
        'pasta_categorias/modais/modal_nova_categoria.html.jinja',
        modulo=modulo
    )


# ==========================================================
# 2. POST - SALVA A CATEGORIA (JSON) + AUDITORIA
# ==========================================================
@login_required
def salvar_nova_categoria():
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        payload = request.json or {}

        dados = {
            'nome':   (payload.get('nome') or '').strip(),
            'cor':    (payload.get('cor') or '#CCCCCC').strip(),
            'modulo': (payload.get('modulo') or '').strip(),
        }

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        sucesso, resultado = InserirCategoriaService.criar_categoria(cursor, usuario_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400

        # 🔥 Auditoria — captura TODOS os campos
        alteracoes = [
            {'campo': 'Nome',   'depois': dados['nome']},
            {'campo': 'Cor',    'depois': dados['cor']},
            {'campo': 'Módulo', 'depois': dados['modulo'].title()},
            {'campo': 'Número', 'depois': resultado['numero']},
        ]

        AuditoriaCategoriasService.registrar(
            categoria_id=resultado['categoria_id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Categoria "{dados["nome"]}" cadastrada com sucesso!',
            'categoria_id': resultado['categoria_id'],
            'sequencia':    resultado['sequencia'],
            'numero':       resultado['numero'],
        }), 201

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar nova categoria usuario_id={usuario_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao salvar a categoria.',
            'details': str(e)
        }), 500
    finally:
        conexao.close()