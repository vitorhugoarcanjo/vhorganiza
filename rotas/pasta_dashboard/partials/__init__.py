# rotas/pasta_dashboard/partials/__init__.py
# ==========================================================
# SUB-BLUEPRINT - PARTIALS HTMX DO DASHBOARD
# ==========================================================

from flask import Blueprint

bp_dashboard_partials = Blueprint('dashboard_partials', __name__)

from .kpis               import partial_kpis
from .fluxo_mensal       import partial_fluxo_mensal
from .top_categorias     import partial_top_categorias
from .ultimas_transacoes import partial_ultimas_transacoes

bp_dashboard_partials.add_url_rule('/kpis',               view_func=partial_kpis,               methods=['GET'])
bp_dashboard_partials.add_url_rule('/fluxo-mensal',       view_func=partial_fluxo_mensal,       methods=['GET'])
bp_dashboard_partials.add_url_rule('/top-categorias',     view_func=partial_top_categorias,     methods=['GET'])
bp_dashboard_partials.add_url_rule('/ultimas-transacoes', view_func=partial_ultimas_transacoes, methods=['GET'])