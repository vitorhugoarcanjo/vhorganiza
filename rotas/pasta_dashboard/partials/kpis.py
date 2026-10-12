# rotas/pasta_dashboard/partials/kpis.py
# ==========================================================

import logging
from flask import render_template, session

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_dashboard.filters import DashboardFilters
from rotas.pasta_dashboard.services.services_dashboard import DashboardServices

logger = logging.getLogger(__name__)


@login_required
def partial_kpis():
    usuario_id = session['user_id']

    # Lê filtro da sessão (padrão Finanças)
    data_inicio, data_fim, _ = DashboardFilters.processar_filtros_data()

    conexao, cursor = ini_conexao()
    try:
        service = DashboardServices(conexao, cursor)
        kpis = service.buscar_kpis(usuario_id, data_inicio, data_fim)
        return render_template(
            'pasta_dashboard/partials/_kpis.html.jinja',
            kpis=kpis,
        )
    except Exception:
        logger.exception("Erro ao renderizar partial 'kpis'")
        return '', 200
    finally:
        conexao.close()