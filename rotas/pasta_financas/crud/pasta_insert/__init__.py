# ==========================================================
# PASTA INSERT - REGISTRO DE ROTAS
# ==========================================================

from flask import Blueprint

# 1. Cria o Blueprint local
bp_insert = Blueprint('insert_transacoes', __name__)

# 2. Importa as funções (após a declaração do Blueprint)
from .insert_transacao import nova_transacao_modal, salvar_nova_transacao

# 3. Registra as regras de URL
bp_insert.add_url_rule('/modal', view_func=nova_transacao_modal, methods=['GET'])
bp_insert.add_url_rule('/salvar', view_func=salvar_nova_transacao, methods=['POST'])