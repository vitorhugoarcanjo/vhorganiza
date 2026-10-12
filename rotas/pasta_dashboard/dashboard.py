# rotas/pasta_dashboard/dashboard.py
# ==========================================================
# DASHBOARD — VIEW MAGRA (padrão 2099 — igual Finanças)
# ==========================================================

from flask import render_template, session, request, redirect, url_for
from datetime import date

from rotas.middleware.autenticacao import login_required
from rotas.pasta_dashboard.filters import DashboardFilters


@login_required
def inidashboard():
    """ Página principal do dashboard """
    usuario_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. PROCESSA FILTROS (sessão, padrão Finanças)
    data_inicio, data_fim, tipo_data = DashboardFilters.processar_filtros_data()
    session['dashboard_tipo_data'] = tipo_data

    # 2. RENDERIZAÇÃO PARA HTMX (só o #tabela-container + OOB)
    if is_htmx:
        return _renderizar_htmx(data_inicio, data_fim, tipo_data)

    # 3. RENDERIZAÇÃO COMPLETA DA PÁGINA (padrão F5)
    return render_template(
        'pasta_dashboard/tela_dashboard.html.jinja',
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data=tipo_data,
    )


def _renderizar_htmx(data_inicio, data_fim, tipo_data):
    """ RENDERIZA APENAS O WRAPPER + ATUALIZA INPUTS VIA HTMX (OOB) """

    wrapper_html = render_template(
        'pasta_dashboard/partials/_tabela_wrapper.html.jinja'
    )

    # 🔥 OOB: atualiza os inputs de data que estão FORA do #tabela-container
    oob = f"""
        <input type="date" name="data_inicio" id="data_inicio_input"
               class="form-control flex-fill" value="{data_inicio or ''}"
               hx-swap-oob="outerHTML:#data_inicio_input">
        <input type="date" name="data_fim" id="data_fim_input"
               class="form-control flex-fill" value="{data_fim or ''}"
               hx-swap-oob="outerHTML:#data_fim_input">
    """

    return wrapper_html + oob


@login_required
def limpar_filtros():
    """ Limpa todos os filtros do dashboard """
    DashboardFilters.limpar_filtros(session)
    return redirect(url_for('dashboard.inidashboard'))