# rotas\pasta_financas\__init__.py
from flask import Blueprint

# BLUEPRINT PRINCIPAL - FINANÇAS
bp_financas = Blueprint('financas', __name__)

# IMPORTS
from .financas import ini_financas, detalhes_transacao, limpar_filtros

# 🔥 IMPORTA O BLUEPRINT DE EDIÇÃO

# ========================================================== #
# ROTAS ORGANIZADAS CORRETAMENTE, FAZER ISSO NOS DEMAIS DEPOIS ...
# ========================================================== #
from .crud.pasta_insert import bp_insert
from .crud.pasta_edit import bp_edit
from .crud.pasta_quitar import bp_quitar
from .crud.pasta_estornar import bp_estornar
from .crud.pasta_reativar import bp_reativar
from .crud.pasta_delete import bp_delete
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
bp_financas.register_blueprint(bp_quitar, url_prefix='/quitar_transacao')
bp_financas.register_blueprint(bp_estornar, url_prefix='/estornar_transacao')
bp_financas.register_blueprint(bp_reativar, url_prefix='/reativar_transacao')
bp_financas.register_blueprint(bp_delete, url_prefix='/excluir_transacao')
