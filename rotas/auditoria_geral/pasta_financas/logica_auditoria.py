# rotas/auditoria_geral/pasta_financas/logica_auditoria.py
# ==========================================================
# AUDITORIA DE FINANÇAS - VIEW (Modal HTMX)
# ==========================================================

from flask import render_template, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .services_auditoria import AuditoriaFinanceiraService


@login_required
def historico_transacao(transacao_id):
    """
    Recebe a SEQUÊNCIA (URL: /auditoria/transacao/<seq>).
    Traduz pra ID interno e busca auditoria.
    """
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    # 🆕 Busca transação pelo ID interno + dados pra header
    cursor.execute("""
        SELECT id, sequencia_transacoes, descricao, tipo, valor_total
        FROM transacoes
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (transacao_id, user_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    id_interno = row[0]

    # 🆕 Monta a tupla no mesmo formato que o template espera:
    # transacao[1] = descricao, transacao[2] = tipo, transacao[3] = valor
    transacao = (row[1], row[2], row[3], row[4])

    # 🔥 Busca auditoria pelo ID INTERNO (não pela sequência)
    historico = AuditoriaFinanceiraService.listar_por_transacao_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_financas/modal_auditoria.html.jinja',
        historico=historico,
        transacao=transacao,
        transacao_id=transacao_id,   # exibe a SEQUÊNCIA no header
    )