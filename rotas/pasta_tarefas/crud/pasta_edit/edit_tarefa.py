# rotas/pasta_tarefas/crud/pasta_edit/edit_tarefa.py
# ==========================================================
# EDITAR TAREFA - VIEW FUNCS
# ==========================================================

import logging
import json
from datetime import date, datetime
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_tarefas.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from .services import EditarTarefaService
from .validacoes import validar_dados_edicao

logger = logging.getLogger(__name__)


def _formatar_data_iso(valor):
    if not valor:
        return ''
    if isinstance(valor, (date, datetime)):
        return valor.strftime('%Y-%m-%d')
    return str(valor)[:10]


def _formatar_data_br(data_iso):
    """Converte 'YYYY-MM-DD' pra 'DD/MM/YYYY'."""
    if not data_iso:
        return ''
    s = str(data_iso)[:10]
    if len(s) == 10 and s[4] == '-':
        return f'{s[8:10]}/{s[5:7]}/{s[0:4]}'
    return s


def _montar_diff(antes, depois):
    """Compara antes/depois e retorna lista de alterações."""
    mapa_campos = {
        'titulo':         'Título',
        'descricao':      'Descrição',
        'status':         'Status',
        'prioridade':     'Prioridade',
        'data_inicio':    'Data Início',
        'data_final':     'Data Final',
        'categoria_nome': 'Categoria',   # 🆕 nome, não id
    }

    alteracoes = []
    for campo, label in mapa_campos.items():
        v_antes = antes.get(campo)
        v_depois = depois.get(campo)

        # 🆕 Formata datas
        if campo in ('data_inicio', 'data_final'):
            v_antes = _formatar_data_br(v_antes)
            v_depois = _formatar_data_br(v_depois)

        v_antes_s = str(v_antes or '').strip()
        v_depois_s = str(v_depois or '').strip()

        if v_antes_s != v_depois_s:
            alteracoes.append({
                'campo': label,
                'antes': v_antes_s or '(vazio)',
                'depois': v_depois_s or '(vazio)',
            })

    return alteracoes


# ==========================================================
# 1. GET - RENDERIZA O ESQUELETO DO MODAL
# ==========================================================
@login_required
def editar_modal(sequencia):
    user_id = session['user_id']

    conexao, cursor = ini_conexao()
    try:
        categorias = EditarTarefaService.buscar_categorias(cursor, user_id)
        return render_template(
            'pasta_tarefas/modais/modal_editar_tarefa.html.jinja',
            categorias=categorias,
            sequencia=sequencia,
        )
    finally:
        conexao.close()


# ==========================================================
# 2. GET - RETORNA OS DADOS EM JSON
# ==========================================================
@login_required
def dados_json(sequencia):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        t = EditarTarefaService.buscar_tarefa_por_sequencia(cursor, sequencia, user_id)
        if not t:
            return jsonify({'success': False, 'error': 'Tarefa não encontrada'}), 404

        return jsonify({
            'success': True,
            'data': {
                'sequencia':        t[0],
                'titulo':           t[1] or '',
                'descricao':        t[2] or '',
                'status':           t[3] or 'pendente',
                'data_inicio':      _formatar_data_iso(t[4]),
                'data_final':       _formatar_data_iso(t[5]),
                'data_finalizacao': _formatar_data_iso(t[6]),
                'categoria_id':     t[7],
                'prioridade':       t[8] or 'media',
                'motivo_conclusao': t[9] or '',
                'ativo':            t[10],
            }
        })
    finally:
        conexao.close()


# ==========================================================
# 3. POST - SALVA A EDIÇÃO (JSON) + AUDITORIA
# ==========================================================
@login_required
def salvar_edicao(sequencia):
    user_id = session['user_id']
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

        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        resultado = EditarTarefaService.atualizar_tarefa(
            cursor, sequencia, user_id, dados
        )
        if not resultado.get('success'):
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado.get('error')}), 400

        # 🔥 Auditoria com DIFF (antes/depois)
        id_interno = resultado.get('id_interno')
        alteracoes = _montar_diff(
            resultado.get('dados_antes', {}),
            resultado.get('dados_depois', {})
        )

        if alteracoes:
            AuditoriaService.registrar(
                tarefa_id=id_interno,
                acao='editada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': 'Tarefa atualizada com sucesso!'
        })

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar edição sequencia={sequencia} user_id={user_id}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()