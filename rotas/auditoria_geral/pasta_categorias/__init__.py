# rotas/auditoria_geral/pasta_categorias/__init__.py
# ==========================================================
# AUDITORIA DE CATEGORIAS - REGISTRO NO bp_auditoria
# ==========================================================

from flask import Blueprint

bp_auditoria_categorias = Blueprint('auditoria_categorias', __name__)

from .logica_auditoria import historico_categoria

bp_auditoria_categorias.add_url_rule(
    '/categoria/<int:categoria_id>',
    view_func=historico_categoria,
    methods=['GET']
)