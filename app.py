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


load_dotenv()

app = Flask(__name__)

# Configura para confiar em proxies (Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

logica_imports(app) # IMPORTAÇÃO DOS BLUEPRINTS
app.secret_key = os.getenv('SECRET_KEY') # CHAVE SECRETA

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        file_path = os.path.join(app.static_folder, filename)

        try:
            with open(file_path, 'rb') as f:
                version = hashlib.md5(f.read()).hexdigest()[:10]
        except:
            version = '1'

        return url_for('static', filename=filename, v=version)
    
    return {
        'static_v': static_v,
        'versao_sistema': '1.0.0'
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
