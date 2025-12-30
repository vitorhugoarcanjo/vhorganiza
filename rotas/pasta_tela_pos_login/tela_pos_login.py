from flask import Blueprint, render_template, session, flash, redirect, url_for
from rotas.middleware.autenticacao import login_required

bp_pos_login = Blueprint('pos_login', __name__)


@bp_pos_login.route('/')
@login_required
def iniposlogin():
    return render_template('pasta_tela_pos_login/teste.html', user_nome=session.get('user_nome'))




# LOGOFF
@bp_pos_login.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('appinicializar'))