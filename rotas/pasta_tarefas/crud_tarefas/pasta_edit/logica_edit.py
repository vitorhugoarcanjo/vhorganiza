# rotas/pasta_tarefas/crud_tarefas/pasta_edit/logica_edit.py
from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3, os

from rotas.middleware.autenticacao import login_required

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_tela_edit = Blueprint('editar_tarefa', __name__)


@bp_tela_edit.route('/editar_tarefa/<int:tarefa_seq>', methods=['GET', 'POST'])
@login_required
def iniedittarefa(tarefa_seq):
    user_id = session['user_id']

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # SELECT com título
    cursor.execute("""
        SELECT t.titulo, t.descricao, t.status, t.data_inicio, t.data_final, 
               t.categoria_id, t.prioridade, c.nome as categoria_nome, c.cor as categoria_cor
        FROM tarefas t
        LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id
        WHERE t.tarefa_sequencia = ? AND t.user_id = ?
    """, (tarefa_seq, user_id))
    tarefa = cursor.fetchone()

    cursor.execute("SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = ?", (user_id,))
    todas_categorias = cursor.fetchall()

    if request.method == 'POST':
        titulo = request.form.get('titulo', '')      # ← NOVO
        descricao = request.form.get('descricao', '')
        status = request.form.get('status', '')
        data_inicio = request.form.get('data_inicio', '')
        data_final = request.form.get('data_final', '')
        categoria_id = request.form.get('categoria_id', '')
        prioridade = request.form.get('prioridade', '')

        if categoria_id == '':
            categoria_id = None
        else:
            categoria_id = int(categoria_id)

        # UPDATE com título
        cursor.execute('''
            UPDATE tarefas 
            SET titulo = ?, descricao = ?, status = ?, data_inicio = ?, 
                data_final = ?, categoria_id = ?, prioridade = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE tarefa_sequencia = ? AND user_id = ?
        ''', (titulo, descricao, status, data_inicio, data_final, categoria_id, prioridade, tarefa_seq, user_id))
        
        conexao.commit()
        conexao.close()
        return redirect(url_for('tarefas.ini_tarefas'))
    
    if not tarefa:
        conexao.close()
        return redirect(url_for('tarefas.ini_tarefas'))

    conexao.close()
    
    return render_template(
        'pasta_tarefas/crud_tarefas/tela_edit.html',
        tarefa=tarefa,
        tarefa_seq=tarefa_seq,
        todas_categorias=todas_categorias
    )