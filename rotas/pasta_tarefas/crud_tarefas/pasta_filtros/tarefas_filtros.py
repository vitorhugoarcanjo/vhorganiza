from calendar import monthrange
from flask import session, request
import os
import sqlite3

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')


# FUNÇÃO - FILTRA CATEGORIAS
def filtro_categorias(user_id):
    """ FUNÇÃO QUE FILTRA CATEGORIAS """

    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = ? ORDER BY nome
""", (user_id,))
        categorias_usuario = cursor.fetchall()


    categorias_selecionadas = request.form.getlist('categorias')    # PEGA AS CATEGORIAS SELECIONADAS (pode ser várias)

    # LÓGICA: se marcou "todas" ou não selecionou nada
    if not categorias_selecionadas:
        return [], categorias_usuario
    
    return categorias_selecionadas, categorias_usuario


# FUNÇÃO - FILTRA STATUS
def filtro_status():
    """ FUNÇÃO QUE FILTRA STATUS """
    status = request.form.get('status', '')
    tipo_filtro = request.form.get('tipo_filtro', '')
    
    # Se veio do POST (qualquer tipo), salva na sessão
    if request.method == 'POST':
        session['status_filtro'] = status
        return status
    
    # Se não, retorna o da sessão
    return session.get('status_filtro', '')



# FUNÇÃO - FILTRA PRIORIDADE
def filtro_prioridade():
    """ FUNÇÃO QUE FILTRA PRIORIDADE """
    prioridade = request.form.get('prioridade', '')
    tipo_filtro = request.form.get('tipo_filtro', '')
    
    # Se veio do POST (qualquer tipo), salva na sessão
    if request.method == 'POST':
        session['prioridade_filtro'] = prioridade
        return prioridade
    
    # Se não, retorna o da sessão
    return session.get('prioridade_filtro', '')


def filtro_descricao():
    """ FUNÇÃO QUE GERENCIA O FILTRO DE DESCRIÇÃO """
    tipo_filtro = request.form.get('tipo_filtro', '')
    descricao = request.form.get('descricao', '')
    
    # Salva se veio descrição (qualquer tipo de POST)
    if descricao:
        session['descricao_filtro'] = descricao
        return descricao
    
    return session.get('descricao_filtro', '')

