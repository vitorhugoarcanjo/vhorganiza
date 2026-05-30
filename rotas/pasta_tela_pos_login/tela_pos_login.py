from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify, request
from rotas.middleware.autenticacao import login_required

bp_pos_login = Blueprint('pos_login', __name__)


@bp_pos_login.route('/')
@login_required
def iniposlogin():
    return render_template('pasta_inicial_pos_login/tela_inicial.html', user_nome=session.get('user_nome'))




# LOGOFF
@bp_pos_login.route('/logout', methods=['GET', 'POST'])  # <-- ADICIONA POST AQUI
def logout():
    # Verifica se é AJAX
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        session.clear()
        return redirect(url_for('ini_app'))

    session.clear()

    return jsonify({
        'status': 'ok',
        'mensagem': 'Você saiu do sistema',
        'redirect': url_for('ini_app')
    })