# rotas/pasta_categorias/crud/pasta_listar_modal/__init__.py
# ==========================================================
# PASTA LISTAR MODAL - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_listar_modal = Blueprint('listar_modal_categorias', __name__)

from .listar_modal import abrir_modal_lista

bp_listar_modal.add_url_rule('/modal-lista', view_func=abrir_modal_lista, methods=['GET'])