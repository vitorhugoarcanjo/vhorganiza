# rotas/pasta_orcamentos/crud/pasta_dados/__init__.py
# ==========================================================
# PASTA DADOS - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_dados = Blueprint('dados_orcamentos', __name__)

from .dados import get_dados_orcamento

bp_dados.add_url_rule('/<int:id>/dados', view_func=get_dados_orcamento, methods=['GET'])