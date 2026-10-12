# rotas/pasta_dashboard/partials/fluxo_mensal.py
# ==========================================================

import logging
from flask import render_template, session

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_dashboard.services.services_dashboard import DashboardServices

logger = logging.getLogger(__name__)


@login_required
def partial_fluxo_mensal():
    usuario_id = session['user_id']

    conexao, cursor = ini_conexao()
    try:
        service = DashboardServices(conexao, cursor)
        fluxo = service.buscar_fluxo_mensal(usuario_id, meses=6)
        return render_template(
            'pasta_dashboard/partials/_fluxo_mensal.html.jinja',
            fluxo=fluxo,
        )
    except Exception:
        logger.exception("Erro ao renderizar partial 'fluxo_mensal'")
        return '', 200
    finally:
        conexao.close()