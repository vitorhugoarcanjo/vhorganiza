""" ARQUIVO PRINCIPAL """
import os
from datetime import timedelta # TEMPO DE LOGIN
from flask import Flask, render_template, request
from dotenv import load_dotenv # CHAVE SECRETA

import logging
logging.basicConfig(level=logging.DEBUG)

from config.database import criar_todas_tabelas # CRIAÇÃO DE TABELAS
from config.imports_rotas import logica_imports # IMPORTS DE BLUEPRINTS


load_dotenv()

app = Flask(__name__)
logica_imports(app) # IMPORTAÇÃO DOS BLUEPRINTS

app.secret_key = os.getenv('SECRET_KEY')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.before_request
def debug_request():
    app.logger.debug(f"=== REQUISIÇÃO RECEBIDA ===")
    app.logger.debug(f"URL: {request.url}")
    app.logger.debug(f"Host: {request.host}")
    app.logger.debug(f"Path: {request.path}")
    app.logger.debug(f"Endpoint: {request.endpoint}")

@app.after_request
def debug_response(response):
    app.logger.debug(f"=== RESPOSTA ENVIADA ===")
    app.logger.debug(f"Status: {response.status_code}")
    app.logger.debug(f"Location: {response.headers.get('Location', 'Nenhum')}")
    return response

@app.route('/')
def ini_app():
    """ INICIO DO MEU APP """
    return render_template('pasta_tela_inicial/paginainicial.html')

# INICIALIZA O APP
if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(debug=True)
