# rotas/auditoria_geral/__init__.py
# ==========================================================
# AUDITORIA GERAL - BLUEPRINT ÚNICO
# ==========================================================

from flask import Blueprint

bp_auditoria = Blueprint('auditoria', __name__)

# ==========================================================
# IMPORTS DAS VIEWS (por módulo)
# ==========================================================
from .pasta_tarefas.logica_auditoria   import historico_tarefa
from .pasta_financas.logica_auditoria  import historico_transacao

# ==========================================================
# ROTAS
# ==========================================================
bp_auditoria.add_url_rule(
    '/tarefa/<int:tarefa_seq>',
    view_func=historico_tarefa,
    endpoint='historico_tarefa'
)

bp_auditoria.add_url_rule(
    '/transacao/<int:transacao_id>',
    view_func=historico_transacao,
    endpoint='historico_transacao'
)