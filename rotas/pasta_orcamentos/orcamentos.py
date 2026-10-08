# rotas/pasta_orcamentos/orcamentos.py
# ==========================================================
# ORÇAMENTOS - TELA PRINCIPAL (idêntico ao Finanças)
# ==========================================================

from flask import render_template, session, request, redirect, url_for
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .filters import OrcamentosFilters
from .services.services_orcamento import OrcamentosServices
from .formatters import OrcamentosFormatters


@login_required
def ini_orcamento():
    """ Página principal de orçamentos """
    user_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. PROCESSA FILTROS
    if request.method == 'POST':
        OrcamentosFilters.salvar_filtros_post(request, session)

    data_inicio, data_fim, tipo_data = OrcamentosFilters.processar_filtros_data()
    session['orcamentos_tipo_data'] = tipo_data

    mostrar_inativas = OrcamentosFilters.processar_mostrar_inativas()

    filtros = OrcamentosFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio':      data_inicio,
        'data_fim':         data_fim,
        'tipo_data':        tipo_data,
        'mostrar_inativas': mostrar_inativas,
    })

    # 2. BUSCA DADOS
    conexao, cursor = ini_conexao()
    service = OrcamentosServices(conexao, cursor)

    orcamentos_raw = service.buscar_orcamentos(user_id, filtros)
    orcamentos = OrcamentosFormatters.formatar_lista(orcamentos_raw)

    contadores = OrcamentosFormatters.calcular_contadores(orcamentos)

    # 3. HTMX
    if is_htmx:
        return _renderizar_htmx(orcamentos, contadores, data_inicio, data_fim, mostrar_inativas)

    # 4. RENDER COMPLETO
    return render_template(
        'pasta_orcamentos/tela_orcamentos.html.jinja',
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data=tipo_data,
        status=filtros['status'],
        cliente=filtros['cliente'],
        busca=filtros['busca'],
        mostrar_inativas=mostrar_inativas,
        orcamentos=orcamentos,
        contadores=contadores,
    )

def _renderizar_htmx(orcamentos, contadores, data_inicio, data_fim, mostrar_inativas):
    """ RENDERIZA APENAS A TABELA E ATUALIZA INPUTS/CONTADORES VIA HTMX (OOB) """

    tabela_html = render_template(
        'pasta_orcamentos/_tabela_orcamentos.html.jinja',
        orcamentos=orcamentos,
    )

    oob_html = f"""
        <input type="date" name="data_inicio" id="data_inicio_input_orc"
               class="form-control filter-auto" value="{data_inicio or ''}"
               hx-swap-oob="outerHTML:#data_inicio_input_orc">
        <input type="date" name="data_fim" id="data_fim_input_orc"
               class="form-control filter-auto" value="{data_fim or ''}"
               hx-swap-oob="outerHTML:#data_fim_input_orc">
        <input type="hidden" name="mostrar_inativas" id="mostrar_inativas_input"
               value="{mostrar_inativas}"
               hx-swap-oob="outerHTML:#mostrar_inativas_input">

        <span id="totalOrcamentos" hx-swap-oob="innerHTML">{contadores['total']}</span>
        <span id="totalRascunho"   hx-swap-oob="innerHTML">{contadores['rascunho']}</span>
        <span id="totalEnviado"    hx-swap-oob="innerHTML">{contadores['enviado']}</span>
        <span id="totalAprovado"   hx-swap-oob="innerHTML">{contadores['aprovado']}</span>
        <span id="totalRejeitado"  hx-swap-oob="innerHTML">{contadores['rejeitado']}</span>
    """

    return tabela_html + oob_html

# ==========================================================
# LIMPA FILTROS
# ==========================================================
@login_required
def limpar_filtros():
    OrcamentosFilters.limpar_filtros(session)
    return redirect(url_for('orcamentos.ini_orcamento'))