# rotas/pasta_categorias/crud/pasta_listar_modal/listar_modal.py
# ==========================================================
# MODAL LISTA DE CATEGORIAS - VIEW
# ==========================================================

import logging
from flask import request, session, render_template

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from rotas.pasta_categorias.services.services_categorias import CategoriasServices

logger = logging.getLogger(__name__)


@login_required
def abrir_modal_lista():
    """Abre o modal com a lista de categorias de UM módulo"""
    usuario_id = session['user_id']

    modulo = request.args.get('modulo', 'tarefas')
    if modulo not in ('tarefas', 'financas'):
        modulo = 'tarefas'

    conexao, cursor = ini_conexao()

    try:
        # Busca categorias ativas do módulo
        service = CategoriasServices(conexao=None, cursor=cursor)
        categorias = service.buscar_categorias_por_modulo(usuario_id, modulo)

        return render_template(
            'pasta_categorias/partials/_lista_categorias.html.jinja',
            categorias=categorias,
            modulo=modulo
        )
    finally:
        conexao.close()