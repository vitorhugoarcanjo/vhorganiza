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
    Traduz pra ID interno + resolve o PAI (se for filha).
    """
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    # 1. Busca a transação clicada
    cursor.execute("""
        SELECT id, sequencia_transacoes, descricao, tipo, valor_total, transacao_pai_id
        FROM transacoes
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (transacao_id, user_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    id_interno = row[0]
    transacao_pai_id = row[5]

    # 2. 🔥 Se for FILHA, busca o PAI (pra header + auditoria)
    if transacao_pai_id:
        cursor.execute("""
            SELECT id, sequencia_transacoes, descricao, tipo, valor_total
            FROM transacoes
            WHERE id = %s AND user_id = %s
        """, (transacao_pai_id, user_id))
        pai_row = cursor.fetchone()

        if pai_row:
            # Usa dados do PAI pro header e auditoria
            id_interno = pai_row[0]
            transacao = (pai_row[1], pai_row[2], pai_row[3], pai_row[4])
        else:
            # Fallback: usa a filha
            transacao = (row[1], row[2], row[3], row[4])
    else:
        # Simples: usa a própria
        transacao = (row[1], row[2], row[3], row[4])

    # 3. Busca auditoria
    historico = AuditoriaFinanceiraService.listar_por_transacao_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_financas/modal_auditoria.html.jinja',
        historico=historico,
        transacao=transacao,
        transacao_id=transacao_id,   # exibe a SEQUÊNCIA da filha (URL) no header
    )