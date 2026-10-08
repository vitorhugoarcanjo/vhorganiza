# rotas/pasta_orcamentos/crud/pasta_pdf/__init__.py
# ==========================================================
# PASTA PDF - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

bp_pdf = Blueprint('pdf_orcamentos', __name__)

from .pdf_orcamento import gerar_pdf

# 🔥 Padrão 2099: recebe SEQUÊNCIA
bp_pdf.add_url_rule('/<int:sequencia>/pdf', view_func=gerar_pdf, methods=['GET'])