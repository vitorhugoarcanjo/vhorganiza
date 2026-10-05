# rotas/pasta_orcamentos/crud/pasta_edit/__init__.py
# ==========================================================
# PASTA EDIT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_edit = Blueprint('edit_orcamentos', __name__)

from .editar_orcamento import salvar_estrutura

bp_edit.add_url_rule('/<int:id>/salvar-estrutura', view_func=salvar_estrutura, methods=['POST'])