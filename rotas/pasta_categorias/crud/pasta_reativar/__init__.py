# rotas/pasta_categorias/crud/pasta_reativar/__init__.py
# ==========================================================
# PASTA REATIVAR - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_reativar = Blueprint('reativar_categorias', __name__)

from .reativar_categoria import reativar_categoria_view

bp_reativar.add_url_rule('/<int:categoria_id>', view_func=reativar_categoria_view, methods=['POST'])