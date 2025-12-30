from flask import Flask, render_template
import os
from dotenv import load_dotenv # CHAVE SECRETA
from datetime import timedelta # TEMPO DE LOGIN
from utils.versao_nova_cache import get_static_version # limpar cache por hora


# CRIAÇÃO DE TABELAS
from config.database import criar_todas_tabelas


# CADASTRE-SE
from rotas.pasta_login.pasta_cadastre_se.tela_cadastre_se import bp_cadastre_se

# LOGIN
from rotas.pasta_login.pasta_acesso_login.logica_login import bp_login

# TELA POS LOGIN
from rotas.pasta_tela_pos_login.tela_pos_login import bp_pos_login

# PASTA FINANÇAS
from rotas.pasta_financas.financas import bp_financas
from rotas.pasta_financas.crud.pasta_insert.insert_transacao import bp_insert_transacao
from rotas.pasta_financas.crud.pasta_edit.edit_transacao import bp_edit_transacao
from rotas.pasta_financas.crud.pasta_delete.delete_transacao import bp_delete
from rotas.pasta_financas.crud.pasta_quitar.quitar_transacao import bp_quitar

# PASTA DASHBOARD
from rotas.pasta_dashboard.dashboard import bp_dashboard

# PASTA CONFIGURACOES
from rotas.pasta_config.config import bp_config

# PASTA TAREFAS
from rotas.pasta_tarefas.tela_tarefas import bp_tela_tarefas
from rotas.pasta_tarefas.crud.pasta_insert.tela_insert import bp_insert_tarefas # INSERIR
from rotas.pasta_tarefas.crud.pasta_edit.logica_edit import bp_tela_edit

load_dotenv()

app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


# ----------------- ADICIONAR BLUEPRINTS ----------------------- #
# CADASTRE_SE
app.register_blueprint(bp_cadastre_se, url_prefix="/cadastre_se")

# LOGIN
app.register_blueprint(bp_login, url_prefix="/login")

# POS LOGIN
app.register_blueprint(bp_pos_login, url_prefix="/pos_login")

# FINANÇAS
app.register_blueprint(bp_financas, url_prefix="/financas")
app.register_blueprint(bp_insert_transacao, url_prefix='/nova_transacao')
app.register_blueprint(bp_edit_transacao, url_prefix="/edit_transacoes")
app.register_blueprint(bp_delete, url_prefix='/deletar_transacao')
app.register_blueprint(bp_quitar, url_prefix="/quitar_transacao")

# DASHBOARD
app.register_blueprint(bp_dashboard, url_prefix="/dashboard")

# CONFIGURACOES
app.register_blueprint(bp_config, url_prefix="/config")

# TAREFAS
app.register_blueprint(bp_tela_tarefas, url_prefix="/tarefas")
app.register_blueprint(bp_insert_tarefas, url_prefix="/insert_tarefas")
app.register_blueprint(bp_tela_edit, url_prefix="/editar_tarefa")

@app.route('/')
def appinicializar():
    return render_template('pasta_tela_inicial/paginainicial.html')


@app.context_processor
def inject_version():
    return {
        'css_version': get_static_version(),  # ← Chama a função
        'app_version': '1.0.0'
    }


# INICIALIZA O APP
if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)