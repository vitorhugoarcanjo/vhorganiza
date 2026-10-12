# rotas/pasta_tela_pos_login/partials/__init__.py
# ==========================================================
# SUB-BLUEPRINT - PARTIALS HTMX DA TELA PÓS-LOGIN
# ==========================================================

from flask import Blueprint

bp_pos_login_partials = Blueprint('pos_login_partials', __name__)

from .vencendo import partial_vencendo
from .proximos import partial_proximos
from .resumo   import partial_resumo

bp_pos_login_partials.add_url_rule('/vencendo', view_func=partial_vencendo, methods=['GET'])
bp_pos_login_partials.add_url_rule('/proximos', view_func=partial_proximos, methods=['GET'])
bp_pos_login_partials.add_url_rule('/resumo',   view_func=partial_resumo,   methods=['GET'])