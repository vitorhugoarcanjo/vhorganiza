# rotas/pasta_tarefas/tarefas.py
# ==========================================================
# ROTAS PRINCIPAIS DO MÓDULO DE TAREFAS
# ==========================================================

import logging
from datetime import date
from flask import render_template, session, request, redirect, url_for, jsonify

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .queries import TarefasQueries
from .filters import TarefasFilters
from .formatters import TarefasFormatters

logger = logging.getLogger(__name__)


# ==========================================================
# LISTAGEM PRINCIPAL
# ==========================================================
@login_required
def ini_tarefas():
    """Página principal de Tarefas"""
    usuario_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. SALVAR FILTROS (só no POST da view principal)
    if request.method == 'POST':
        TarefasFilters.salvar_filtros_post(request, session)

    # 2. PROCESSAR DATA + RECUPERAR FILTROS
    data_inicio, data_fim, tipo_data = TarefasFilters.processar_filtros_data()
    session['tarefas_tipo_data'] = tipo_data

    conexao, cursor = ini_conexao()

    filtros = TarefasFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim':    data_fim,
        'tipo_data':   tipo_data,
    })

    # Categorias pro filtro (só se não for HTMX)
    categorias_filtro, categorias_usuario = TarefasFilters.filtro_categorias(usuario_id, cursor)

    # 3. QUERY
    query = TarefasQueries.get_tarefas_base()
    params = [usuario_id]
    query, params = TarefasFilters.aplicar_filtros_query(query, params, filtros)
    query += " ORDER BY t.tarefa_sequencia ASC"

    cursor.execute(query, params)
    tarefas_raw = cursor.fetchall()
    tarefas = TarefasFormatters.formatar_tarefas(tarefas_raw)

    # 4. CONTADORES
    pendentes  = sum(1 for t in tarefas if t['status'] == 'pendente'     and t['ativo'] == 1)
    andamento  = sum(1 for t in tarefas if t['status'] == 'em andamento' and t['ativo'] == 1)
    concluidas = sum(1 for t in tarefas if t['status'] == 'concluido'    and t['ativo'] == 1)

    contadores = {
        'pendentes':  pendentes,
        'andamento':  andamento,
        'concluidas': concluidas,
    }

    # 5. HTMX (retorna só a tabela + OOB)
    if is_htmx:
        return _renderizar_htmx(tarefas, contadores, filtros, data_inicio, data_fim)

    # 6. RENDER COMPLETO
    return render_template(
        'pasta_tarefas/tela_tarefas.html.jinja',
        user_nome=session.get('user_nome'),
        tarefas=tarefas,
        contadores=contadores,
        data_hoje=date.today(),
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data=tipo_data,
        mostrar_inativas=filtros['mostrar_inativas'],
        categorias_usuario=categorias_usuario,
        categorias_filtro=categorias_filtro,
        status_filtro=filtros['status'],
        prioridade_filtro=filtros['prioridade'],
        descricao_filtro=filtros['descricao'],
    )


def _renderizar_htmx(tarefas, contadores, filtros, data_inicio, data_fim):
    """Retorna só a tabela + OOB (inputs + contadores)"""
    tabela_html = render_template(
        'pasta_tarefas/_tabela_tarefas.html.jinja',
        tarefas=tarefas,
        mostrar_inativas=filtros['mostrar_inativas'],
    )

    oob_html = f"""
        <input type="date" name="data_inicio" id="data_inicio_input"
               class="form-control" value="{data_inicio or ''}"
               hx-swap-oob="outerHTML:#data_inicio_input">
        <input type="date" name="data_fim" id="data_fim_input"
               class="form-control" value="{data_fim or ''}"
               hx-swap-oob="outerHTML:#data_fim_input">
        <input type="hidden" name="mostrar_inativas"
               value="{filtros['mostrar_inativas']}" id="mostrar_inativas_input"
               hx-swap-oob="outerHTML:#mostrar_inativas_input">
        <span id="totalPendentes"  hx-swap-oob="innerHTML">{contadores['pendentes']}</span>
        <span id="totalAndamento"  hx-swap-oob="innerHTML">{contadores['andamento']}</span>
        <span id="totalConcluidas" hx-swap-oob="innerHTML">{contadores['concluidas']}</span>
    """

    return tabela_html + oob_html


# ==========================================================
# DETALHES (JSON)
# ==========================================================
@login_required
def detalhes_tarefa(tarefa_seq):
    conexao, cursor = ini_conexao()
    cursor.execute(TarefasQueries.get_detalhes_tarefa(),
                   (tarefa_seq, session['user_id']))
    tarefa = cursor.fetchone()

    if not tarefa:
        return jsonify({'error': 'Tarefa não encontrada'}), 404

    return jsonify(TarefasFormatters.formatar_detalhes(tarefa))


# ==========================================================
# LIMPAR FILTROS
# ==========================================================
@login_required
def limpar_filtros():
    TarefasFilters.limpar_filtros(session)
    return redirect(url_for('tarefas.ini_tarefas'))