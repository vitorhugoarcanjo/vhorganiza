# ==========================================================
# PASTA INSERT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

# 🔥 CRIA O BLUEPRINT
bp_insert = Blueprint('insert_transacoes', __name__)

# 🔥 IMPORTA AS FUNÇÕES
from .insert_transacao import nova_transacao_modal, salvar_nova_transacao

# 🔥 REGISTRA AS ROTAS (usando add_url_rule)
bp_insert.add_url_rule('/modal', view_func=nova_transacao_modal, methods=['GET'])
bp_insert.add_url_rule('/salvar', view_func=salvar_nova_transacao, methods=['POST'])