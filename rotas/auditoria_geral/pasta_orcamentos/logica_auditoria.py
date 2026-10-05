# rotas/auditoria_geral/pasta_orcamentos/logica_auditoria.py
# ==========================================================
# AUDITORIA DE ORÇAMENTOS - VIEW (Modal HTMX)
# ==========================================================

from flask import render_template, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .services_auditoria import AuditoriaOrcamentosService


@login_required
def historico_orcamento(orcamento_id):
    """Retorna o HTML do MODAL de auditoria de orçamentos"""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    # Busca orçamento (pro header)
    cursor.execute("""
        SELECT id, titulo, cliente, status
        FROM orcamentos
        WHERE id = %s AND usuario_id = %s
    """, (orcamento_id, user_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    orcamento = (row[0], row[1], row[2], row[3])

    historico = AuditoriaOrcamentosService.listar_por_orcamento_formatado(orcamento_id)

    return render_template(
        'pasta_auditoria/pasta_orcamentos/modal_auditoria.html.jinja',
        historico=historico,
        orcamento=orcamento,
        orcamento_id=orcamento_id,
    )