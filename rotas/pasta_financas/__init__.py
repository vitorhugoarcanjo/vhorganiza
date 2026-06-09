from flask import Blueprint

# BLUEPRINT PRINCIPAL - FINANÇAS
bp_financas = Blueprint('financas', __name__)

# IMPORTS DOS CRUDS BLUEPRINTS E FUNCOES E ROTAS
from rotas.pasta_financas.financas import ini_financas, detalhes_transacao, limpar_filtros

# CRUDS
from .crud.pasta_delete.delete_transacao import ini_inativar_financas # INATIVAR FINANÇAS
from .crud.pasta_estornar.reativar_transacao import ini_reativar_financas # REATIVAR INATIVADO FINANCAS

bp_financas.add_url_rule('/', view_func=ini_financas, methods=['GET', 'POST'])
bp_financas.add_url_rule('/detalhes/<int:transacao_id>', view_func=detalhes_transacao)
bp_financas.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# REGISTRA OS CRUDS
ini_inativar_financas(bp_financas) # INATIVAR FINANCAS
ini_reativar_financas(bp_financas) # REATIVAR INATIVADO FINANCAS