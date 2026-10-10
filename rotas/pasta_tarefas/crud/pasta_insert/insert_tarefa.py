# rotas/pasta_tarefas/crud/pasta_insert/insert_tarefa.py
# ==========================================================
# INSERIR TAREFA - VIEW FUNCS
# ==========================================================

import logging
import json
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_tarefas.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from .services import InserirTarefaService
from .validacoes import validar_dados_insercao

logger = logging.getLogger(__name__)


def _fmt_data_br(data_iso):
    """Converte 'YYYY-MM-DD' pra 'DD/MM/YYYY'."""
    if not data_iso:
        return ''
    s = str(data_iso)[:10]
    if len(s) == 10 and s[4] == '-':
        return f'{s[8:10]}/{s[5:7]}/{s[0:4]}'
    return s


# ==========================================================
# 1. GET - RETORNA O HTML DO MODAL
# ==========================================================
@login_required
def nova_tarefa_modal():
    usuario_id = session.get('user_id')

    conexao, cursor = ini_conexao()
    try:
        categorias = InserirTarefaService.buscar_categorias(cursor, usuario_id)
        return render_template(
            'pasta_tarefas/modais/modal_nova_tarefa.html.jinja',
            categorias=categorias
        )
    finally:
        conexao.close()


# ==========================================================
# 2. POST - SALVA A TAREFA (JSON) + AUDITORIA
# ==========================================================
@login_required
def salvar_nova_tarefa():
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        payload = request.json or {}

        dados = {
            'titulo':       (payload.get('titulo') or '').strip(),
            'descricao':    (payload.get('descricao') or '').strip(),
            'status':       payload.get('status') or 'pendente',
            'prioridade':   payload.get('prioridade') or 'media',
            'data_inicio':  payload.get('data_inicio') or None,
            'data_final':   payload.get('data_final') or None,
            'categoria_id': payload.get('categoria_id') or None,
        }

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        # 🔥 Busca o NOME da categoria ANTES de criar
        categoria_nome = InserirTarefaService.buscar_nome_categoria(cursor, dados['categoria_id'])

        sucesso, resultado = InserirTarefaService.criar_tarefa(cursor, usuario_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400

        # 🔥 Auditoria — captura TODOS os campos
        alteracoes = [
            {'campo': 'Título',       'depois': dados['titulo']},
            {'campo': 'Descrição',    'depois': dados['descricao'] or '(vazio)'},
            {'campo': 'Status',       'depois': dados['status'].title()},
            {'campo': 'Prioridade',   'depois': dados['prioridade'].title()},
            {'campo': 'Data Início',  'depois': _fmt_data_br(dados['data_inicio']) or '(vazio)'},
            {'campo': 'Data Final',   'depois': _fmt_data_br(dados['data_final']) or '(vazio)'},
            {'campo': 'Categoria',    'depois': categoria_nome},
        ]

        AuditoriaService.registrar(
            tarefa_id=resultado['tarefa_id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Tarefa "{dados["titulo"]}" cadastrada com sucesso!',
            'tarefa_sequencia': resultado['tarefa_sequencia'],
            'tarefa_id': resultado['tarefa_id'],
        }), 201

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar nova tarefa usuario_id={usuario_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao salvar a tarefa.',
            'details': str(e)
        }), 500
    finally:
        conexao.close()