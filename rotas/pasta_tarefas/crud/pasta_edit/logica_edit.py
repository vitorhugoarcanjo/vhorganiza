from flask import Blueprint, render_template
from rotas.middleware.autenticacao import login_required

bp_tela_edit = Blueprint('editar_tarefa', __name__)


@bp_tela_edit.route('/editar_tarefa/<int:tarefa_id>', methods=['GET', 'POST'])
@login_required
def iniedittarefa(tarefa_id):


    return render_template('pasta_tarefas/crud/tela_edit.html')