# rotas/pasta_tarefas/crud/pasta_concluir/__init__.py
# ==========================================================
# PASTA CONCLUIR - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_concluir = Blueprint('concluir_tarefas', __name__)

from .concluir_tarefa import concluir

bp_concluir.add_url_rule('/<int:sequencia>', view_func=concluir, methods=['POST'])