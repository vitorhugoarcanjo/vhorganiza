# rotas/pasta_categorias/logica_insert_categorias.py
# ==========================================================
# CATEGORIAS - Blueprint e rotas
# ==========================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .tela_categorias import ini_categorias
from .crud.categorias_tarefas.cat_tarefas import insert_cat_tarefa
from .crud.categorias_financas.cat_financas import insert_cat_fin


bp_categorias = Blueprint('categorias', __name__)


@bp_categorias.route('/', methods=['GET'])
@login_required
def listar_categorias():
    return ini_categorias()


@bp_categorias.route('/novo', methods=['GET', 'POST'])
@login_required
def insert_categorias_global():
    msg = ''

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cor = request.form.get('cor', '').strip()
        modulo = request.form.get('modulo', '').strip()

        if not all([nome, cor, modulo]):
            msg = 'Descreva todos os campos corretamente!'
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)

        usuario_id = session['user_id']
        conexao, cursor = ini_conexao()

        if modulo == 'tarefas':
            ok, msg = insert_cat_tarefa(nome, cor, usuario_id, cursor)
        elif modulo == 'financas':
            ok, msg = insert_cat_fin(nome, cor, usuario_id, cursor)
        else:
            msg = 'Módulo inválido'
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)

        if ok:
            conexao.commit()
            return redirect(url_for('categorias.listar_categorias'))
        else:
            conexao.rollback()
            msg = msg or 'Erro ao criar categoria'
            return render_template('pasta_categorias/crud/insert_categorias.html', msg=msg)

    return render_template('pasta_categorias/crud/insert_categorias.html')


@bp_categorias.route('/excluir/<modulo>/<int:id>')
@login_required
def excluir_categoria(modulo, id):
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    if modulo == 'tarefas':
        cursor.execute("""
            DELETE FROM categorias_tarefas
            WHERE id = %s AND usuario_id = %s
        """, (id, usuario_id))

    elif modulo == 'financas':
        cursor.execute("""
            DELETE FROM categorias_financas
            WHERE id = %s AND usuario_id = %s
        """, (id, usuario_id))

    else:
        flash('Módulo inválido', 'error')
        return redirect(url_for('categorias.listar_categorias'))

    conexao.commit()

    flash('Categoria excluída com sucesso!', 'success')
    return redirect(url_for('categorias.listar_categorias'))


@bp_categorias.route('/editar/<tipo>/<int:id>', methods=['GET'])
@login_required
def editar_categoria_form(tipo, id):
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    if tipo == 'tarefas':
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_tarefas
            WHERE id = %s AND usuario_id = %s
        """, (id, usuario_id))

    elif tipo == 'financas':
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_financas
            WHERE id = %s AND usuario_id = %s
        """, (id, usuario_id))

    else:
        flash('Tipo inválido', 'error')
        return redirect(url_for('categorias.listar_categorias'))

    categoria = cursor.fetchone()

    if not categoria:
        flash('Categoria não encontrada', 'error')
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
    usuario_id = session['user_id']

    conexao, cursor = ini_conexao()

    if tipo == 'tarefas':
        cursor.execute("""
            UPDATE categorias_tarefas
            SET nome = %s, cor = %s
            WHERE id = %s AND usuario_id = %s
        """, (nome, cor, id, usuario_id))

    elif tipo == 'financas':
        cursor.execute("""
            UPDATE categorias_financas
            SET nome = %s, cor = %s
            WHERE id = %s AND usuario_id = %s
        """, (nome, cor, id, usuario_id))

    else:
        flash('Tipo de categoria inválido', 'error')
        return redirect(url_for('categorias.listar_categorias'))

    conexao.commit()

    flash('Categoria atualizada com sucesso!', 'success')
    return redirect(url_for('categorias.listar_categorias'))