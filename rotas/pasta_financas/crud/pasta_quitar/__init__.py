# rotas/pasta_financas/crud/pasta_quitar/__init__.py
from flask import Blueprint

bp_quitar = Blueprint('quitar_transacao', __name__)

# Importa a view
from .quitar_transacao import quitar_transacao_view

# Registra as rotas
bp_quitar.add_url_rule('/<int:sequencia>', view_func=quitar_transacao_view, methods=['POST'])