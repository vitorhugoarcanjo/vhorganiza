# rotas/auditoria_geral/pasta_tarefas/logica_auditoria.py
# ==========================================================
# AUDITORIA DE TAREFAS - VIEW (Modal HTMX)
# ==========================================================

from flask import render_template, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .services_auditoria import AuditoriaService


@login_required
def historico_tarefa(tarefa_seq):
    """
    Recebe a SEQUÊNCIA (URL: /auditoria/tarefa/<seq>).
    Traduz pra ID interno e busca auditoria.
    """
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    # 🆕 Busca tarefa pelo ID interno + dados pro header
    cursor.execute("""
        SELECT id, tarefa_sequencia, titulo
        FROM tarefas
        WHERE tarefa_sequencia = %s AND user_id = %s
    """, (tarefa_seq, user_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    id_interno = row[0]

    # 🆕 Monta tupla no formato esperado pelo template:
    # tarefa[1] = titulo
    tarefa = (row[1], row[2])

    # 🔥 Busca auditoria pelo ID INTERNO
    historico = AuditoriaService.listar_por_tarefa_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_tarefas/modal_auditoria.html.jinja',
        historico=historico,
        tarefa=tarefa,
        tarefa_seq=tarefa_seq,   # exibe a SEQUÊNCIA no header
    )