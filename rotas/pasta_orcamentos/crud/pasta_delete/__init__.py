# rotas/pasta_orcamentos/crud/pasta_delete/__init__.py
# ==========================================================
# PASTA DELETE - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_delete = Blueprint('delete_orcamentos', __name__)

from .excluir_orcamento import excluir_orcamento

# 🔥 POST (padrão HTMX) + recebe SEQUÊNCIA
bp_delete.add_url_rule('/<int:sequencia>/excluir', view_func=excluir_orcamento, methods=['POST'])