# rotas/pasta_orcamentos/crud/pasta_insert/__init__.py
# ==========================================================
# PASTA INSERT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_insert = Blueprint('insert_orcamentos', __name__)

from .cadastrar_orcamento import criar_orcamento

bp_insert.add_url_rule('/criar', view_func=criar_orcamento, methods=['POST'])