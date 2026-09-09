# ==========================================================
# PASTA EDIT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

# 🔥 CRIA O BLUEPRINT
bp_edit = Blueprint('edit_transacoes', __name__)

# 🔥 IMPORTA AS FUNÇÕES
from .edit_transacao import editar_modal, dados_json, salvar_edicao

# 🔥 REGISTRA AS ROTAS (usando add_url_rule)
bp_edit.add_url_rule('/<int:sequencia>', view_func=editar_modal, methods=['GET'])
bp_edit.add_url_rule('/dados/<int:sequencia>', view_func=dados_json, methods=['GET'])
bp_edit.add_url_rule('/<int:sequencia>', view_func=salvar_edicao, methods=['POST'])