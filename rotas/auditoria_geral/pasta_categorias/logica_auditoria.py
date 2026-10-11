# rotas/auditoria_geral/pasta_categorias/logica_auditoria.py
# ==========================================================
# AUDITORIA DE CATEGORIAS - VIEW (Modal HTMX)
# ==========================================================

from flask import render_template, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .services_auditoria import AuditoriaCategoriasService


@login_required
def historico_categoria(categoria_id):
    """
    Recebe o ID interno da categoria.
    Busca a auditoria e renderiza o modal.
    """
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    # 1. Busca a categoria (pra montar header do modal)
    cursor.execute("""
        SELECT id, sequencia_categorias, nome, modulo, cor
        FROM categorias
        WHERE id = %s AND usuario_id = %s
    """, (categoria_id, usuario_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    # Tupla pro template: (sequencia, nome, modulo, cor)
    categoria = (row[1], row[2], row[3], row[4])

    # 2. Busca auditoria
    historico = AuditoriaCategoriasService.listar_por_categoria_formatado(categoria_id)

    return render_template(
        'pasta_auditoria/pasta_categorias/modal_auditoria.html.jinja',
        historico=historico,
        categoria=categoria,
        categoria_id=categoria_id,
    )