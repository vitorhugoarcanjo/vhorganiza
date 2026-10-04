# rotas/pasta_tarefas/crud/pasta_insert/__init__.py
# ==========================================================
# PASTA INSERT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_insert = Blueprint('insert_tarefas', __name__)

from .insert_tarefa import nova_tarefa_modal, salvar_nova_tarefa

bp_insert.add_url_rule('/modal',  view_func=nova_tarefa_modal,    methods=['GET'])
bp_insert.add_url_rule('/salvar', view_func=salvar_nova_tarefa,   methods=['POST'])