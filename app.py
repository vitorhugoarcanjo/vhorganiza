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


# Cache global (fora da função)
STATIC_VERSION_CACHE = {}

@app.context_processor
def inject_global_contexts():
    def static_v(filename):
        # 1. Verifica se já tem no cache
        if filename in STATIC_VERSION_CACHE:
            return url_for('static', filename=filename, v=STATIC_VERSION_CACHE[filename])
        
        file_path = os.path.join(app.static_folder, filename)
        
        # 2. Calcula hash do arquivo (garantido 100%)
        try:
            with open(file_path, 'rb') as f:
                # Lê arquivo inteiro e gera MD5
                file_hash = hashlib.md5(f.read()).hexdigest()[:10]  # 10 caracteres
                version = file_hash
        except (OSError, IOError):
            # Fallback: timestamp se arquivo não existir
            version = str(int(os.path.getmtime(file_path))) if os.path.exists(file_path) else '1'
        
        # 3. Salva no cache
        STATIC_VERSION_CACHE[filename] = version
        
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
