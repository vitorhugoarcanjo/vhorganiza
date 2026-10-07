# rotas/pasta_orcamentos/crud/pasta_reativar/__init__.py
# ==========================================================
# PASTA REATIVAR - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_reativar = Blueprint('reativar_orcamentos', __name__)

from .reativar_orcamento import reativar_orcamento

# 🔥 POST (padrão HTMX) + recebe SEQUÊNCIA
bp_reativar.add_url_rule('/<int:sequencia>/reativar', view_func=reativar_orcamento, methods=['POST'])