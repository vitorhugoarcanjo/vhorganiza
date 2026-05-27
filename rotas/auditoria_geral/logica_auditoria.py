# rotas/auditoria_geral/routes.py
from flask import Blueprint, render_template, request, session, url_for
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.services_auditoria import AuditoriaService

bp_auditoria_tarefas = Blueprint('auditoria', __name__)

@bp_auditoria_tarefas.route('/tarefa/<int:tarefa_seq>')
@login_required
def historico_tarefa(tarefa_seq):
    """Ver histórico de alterações de uma tarefa"""
    
    # Pega os parâmetros da URL
    mostrar_inativas = request.args.get('mostrar_inativas', '0')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo_data = request.args.get('tipo_data', 'inicio')
    
    # Usa o método formatado
    historico = AuditoriaService.listar_por_tarefa_formatado(tarefa_seq)
    
    return render_template('pasta_auditoria/pasta_tarefas/auditoria_tarefas.html', 
                          historico=historico, 
                          tarefa_seq=tarefa_seq,
                          mostrar_inativas=mostrar_inativas,
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          tipo_data=tipo_data)