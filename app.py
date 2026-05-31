""" ARQUIVO PRINCIPAL """
import os
import hashlib
from datetime import timedelta # TEMPO DE LOGIN
from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv # CHAVE SECRETA
from werkzeug.middleware.proxy_fix import ProxyFix # PEGAR IP DE QUEM ACESSOU

import logging
logging.basicConfig(level=logging.DEBUG)

from config.database import criar_todas_tabelas # CRIAÇÃO DE TABELAS
from config.imports_rotas import logica_imports # IMPORTS DE BLUEPRINTS


load_dotenv()

app = Flask(__name__)

# Configura para confiar em proxies (Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

logica_imports(app) # IMPORTAÇÃO DOS BLUEPRINTS
app.secret_key = os.getenv('SECRET_KEY') # CHAVE SECRETA


# VERSÃO DO CSS - MUDE ISSO QUANDO ALTERAR CSS
VERSAO_CSS = "1.0.2"

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        return url_for('static', filename=filename, v=VERSAO_CSS)
    
    return {
        'static_v': static_v,
        'versao_sistema': '1.0.0'
    }

# Desabilita cache para CSS/JS (FORÇA SEMPRE BUSCAR NOVO)
@app.after_request
def add_header(response):
    if request.path.endswith(('.css', '.js')):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=240) # SESSÃO DE LOGIN 60    

@app.route('/')
def ini_app():
    """ INICIO DO MEU APP """
    return render_template('pasta_inicial_pre_login/paginainicial.html')

with app.app_context():
    criar_todas_tabelas()


# INICIALIZA O APP
if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)
