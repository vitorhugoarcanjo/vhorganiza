# rotas/pasta_tela_pos_login/tela_pos_login.py
# ==========================================================
# TELA PÓS-LOGIN - "MEU DIA"
# ==========================================================

from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from rotas.middleware.autenticacao import login_required

bp_pos_login = Blueprint('pos_login', __name__)


@bp_pos_login.route('/')
@login_required
def iniposlogin():
    """
    Tela inicial pós-login.
    Retorna a casca vazia; os blocos (vencendo / próximos / resumo)
    carregam em paralelo via hx-get no load.
    """
    return render_template(
        'pasta_inicial_pos_login/tela_inicial.html',
        user_nome=session.get('user_nome'),
    )


# 🔥 REGISTRA OS PARTIALS (vencendo / proximos / resumo)
from .partials import bp_pos_login_partials
bp_pos_login.register_blueprint(bp_pos_login_partials, url_prefix='/partial')


# LOGOFF (mantido intacto)
@bp_pos_login.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        session.clear()
        return redirect(url_for('ini_app'))

    session.clear()
    return jsonify({
        'status': 'ok',
        'mensagem': 'Você saiu do sistema',
        'redirect': url_for('ini_app')
    })