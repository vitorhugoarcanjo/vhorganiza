# rotas/pasta_categorias/crud/pasta_edit/__init__.py
# ==========================================================
# PASTA EDIT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_edit = Blueprint('edit_categorias', __name__)

from .edit_categoria import editar_categoria_modal, salvar_edicao_categoria

bp_edit.add_url_rule('/modal/<int:categoria_id>',  view_func=editar_categoria_modal,    methods=['GET'])
bp_edit.add_url_rule('/salvar/<int:categoria_id>', view_func=salvar_edicao_categoria,   methods=['POST'])