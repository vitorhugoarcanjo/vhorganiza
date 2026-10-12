# rotas/pasta_dashboard/__init__.py
# ==========================================================
# BLUEPRINT PRINCIPAL - DASHBOARD
# ==========================================================

from flask import Blueprint

bp_dashboard = Blueprint('dashboard', __name__)

# ==========================================================
# IMPORTS DAS ROTAS PRINCIPAIS
# ==========================================================
from .dashboard import inidashboard, limpar_filtros

# ==========================================================
# IMPORTS DOS PARTIALS (sub-blueprint pros blocos HTMX)
# ==========================================================
from .partials import bp_dashboard_partials

# ==========================================================
# ROTAS PRINCIPAIS
# ==========================================================
bp_dashboard.add_url_rule('/', view_func=inidashboard,   methods=['GET', 'POST'])
bp_dashboard.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ==========================================================
# REGISTRA OS PARTIALS COM PREFIXO
# ==========================================================
bp_dashboard.register_blueprint(bp_dashboard_partials, url_prefix='/partial')