# rotas/pasta_tela_pos_login/partials/resumo.py
# ==========================================================
# PARTIAL HTMX - RESUMO RÁPIDO (KPIs DO MÊS)
# ==========================================================

import logging
from flask import render_template, session

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_tela_pos_login.services.services import PosLoginServices

logger = logging.getLogger(__name__)


def _buscar_resumo(cursor, usuario_id):
    service = PosLoginServices(conexao=None, cursor=cursor)
    return service.buscar_resumo(usuario_id)


def _render_resumo(usuario_id, cursor):
    dados = _buscar_resumo(cursor, usuario_id)
    html = render_template(
        'pasta_inicial_pos_login/partials/_resumo.html.jinja',
        resumo=dados,
    )
    # 🔥 OOB: atualiza saldo no footer
    oob = f'<span id="poslTotalSaldo" hx-swap-oob="innerHTML">{dados["saldo_fmt"]}</span>'
    return html + oob


@login_required
def partial_resumo():
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        return _render_resumo(usuario_id, cursor)
    except Exception:
        logger.exception("Erro ao renderizar partial 'resumo'")
        return '', 200
    finally:
        conexao.close()