# rotas/pasta_tarefas/crud/pasta_reabrir/__init__.py
# ==========================================================
# PASTA REABRIR - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_reabrir = Blueprint('reabrir_tarefas', __name__)

from .reabrir_tarefa import reabrir_tarefa

bp_reabrir.add_url_rule('/<int:sequencia>', view_func=reabrir_tarefa, methods=['POST'])