""" ARQUIVO PRINCIPAL """
import os
import hashlib
from datetime import timedelta # TEMPO DE LOGIN
from flask import Flask, render_template, url_for
from dotenv import load_dotenv # CHAVE SECRETA
from werkzeug.middleware.proxy_fix import ProxyFix # PEGAR IP DE QUEM ACESSOU

import logging
logging.basicConfig(level=logging.DEBUG)

from config.database import criar_todas_tabelas # CRIAÇÃO DE TABELAS
from config.imports_rotas import logica_imports # IMPORTS DE BLUEPRINTS

from utils.database.conexao_global import init_conexao


load_dotenv()

app = Flask(__name__)

# BANCO DE DADOS GLOBAL
init_conexao(app)


# Configura para confiar em proxies (Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

logica_imports(app) # IMPORTAÇÃO DOS BLUEPRINTS
app.secret_key = os.getenv('SECRET_KEY') # CHAVE SECRETA


# Cache global (fora da função)
STATIC_VERSION_CACHE = {}
VERSAO_EXTRA = "3"

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        if filename in STATIC_VERSION_CACHE:
            return url_for('static', filename=filename, v=STATIC_VERSION_CACHE[filename] + VERSAO_EXTRA)
        
        file_path = os.path.join(app.static_folder, filename)
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:10]
                version = file_hash
        except (OSError, IOError):
            version = str(int(os.path.getmtime(file_path))) if os.path.exists(file_path) else '1'
        
        STATIC_VERSION_CACHE[filename] = version
        return url_for('static', filename=filename, v=version + VERSAO_EXTRA)
    
    return {
        'static_v': static_v,
        'versao_sistema': '1.0.0'
    }

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=240)

@app.route('/')
def ini_app():
    return render_template('pasta_inicial_pre_login/paginainicial.html')

with app.app_context():
    criar_todas_tabelas()

if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)