from flask import Blueprint, render_template
from rotas.middleware.autenticacao import login_required

bp_config = Blueprint('config', __name__)

@bp_config.route('/')
@login_required
def iniconfig():
    return render_template('pasta_configuracoes/config.html')
