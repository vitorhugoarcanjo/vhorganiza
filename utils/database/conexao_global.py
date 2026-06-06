# utils/database/conexao_global.py
import os
import psycopg2
from flask import g
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')


def ini_conexao():
    """RETORNA CONEXÃO COM O POSTGRESQL para blueprints"""
    
    if 'db' not in g:
        url = urlparse(DATABASE_URL)
        g.db = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            port=url.port or 5432
        )
        g.db.autocommit = False
        g.cursor = g.db.cursor()
    
    return g.db, g.cursor


def get_conexao_direct():
    """RETORNA CONEXÃO PARA USO FORA DO CONTEXTO"""
    url = urlparse(DATABASE_URL)
    conexao = psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port or 5432
    )
    return conexao  # ← SEM row_factory


def close_conexao(e=None):
    """Fecha conexão no final da requisição"""
    db = g.pop('db', None)
    if db is not None:
        print("🔒 FECHANDO CONEXÃO DO BANCO!")
        db.close()


def init_conexao(app):
    """Registra a função de fechar conexão no Flask"""
    app.teardown_appcontext(close_conexao)