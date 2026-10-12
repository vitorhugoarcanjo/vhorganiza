# rotas/pasta_tela_pos_login/partials/vencendo.py
# ==========================================================
# PARTIAL HTMX - VENCENDO (ATRASADO + HOJE)
# ==========================================================

import logging
from flask import render_template, session

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_tela_pos_login.services.services import PosLoginServices

logger = logging.getLogger(__name__)


def _buscar_vencendo(cursor, usuario_id):
    service = PosLoginServices(conexao=None, cursor=cursor)
    return service.buscar_vencendo(usuario_id)


def _render_vencendo(usuario_id, cursor):
    itens = _buscar_vencendo(cursor, usuario_id)
    html = render_template(
        'pasta_inicial_pos_login/partials/_vencendo.html.jinja',
        itens=itens,
    )
    # 🔥 OOB: atualiza contador no footer
    oob = f'<span id="poslTotalVencendo" hx-swap-oob="innerHTML">{len(itens)}</span>'
    return html + oob


@login_required
def partial_vencendo():
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        return _render_vencendo(usuario_id, cursor)
    except Exception:
        logger.exception("Erro ao renderizar partial 'vencendo'")
        return '', 200
    finally:
        conexao.close()