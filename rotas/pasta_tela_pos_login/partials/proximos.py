# rotas/pasta_tela_pos_login/partials/proximos.py
# ==========================================================
# PARTIAL HTMX - PRÓXIMOS 7 DIAS
# ==========================================================

import logging
from flask import render_template, session

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_tela_pos_login.services.services import PosLoginServices

logger = logging.getLogger(__name__)


def _buscar_proximos(cursor, usuario_id):
    service = PosLoginServices(conexao=None, cursor=cursor)
    return service.buscar_proximos(usuario_id)


def _render_proximos(usuario_id, cursor):
    itens = _buscar_proximos(cursor, usuario_id)
    html = render_template(
        'pasta_inicial_pos_login/partials/_proximos.html.jinja',
        itens=itens,
    )
    oob = f'<span id="poslTotalProximos" hx-swap-oob="innerHTML">{len(itens)}</span>'
    return html + oob


@login_required
def partial_proximos():
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        return _render_proximos(usuario_id, cursor)
    except Exception:
        logger.exception("Erro ao renderizar partial 'proximos'")
        return '', 200
    finally:
        conexao.close()