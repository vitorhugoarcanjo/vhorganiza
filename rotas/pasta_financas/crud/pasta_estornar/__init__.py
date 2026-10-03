# rotas/pasta_financas/crud/pasta_estornar/__init__.py
from flask import Blueprint

bp_estornar = Blueprint('estornar_transacao', __name__)

# Importa a view
from .estornar_transacao import estornar_transacao_view

# Registra as rotas
bp_estornar.add_url_rule('/<int:sequencia>', view_func=estornar_transacao_view, methods=['POST'])