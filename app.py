""" ARQUIVO PRINCIPAL """
import os
import hashlib
import time
from datetime import timedelta # TEMPO DE LOGIN
from flask import Flask, render_template, url_for
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


# Adiciona isso no lugar (depois do app = Flask(__name__))
BUILD_TIMESTAMP = str(int(time.time()))  # MUDA A CADA REINICIO DO APP

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        # PEGA A DATA DE MODIFICAÇÃO DO ARQUIVO
        file_path = os.path.join(app.static_folder, filename)
        if os.path.exists(file_path):
            mtime = str(int(os.path.getmtime(file_path)))
            # USA O TIMESTAMP DO BUILD + MODIFICAÇÃO DO ARQUIVO
            version = f"{BUILD_TIMESTAMP}_{mtime}"
        else:
            version = BUILD_TIMESTAMP
        
        # GERA URL COM VERSÃO: /static/arquivo.css?v=1234567890_1234567
        return url_for('static', filename=filename, v=version)
    
    return {
        'static_v': static_v,
        'versao_sistema': BUILD_TIMESTAMP  # PRA VER NO FRONT
    }

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
