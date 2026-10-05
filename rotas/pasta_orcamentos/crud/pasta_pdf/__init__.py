# rotas/pasta_orcamentos/crud/pasta_pdf/__init__.py
# ==========================================================
# PASTA PDF - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_pdf = Blueprint('pdf_orcamentos', __name__)

from .pdf_orcamento import gerar_pdf

bp_pdf.add_url_rule('/<int:id>/pdf', view_func=gerar_pdf, methods=['GET'])