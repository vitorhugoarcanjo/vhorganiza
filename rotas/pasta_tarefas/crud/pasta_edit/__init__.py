# rotas/pasta_tarefas/crud/pasta_edit/__init__.py
# ==========================================================
# PASTA EDIT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_edit = Blueprint('edit_tarefas', __name__)

from .edit_tarefa import editar_modal, dados_json, salvar_edicao

bp_edit.add_url_rule('/<int:sequencia>',       view_func=editar_modal, methods=['GET'])
bp_edit.add_url_rule('/dados/<int:sequencia>', view_func=dados_json,   methods=['GET'])
bp_edit.add_url_rule('/<int:sequencia>',       view_func=salvar_edicao, methods=['POST'])