import sqlite3
import os
from flask import g

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

def ini_conexao():
    """ RETORNA CONEXÃO COM O BANCO """
    
    if 'db' not in g:
        g.db = sqlite3.connect(caminho_banco)
        g.db.row_factory = sqlite3.Row
    
    return g.db  # ← ATENÇÃO: identação correta (fora do if)

def get_conexao_direct():
    """ RETORNA CONEXÃO PARA USO FORA DO CONTEXTO(migracoes, scripts)"""
    conexao = sqlite3.connect(caminho_banco)
    conexao.row_factory = sqlite3.Row
    return conexao

def close_conexao(e=None):
    """ Fecha conexão no final da requisição """

    db = g.pop('db', None)
    if db is not None:
        print("🔒 FECHANDO CONEXÃO DO BANCO!")  # ← VAI APARECER NO TERMINAL
        db.close()

def init_conexao(app):
    """ Registra a função de fechar conexão no Flask """
    app.teardown_appcontext(close_conexao)
