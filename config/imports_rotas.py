""" ARQUIVO IMPORTS DE ROTAS """
from rotas.pasta_login.pasta_acesso_login.logica_login import bp_login # LOGIN
from rotas.pasta_login.recuperar_senha.recuperar_senha import bp_recuperar # RECUPERAR SENHA
from rotas.pasta_login.pasta_cadastre_se.tela_cadastre_se import bp_cadastre_se # CADASTRE-SE
from rotas.pasta_tela_pos_login.tela_pos_login import bp_pos_login # TELA POS LOGIN

# PASTA FINANÇAS
from rotas.pasta_financas.financas import bp_financas # LÓGICA FINANÇAS - INICIO
from rotas.pasta_financas.crud.pasta_insert.insert_transacao import bp_insert_transacao # INSERIR
from rotas.pasta_financas.crud.pasta_edit.edit_transacao import bp_edit_transacao # EDITAR
from rotas.pasta_financas.crud.pasta_delete.delete_transacao import bp_delete # DELETAR
from rotas.pasta_financas.crud.pasta_quitar.quitar_transacao import bp_quitar # QUITAR

# PASTA DASHBOARD
from rotas.pasta_dashboard.dashboard import bp_dashboard

# PASTA CONFIGURACOES
from rotas.pasta_config.config import bp_config

# PASTA TAREFAS
from rotas.pasta_tarefas.tela_tarefas import bp_tela_tarefas # LÓGICA TAREFAS - INICIO
from rotas.pasta_tarefas.crud_tarefas.pasta_insert.tela_insert import bp_insert_tarefas # INSERIR
from rotas.pasta_tarefas.crud_tarefas.pasta_edit.logica_edit import bp_tela_edit # EDITAR

# PASTA CATEGORIAS
from rotas.pasta_categorias.logica_insert_categorias import bp_categorias

# IMPORTS ROTAS
def logica_imports(app):
    """ REGISTROS DO APP.BLUE... """
    app.register_blueprint(bp_login, url_prefix="/login") # LOGIN
    app.register_blueprint(bp_recuperar, url_prefix="/recuperar")
    app.register_blueprint(bp_cadastre_se, url_prefix="/cadastre_se") # CADASTRE-SE
    app.register_blueprint(bp_pos_login, url_prefix="/pos_login") # TELA POS LOGIN

    # FINANÇAS
    app.register_blueprint(bp_financas, url_prefix="/financas")
    app.register_blueprint(bp_insert_transacao, url_prefix='/nova_transacao') # INSERIR
    app.register_blueprint(bp_edit_transacao, url_prefix="/edit_transacoes") # EDITAR
    app.register_blueprint(bp_delete, url_prefix='/deletar_transacao') # DELETAR
    app.register_blueprint(bp_quitar, url_prefix="/quitar_transacao") # QUITAR

    # DASHBOARD
    app.register_blueprint(bp_dashboard, url_prefix="/dashboard")

    # CONFIGURACOES
    app.register_blueprint(bp_config, url_prefix="/config")

    # TAREFAS
    app.register_blueprint(bp_tela_tarefas, url_prefix="/tarefas")
    app.register_blueprint(bp_insert_tarefas, url_prefix="/insert_tarefas")
    app.register_blueprint(bp_tela_edit, url_prefix="/editar_tarefa")

    app.register_blueprint(bp_categorias, url_prefix="/categorias")
