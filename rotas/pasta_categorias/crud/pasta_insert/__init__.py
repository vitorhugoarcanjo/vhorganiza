# rotas/pasta_categorias/crud/pasta_insert/__init__.py
# ==========================================================
# PASTA INSERT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_insert = Blueprint('insert_categorias', __name__)

from .insert_categoria import nova_categoria_modal, salvar_nova_categoria

bp_insert.add_url_rule('/modal',  view_func=nova_categoria_modal,    methods=['GET'])
bp_insert.add_url_rule('/salvar', view_func=salvar_nova_categoria,   methods=['POST'])