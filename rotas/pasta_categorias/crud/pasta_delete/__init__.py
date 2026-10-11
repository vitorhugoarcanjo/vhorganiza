# rotas/pasta_categorias/crud/pasta_delete/__init__.py
# ==========================================================
# PASTA DELETE - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_delete = Blueprint('delete_categorias', __name__)

from .delete_categoria import inativar_categoria_view

bp_delete.add_url_rule('/<int:categoria_id>', view_func=inativar_categoria_view, methods=['POST'])