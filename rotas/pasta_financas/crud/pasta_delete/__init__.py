# rotas/pasta_financas/crud/pasta_delete/__init__.py
from flask import Blueprint

bp_delete = Blueprint('delete_transacao', __name__)

from .delete_transacao import (
    inativar_financa,
    excluir_parcelamento_completo,
)

# Inativar 1 transação
bp_delete.add_url_rule(
    '/<int:transacao_id>',
    view_func=inativar_financa,
    methods=['POST']
)

# Inativar parcelamento completo
bp_delete.add_url_rule(
    '/parcelamento/<int:pai_id>',
    view_func=excluir_parcelamento_completo,
    methods=['POST']
)