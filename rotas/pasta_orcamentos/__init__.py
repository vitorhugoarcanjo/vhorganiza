# rotas/pasta_orcamentos/__init__.py
# ==========================================================
# BLUEPRINT PRINCIPAL - ORÇAMENTOS
# ==========================================================

from flask import Blueprint

bp_orcamentos = Blueprint('orcamentos', __name__)

# ==========================================================
# ROTA PRINCIPAL
# ==========================================================
from .orcamentos import ini_orcamento, limpar_filtros

bp_orcamentos.add_url_rule('/', view_func=ini_orcamento, methods=['GET', 'POST'])
bp_orcamentos.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ==========================================================
# CRUDs (sub-blueprints)
# ==========================================================
from .crud.pasta_insert import bp_insert
from .crud.pasta_edit   import bp_edit
from .crud.pasta_delete import bp_delete
from .crud.pasta_dados  import bp_dados
from .crud.pasta_pdf    import bp_pdf

bp_orcamentos.register_blueprint(bp_insert, url_prefix='')
bp_orcamentos.register_blueprint(bp_edit,   url_prefix='')
bp_orcamentos.register_blueprint(bp_delete, url_prefix='')
bp_orcamentos.register_blueprint(bp_dados,  url_prefix='')
bp_orcamentos.register_blueprint(bp_pdf,    url_prefix='')