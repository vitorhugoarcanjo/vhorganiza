# rotas/pasta_tarefas/__init__.py
# ==========================================================
# BLUEPRINT PRINCIPAL - TAREFAS
# ==========================================================

from flask import Blueprint

bp_tarefas = Blueprint('tarefas', __name__)

# ==========================================================
# IMPORTS DAS ROTAS PRINCIPAIS
# ==========================================================
from .tarefas import ini_tarefas, detalhes_tarefa, limpar_filtros

# ==========================================================
# IMPORTS DOS CRUDs (blueprints filhos)
# ==========================================================
from .crud.pasta_insert  import bp_insert
from .crud.pasta_edit    import bp_edit
from .crud.pasta_delete  import bp_delete
from .crud.pasta_concluir import bp_concluir
from .crud.pasta_reabrir  import bp_reabrir
from .crud.pasta_reativar import bp_reativar

# ==========================================================
# ROTAS PRINCIPAIS
# ==========================================================
bp_tarefas.add_url_rule('/', view_func=ini_tarefas, methods=['GET', 'POST'])
bp_tarefas.add_url_rule('/detalhes/<int:tarefa_seq>', view_func=detalhes_tarefa)
bp_tarefas.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# ==========================================================
# ROTAS DE CRUD (usando register_blueprint com prefixo)
# ==========================================================
bp_tarefas.register_blueprint(bp_insert,   url_prefix='/nova_tarefa')
bp_tarefas.register_blueprint(bp_edit,     url_prefix='/edit_tarefas')
bp_tarefas.register_blueprint(bp_delete,   url_prefix='/excluir_tarefa')
bp_tarefas.register_blueprint(bp_concluir, url_prefix='/concluir_tarefa')
bp_tarefas.register_blueprint(bp_reabrir,  url_prefix='/reabrir_tarefa')
bp_tarefas.register_blueprint(bp_reativar, url_prefix='/reativar_tarefa')