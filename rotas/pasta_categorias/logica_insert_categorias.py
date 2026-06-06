import os
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from rotas.middleware.autenticacao import login_required
from .tela_categorias import ini_categorias

from .crud.categorias_tarefas.cat_tarefas import insert_cat_tarefa
from .crud.categorias_financas.cat_financas import insert_cat_fin

from utils.database.conexao_global import ini_conexao

bp_categorias = Blueprint('categorias', __name__)


@bp_categorias.route('/', methods=['GET'])
@login_required
def listar_categorias():
    return ini_categorias()

@bp_categorias.route('/novo', methods=['GET','POST'])
@login_required
def insert_categorias_global():
    msg = ''

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cor = request.form.get('cor', '').strip()
        modulo = request.form.get('modulo', '').strip()

        if not all([nome, cor]):
            msg = "Descreva todos os campos corretamente!"
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)
        
        conexao, cursor = ini_conexao()
        
        user_id = session['user_id']

        if modulo == 'tarefas':
            ok, msg = insert_cat_tarefa(nome, cor, user_id, cursor)

        elif modulo == 'financas':
            ok, msg = insert_cat_fin(nome, cor, user_id, cursor)

        else:
            msg = "Módulo inválido"
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)

        if ok:
            conexao.commit()
            return redirect(url_for('categorias.listar_categorias'))

        else:
            conexao.rollback()
            msg = msg or "Erro ao criar categoria"
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)  # ← LINHA 3: MOSTRA MSG!
    
    return render_template('pasta_categorias/crud/insert_categorias.html')


@bp_categorias.route('/excluir/<modulo>/<int:id>')
@login_required
def excluir_categoria(modulo, id):
    user_id = session['user_id']

    conexao, cursor = ini_conexao()
    

    if modulo == 'tarefas':
        cursor.execute("""
            DELETE FROM categorias_tarefas
            WHERE id = %s AND user_id = %s
        """, (id, user_id))

    elif modulo == 'financas':
        cursor.execute("""
            DELETE FROM categorias_financas
            WHERE id = %s AND user_id = %s
        """, (id, user_id))

    else:
        flash("Módulo inválido", "error")
        return redirect(url_for('categorias.listar_categorias'))

    conexao.commit()
    
    flash('Categoria excluída com sucesso!', 'success')
    return redirect(url_for('categorias.listar_categorias'))



@bp_categorias.route('/editar/<tipo>/<int:id>', methods=['GET'])
@login_required
def editar_categoria_form(tipo, id):
    user_id = session['user_id']

    conexao, cursor = ini_conexao()
    

    if tipo == 'tarefas':
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_tarefas
            WHERE id = %s AND user_id = %s
        """, (id, user_id))

    elif tipo == 'financas':
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_financas
            WHERE id = %s AND user_id = %s
        """, (id, user_id))

    else:
        flash("Tipo inválido", "error")
        return redirect(url_for('categorias.listar_categorias'))

    categoria = cursor.fetchone()

    if not categoria:
        flash("Categoria não encontrada", "error")
        return redirect(url_for('categorias.listar_categorias'))

    return render_template(
        'pasta_categorias/crud/edit_categorias.html.jinja',
        categoria=categoria,
        tipo=tipo
    )

@bp_categorias.route('/editar/<tipo>/<int:id>', methods=['POST'])
@login_required
def editar_categoria_salvar(tipo, id):

    nome = request.form['nome']
    cor = request.form['cor']
    user_id = session['user_id']

    conexao, cursor = ini_conexao()
    

    if tipo == 'tarefas':
        cursor.execute("""
            UPDATE categorias_tarefas
            SET nome = %s, cor = %s
            WHERE id = %s AND user_id = %s
        """, (nome, cor, id, user_id))

    elif tipo == 'financas':
        cursor.execute("""
            UPDATE categorias_financas
            SET nome = %s, cor = %s
            WHERE id = %s AND user_id = %s
        """, (nome, cor, id, user_id))

    else:
        flash("Tipo de categoria inválido", "error")
        return redirect(url_for('categorias.listar_categorias'))

    conexao.commit()

    flash("Categoria atualizada com sucesso!", "success")
    return redirect(url_for('categorias.listar_categorias'))
