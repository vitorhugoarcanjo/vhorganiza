# rotas/pasta_categorias/__init__.py
# ==========================================================
# BLUEPRINT PRINCIPAL - CATEGORIAS
# ==========================================================

from flask import Blueprint

bp_categorias = Blueprint('categorias', __name__)

# ==========================================================
# IMPORTS DAS ROTAS PRINCIPAIS
# ==========================================================
from .categorias import ini_categorias, limpar_filtros

# ==========================================================
# IMPORTS DOS CRUDs (blueprints filhos)
# ==========================================================
from .crud.pasta_insert  import bp_insert
from .crud.pasta_edit    import bp_edit
from .crud.pasta_delete  import bp_delete
from .crud.pasta_reativar import bp_reativar
from .crud.pasta_listar_modal   import bp_listar_modal

# ==========================================================
# ROTAS PRINCIPAIS
# ==========================================================
bp_categorias.add_url_rule('/', view_func=ini_categorias, methods=['GET', 'POST'])
bp_categorias.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ==========================================================
# ROTAS DE CRUD (usando register_blueprint com prefixo)
# ==========================================================
bp_categorias.register_blueprint(bp_insert,    url_prefix='/nova_categoria')
bp_categorias.register_blueprint(bp_edit,      url_prefix='/edit_categorias')
bp_categorias.register_blueprint(bp_delete,    url_prefix='/excluir_categoria')
bp_categorias.register_blueprint(bp_reativar,  url_prefix='/reativar_categoria')
bp_categorias.register_blueprint(bp_listar_modal,  url_prefix='')