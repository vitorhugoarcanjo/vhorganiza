"""
GERENCIADOR DE CONEXÕES SQLITE
===============================
Funções:
- ini_conexao()        -> Usar em blueprints/rotas Flask
- get_conexao_direct() -> Usar em scripts/migrações/workers
- close_conexao()      -> Chamado automaticamente pelo Flask
- init_conexao(app)    -> Registrar no app factory

ONDE CADA FUNÇÃO É USADA:
- ini_conexao: todos os blueprints, LogService
- get_conexao_direct: scripts/migrate.py, workers/cleanup.py
"""

import sqlite3
import os
from flask import g

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

def ini_conexao(timeout=5):
    """ RETORNA CONEXÃO COM O BANCO """
    
    if 'db' not in g:
        g.db = sqlite3.connect(caminho_banco, timeout=timeout)
        g.db.row_factory = sqlite3.Row
    
    return g.db

def get_conexao_direct(timeout=5):
    """ RETORNA CONEXÃO PARA USO FORA DO CONTEXTO(migracoes, scripts)"""
    conexao = sqlite3.connect(caminho_banco, timeout=timeout)
    conexao.row_factory = sqlite3.Row
    return conexao

def close_conexao(e=None):
    """ Fecha conexão no final da requisição """

    db = g.pop('db', None)
    if db is not None:
        print("🔒 FECHANDO CONEXÃO DO BANCO!")
        db.close()

def init_conexao(app):
    """ Registra a função de fechar conexão no Flask """
    app.teardown_appcontext(close_conexao)