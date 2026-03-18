from flask import Blueprint, request, render_template, session, redirect, url_for
import os, sqlite3

bp_insert_tarefas = Blueprint('insert_tarefas', __name__)

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

@bp_insert_tarefas.route('/', methods=['GET', 'POST'])
def ini_insert():
    if request.method == 'POST':
        user_id = session['user_id']
        descricao = request.form.get('descricao')
        status = request.form.get('status')
        data_inicio = request.form.get('data_inicio')
        data_final = request.form.get('data_final')
        categoria_tarefa = request.form.get('categoria_id')
        prioridade_tarefa = request.form.get('prioridade')

        if categoria_tarefa == '':
            categoria_tarefa = None
        else:
            categoria_tarefa = int(categoria_tarefa) if categoria_tarefa else None

        try:
            conexao_banco = sqlite3.connect(caminho_banco)
            cursor = conexao_banco.cursor()

            # 1. pegar próxima sequência POR USUÁRIO - TAREFA SEQUENCIA
            cursor.execute(
                "SELECT IFNULL(MAX(tarefa_sequencia), 0) + 1 FROM tarefas WHERE user_id = ?",
                (user_id,)
            )
            prox_seq = cursor.fetchone()[0]

            cursor.execute('INSERT INTO tarefas (user_id, descricao, status, data_inicio, data_final, categoria_id, prioridade, tarefa_sequencia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (user_id, descricao or '', status or 'pendente', data_inicio, data_final, categoria_tarefa, prioridade_tarefa, prox_seq))

            conexao_banco.commit()
            conexao_banco.close()
            return redirect(url_for('tarefas.ini_tarefas'))
        except Exception as e:
            print(f'Erro: {e}')

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute('SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = ?', (session['user_id'],))
    categorias = cursor.fetchall()
    conexao.close()

    return render_template('pasta_tarefas/crud_tarefas/tela_insert.html.jinja', categorias=categorias)
