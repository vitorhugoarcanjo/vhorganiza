""" ARQUIVO PRINCIPAL """
import os
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


# BLOCO - VERSIONAMENTO E VARIAVEIS GLOBAIS
@app.context_processor
def inject_global_contexts():
    def date_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                # Conecta com a pasta static do projeto
                file_path = os.path.join(app.root_path, endpoint, filename)

                try:
                    # Adiciona a data da última modificação do arquivo (?v=timestamp)
                    values['v'] = int(os.stat(file_path).st_mtime)

                except OSError:
                    pass
        return url_for(endpoint, **values)
    
    return {
        'url_for': date_url_for,
        'versao_sistema': '1.0.0'
    }

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60) # SESSÃO DE LOGIN 60
    

@app.route('/')
def ini_app():
    """ INICIO DO MEU APP """
    return render_template('pasta_tela_inicial/paginainicial.html')

# INICIALIZA O APP
if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)
