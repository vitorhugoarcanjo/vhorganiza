from flask import Blueprint

# BLUEPRINT PRINCIPAL - FINANÇAS
bp_financas = Blueprint('financas', __name__)

# IMPORTS
from .financas import ini_financas, detalhes_transacao, limpar_filtros
from .crud.pasta_delete.delete_transacao import ini_inativar_financas
from .crud.pasta_estornar.reativar_transacao import ini_reativar_financas

# 🔥 IMPORTA O BLUEPRINT DE EDIÇÃO

# ========================================================== #
# ROTAS ORGANIZADAS CORRETAMENTE, FAZER ISSO NOS DEMAIS DEPOIS ...
# ========================================================== #
from .crud.pasta_insert import bp_insert
from .crud.pasta_edit import bp_edit
# ========================================================== #
# ROTAS PRINCIPAIS
# ========================================================== #
bp_financas.add_url_rule('/', view_func=ini_financas, methods=['GET', 'POST'])
bp_financas.add_url_rule('/detalhes/<int:transacao_id>', view_func=detalhes_transacao)
bp_financas.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ========================================================== #
# 🔥 ROTAS DE EDIÇÃO (USANDO add_url_rule)
# ========================================================== #
bp_financas.register_blueprint(bp_insert, url_prefix='/nova_transacao')
bp_financas.register_blueprint(bp_edit, url_prefix='/edit_transacoes')


# ========================================================== #
# FUNÇÕES CRUD
# ========================================================== #
ini_inativar_financas(bp_financas)
ini_reativar_financas(bp_financas)