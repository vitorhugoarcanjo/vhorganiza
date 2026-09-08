from flask import Blueprint

# BLUEPRINT PRINCIPAL - FINANÇAS
bp_financas = Blueprint('financas', __name__)

# IMPORTS
from .financas import ini_financas, detalhes_transacao, limpar_filtros
from .crud.pasta_delete.delete_transacao import ini_inativar_financas
from .crud.pasta_estornar.reativar_transacao import ini_reativar_financas

# 🔥 IMPORTA O BLUEPRINT DE EDIÇÃO
from .crud.pasta_edit.edit_transacao import editar_modal, dados_json, salvar_edicao

# ========================================================== #
# ROTAS PRINCIPAIS
# ========================================================== #
bp_financas.add_url_rule('/', view_func=ini_financas, methods=['GET', 'POST'])
bp_financas.add_url_rule('/detalhes/<int:transacao_id>', view_func=detalhes_transacao)
bp_financas.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ========================================================== #
# 🔥 ROTAS DE EDIÇÃO (USANDO add_url_rule)
# ========================================================== #
bp_financas.add_url_rule('/edit_transacoes/<int:sequencia>', view_func=editar_modal, methods=['GET'])
bp_financas.add_url_rule('/edit_transacoes/dados/<int:sequencia>', view_func=dados_json, methods=['GET'])
bp_financas.add_url_rule('/edit_transacoes/<int:sequencia>', view_func=salvar_edicao, methods=['POST'])

# ========================================================== #
# FUNÇÕES CRUD
# ========================================================== #
ini_inativar_financas(bp_financas)
ini_reativar_financas(bp_financas)