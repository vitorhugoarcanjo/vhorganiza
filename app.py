""" ARQUIVO PRINCIPAL """
import os
import hashlib
import time  # ← Já tem que ter esse import
from datetime import timedelta
from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

import logging
logging.basicConfig(level=logging.DEBUG)

from config.database import criar_todas_tabelas
from config.imports_rotas import logica_imports

load_dotenv()

app = Flask(__name__)

# Configura para confiar em proxies (Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

logica_imports(app)
app.secret_key = os.getenv('SECRET_KEY')

# ==================================================
# SOLUÇÃO DEFINITIVA - TIMESTAMP DINÂMICO
# ==================================================
@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        # Gera timestamp atual (muda a cada requisição)
        timestamp = str(int(time.time()))
        return url_for('static', filename=filename, v=timestamp)
    
    return {
        'static_v': static_v,
        'versao_sistema': '1.0.0'
    }

# Mantém os headers anti-cache
@app.after_request
def add_header(response):
    if request.path.endswith(('.css', '.js')):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=240)

@app.route('/')
def ini_app():
    return render_template('pasta_inicial_pre_login/paginainicial.html')

with app.app_context():
    criar_todas_tabelas()

if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)