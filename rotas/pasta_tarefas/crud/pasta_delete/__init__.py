# rotas/pasta_tarefas/crud/pasta_delete/__init__.py
# ==========================================================
# PASTA DELETE (INATIVAR) - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_delete = Blueprint('delete_tarefas', __name__)

from .delete_tarefa import inativar_tarefa

bp_delete.add_url_rule('/<int:sequencia>', view_func=inativar_tarefa, methods=['POST'])