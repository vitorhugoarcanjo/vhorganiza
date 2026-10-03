# rotas/pasta_financas/crud/pasta_reativar/__init__.py
from flask import Blueprint

bp_reativar = Blueprint('reativar_transacao', __name__)

from .reativar_transacao import (
    verificar_reativacao_view,
    reativar_view,
    reativar_parcelamento_view,
)

# GET — verifica o tipo (JSON, mantém o fluxo atual)
bp_reativar.add_url_rule(
    '/verificar/<int:transacao_seq>',
    view_func=verificar_reativacao_view,
    methods=['GET']
)

# POST — reativa 1 transação (simples ou parcela) → devolve HTML da linha
bp_reativar.add_url_rule(
    '/<int:transacao_seq>',
    view_func=reativar_view,
    methods=['POST']
)

# POST — reativa parcelamento completo (pai + filhas) → devolve HTML de todas as linhas
bp_reativar.add_url_rule(
    '/parcelamento/<int:transacao_pai_id>',
    view_func=reativar_parcelamento_view,
    methods=['POST']
)