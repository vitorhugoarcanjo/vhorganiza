# rotas/pasta_financas/crud/pasta_quitar/__init__.py
from flask import Blueprint

bp_quitar = Blueprint('quitar_transacao', __name__)

from .quitar_transacao import quitar_modal_view, quitar_transacao_view

# 🔥 GET — Renderiza o modal
bp_quitar.add_url_rule(
    '/modal/<int:sequencia>',
    view_func=quitar_modal_view,
    methods=['GET']
)

# 🔥 POST — Quita a transação
bp_quitar.add_url_rule(
    '/<int:sequencia>',
    view_func=quitar_transacao_view,
    methods=['POST']
)