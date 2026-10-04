# rotas/pasta_tarefas/crud/pasta_reativar/__init__.py
# ==========================================================
# PASTA REATIVAR - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_reativar = Blueprint('reativar_tarefas', __name__)

from .reativar_tarefa import reativar_tarefa

bp_reativar.add_url_rule('/<int:sequencia>', view_func=reativar_tarefa, methods=['POST'])