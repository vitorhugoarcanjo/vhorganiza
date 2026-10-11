# rotas/pasta_categorias/categorias.py
# ==========================================================
# ROTAS PRINCIPAIS DO MÓDULO DE CATEGORIAS
# ==========================================================

import logging
from flask import render_template, session, request, redirect, url_for

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .queries import CategoriasQueries
from .filters import CategoriasFilters
from .formatters import CategoriasFormatters

logger = logging.getLogger(__name__)


# ==========================================================
# LISTAGEM PRINCIPAL
# ==========================================================
@login_required
def ini_categorias():
    """Página principal de Categorias (2 boxes: Tarefas | Finanças)"""
    usuario_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. FILTROS
    descricao_filtro  = CategoriasFilters.filtro_descricao()
    mostrar_inativas  = CategoriasFilters.processar_mostrar_inativas()

    filtros = {
        'descricao':         descricao_filtro,
        'mostrar_inativas':  mostrar_inativas,
    }

    conexao, cursor = ini_conexao()

    # 2. BUSCA TAREFAS
    filtros_tarefas = dict(filtros, modulo='tarefas')
    query = CategoriasQueries.get_categorias_base()
    params = [usuario_id]
    query, params = CategoriasFilters.aplicar_filtros_query(query, params, filtros_tarefas)
    query += " ORDER BY c.sequencia_categorias ASC"

    cursor.execute(query, params)
    categorias_tarefas_raw = cursor.fetchall()
    categorias_tarefas = CategoriasFormatters.formatar_categorias(categorias_tarefas_raw)

    # 3. BUSCA FINANÇAS
    filtros_financas = dict(filtros, modulo='financas')
    query = CategoriasQueries.get_categorias_base()
    params = [usuario_id]
    query, params = CategoriasFilters.aplicar_filtros_query(query, params, filtros_financas)
    query += " ORDER BY c.sequencia_categorias ASC"

    cursor.execute(query, params)
    categorias_financas_raw = cursor.fetchall()
    categorias_financas = CategoriasFormatters.formatar_categorias(categorias_financas_raw)

    # 4. CONTADORES (pro footer)
    contadores = {
        'tarefas':  sum(1 for c in categorias_tarefas if c['ativo'] == 1),
        'financas': sum(1 for c in categorias_financas if c['ativo'] == 1),
    }

    # 5. HTMX (retorna só os tbody + OOB)
    if is_htmx:
        return _renderizar_htmx(categorias_tarefas, categorias_financas, mostrar_inativas)

    # 6. RENDER COMPLETO
    return render_template(
        'pasta_categorias/tela_categorias.html.jinja',
        categorias_tarefas=categorias_tarefas,
        categorias_financas=categorias_financas,
        contadores=contadores,
        descricao_filtro=descricao_filtro,
        mostrar_inativas=mostrar_inativas,
    )


def _renderizar_htmx(categorias_tarefas, categorias_financas, mostrar_inativas):
    """Retorna o partial da tabela (com os 2 boxes) + OOB do hidden"""
    tabela = render_template(
        'pasta_categorias/_tabela_categorias.html.jinja',
        categorias_tarefas=categorias_tarefas,
        categorias_financas=categorias_financas,
        mostrar_inativas=mostrar_inativas,
    )

    oob_html = f"""
        <input type="hidden" name="mostrar_inativas"
               value="{mostrar_inativas}"
               id="mostrar_inativas_input"
               hx-swap-oob="outerHTML:#mostrar_inativas_input">
    """

    return tabela + oob_html


# ==========================================================
# LIMPAR FILTROS
# ==========================================================
@login_required
def limpar_filtros():
    CategoriasFilters.limpar_filtros()
    return redirect(url_for('categorias.ini_categorias'))