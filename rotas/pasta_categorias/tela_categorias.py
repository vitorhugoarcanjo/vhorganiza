# rotas/pasta_categorias/tela_categorias.py
from flask import render_template, session
from utils.database.conexao_global import ini_conexao


def ini_categorias():
    usuario_id = session['user_id']

    conexao, cursor = ini_conexao()

    # BLOCO 1 - CATEGORIA TAREFAS
    cursor.execute(
        'SELECT id, nome, cor FROM categorias_tarefas WHERE usuario_id = %s',
        (usuario_id,)
    )
    categoria_tarefas = cursor.fetchall()

    # BLOCO 2 - CATEGORIA FINANCAS
    cursor.execute(
        'SELECT id, nome, cor FROM categorias_financas WHERE usuario_id = %s',
        (usuario_id,)
    )
    categoria_financas = cursor.fetchall()

    return render_template(
        'pasta_categorias/tela_categorias.html.jinja',
        categoria_tarefas=categoria_tarefas,
        categoria_financas=categoria_financas
    )