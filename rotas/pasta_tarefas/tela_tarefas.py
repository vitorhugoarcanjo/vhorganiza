from flask import Blueprint, render_template, session, redirect, url_for, flash
import os, sqlite3
from rotas.middleware.autenticacao import login_required

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_tela_tarefas = Blueprint('tarefas', __name__)

@bp_tela_tarefas.route('/', methods=['GET', 'POST'])
@login_required
def initarefas():
    with sqlite3.connect(caminho_banco) as conexao_banco:
        cursor = conexao_banco.cursor()

        cursor.execute('SELECT id, descricao, status, data_inicio, data_final FROM tarefas WHERE user_id = ?', (session['user_id'],))
        tarefas = cursor.fetchall()
    return render_template('pasta_tarefas/tela_tarefas.html', user_nome=session.get('user_nome'), tarefas=tarefas)



# FUNÇÃO DE CONCLUIR TAREFA
@bp_tela_tarefas.route('/concluir/<int:tarefa_id>', methods=['POST'])
@login_required
def concluir_tarefa(tarefa_id):
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        
        cursor.execute('UPDATE tarefas SET status = ? WHERE id = ? AND user_id = ?', ('concluido', tarefa_id, session['user_id']))
        conexao.commit()

        flash('Tarefa concluída com sucesso!', 'success')
        return redirect(url_for('tarefas.initarefas'))




# FUNÇÃO PARA EXCLUIR TAREFA
@bp_tela_tarefas.route('/excluir/<int:tarefa_id>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM tarefas WHERE id = ? AND user_id = ?', (tarefa_id, session['user_id'] ))

        conexao.commit()

        flash('Tarefa excluída com sucesso!', 'success')
        return redirect(url_for('tarefas.initarefas'))
