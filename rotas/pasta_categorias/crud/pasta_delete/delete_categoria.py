# rotas/pasta_categorias/crud/pasta_delete/delete_categoria.py
# ==========================================================
# INATIVAR CATEGORIA - VIEW FUNCS (HTML + HX-Trigger)
# ==========================================================

import json
import logging
from flask import session, make_response, render_template

from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_categorias.services_auditoria import AuditoriaCategoriasService
from utils.database.conexao_global import ini_conexao

from .services import InativarCategoriaService
from rotas.pasta_categorias.services.services_categorias import CategoriasServices
from rotas.pasta_categorias.filters import CategoriasFilters
from rotas.pasta_categorias.formatters import CategoriasFormatters

logger = logging.getLogger(__name__)


def _buscar_categorias_por_modulo(cursor, usuario_id, modulo):
    """Helper — busca categorias do módulo com filtros da sessão"""
    filtros = {
        'descricao':        CategoriasFilters.filtro_descricao(),
        'mostrar_inativas': CategoriasFilters.processar_mostrar_inativas(),
        'modulo':           modulo,
    }
    service = CategoriasServices(conexao=None, cursor=cursor)
    categorias_raw = service.buscar_categorias(usuario_id, filtros)
    return CategoriasFormatters.formatar_categorias(categorias_raw)


def _render_tbody(user_id, cursor, modulo):
    categorias = _buscar_categorias_por_modulo(cursor, user_id, modulo)
    return render_template(
        'pasta_categorias/partials/_tbody_categorias.html.jinja',
        categorias=categorias,
        modulo=modulo,
        mostrar_inativas=CategoriasFilters.processar_mostrar_inativas(),
    )


# ==========================================================
# POST — INATIVA CATEGORIA (soft delete)
# ==========================================================
@login_required
def inativar_categoria_view(categoria_id):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        categoria = InativarCategoriaService.buscar_categoria(cursor, categoria_id, user_id)
        if not categoria:
            conexao.close()
            return '', 404

        nome   = categoria[1]
        modulo = categoria[2]

        InativarCategoriaService.inativar_categoria(cursor, categoria_id, user_id)

        # 🔥 Auditoria transacional
        AuditoriaCategoriasService.registrar(
            categoria_id=categoria_id,
            acao='inativada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(user_id, cursor, modulo)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'categoriaInativada': {'message': f'Categoria "{nome}" inativada!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao inativar categoria id={categoria_id}")
        conexao.close()
        return '', 500