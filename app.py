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


# VERSÃO DO SISTEMA (muda manualmente quando você lança uma versão nova)
VERSAO_SISTEMA = "2.0.0"  # ← VOCÊ CONTROLA ISSO MANUALMENTE

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        file_path = os.path.join(app.static_folder, filename)
        if os.path.exists(file_path):
            # Calcula MD5 do arquivo (muda quando o arquivo muda)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:10]
            # USA O HASH COMO PARTE DO NOME, NÃO QUERY STRING!
            return url_for('static', filename=f"{filename}?v={file_hash}")
        return url_for('static', filename=filename)
    
    return {
        'static_v': static_v,
        'versao_sistema': VERSAO_SISTEMA  # ← VERSÃO DO SISTEMA AQUI
    }

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
