# rotas/auditoria_geral/pasta_orcamentos/logica_auditoria.py
# ==========================================================
# AUDITORIA DE ORÇAMENTOS - VIEW (Modal HTMX)
# ==========================================================

from flask import render_template, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .services_auditoria import AuditoriaOrcamentosService


@login_required
def historico_orcamento(orcamento_seq):
    """
    Recebe a SEQUÊNCIA (URL: /auditoria/orcamento/<seq>).
    Traduz pra ID interno e busca auditoria.
    """
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    # 🔥 Busca por SEQUÊNCIA (não id)
    cursor.execute("""
        SELECT id, sequencia_orcamentos, titulo, cliente, status
        FROM orcamentos
        WHERE sequencia_orcamentos = %s AND usuario_id = %s
    """, (orcamento_seq, user_id))

    row = cursor.fetchone()
    if not row:
        return '', 404

    id_interno = row[0]
    orcamento = (row[1], row[2], row[3], row[4])  # (seq, titulo, cliente, status)

    # 🔥 Busca auditoria por ID INTERNO
    historico = AuditoriaOrcamentosService.listar_por_orcamento_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_orcamentos/modal_auditoria.html.jinja',
        historico=historico,
        orcamento=orcamento,
        orcamento_id=orcamento_seq,   # ← passa a SEQUÊNCIA pro header
    )