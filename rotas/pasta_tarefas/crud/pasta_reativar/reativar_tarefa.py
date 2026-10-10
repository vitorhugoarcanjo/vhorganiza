# rotas/pasta_tarefas/crud/pasta_reativar/reativar_tarefa.py
# ==========================================================
# REATIVAR TAREFA - HTMX puro (devolve <tbody> + HX-Trigger)
# ==========================================================

import logging
import json
from flask import session, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_tarefas.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from rotas.pasta_tarefas.services.services_tarefas import TarefasServices
from rotas.pasta_tarefas.filters import TarefasFilters
from rotas.pasta_tarefas.formatters import TarefasFormatters

from .services import ReativarTarefaService

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — busca tarefas com filtros da sessão
# ==========================================================
def _buscar_tarefas_com_filtros(cursor, usuario_id):
    data_inicio, data_fim, tipo_data = TarefasFilters.processar_filtros_data()
    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
        'categorias': TarefasFilters.filtro_categorias(usuario_id, cursor)[0],
        'status': TarefasFilters.filtro_status(),
        'prioridade': TarefasFilters.filtro_prioridade(),
        'descricao': TarefasFilters.filtro_descricao(),
        'mostrar_inativas': TarefasFilters.processar_mostrar_inativas(),
    }

    service = TarefasServices(conexao=None, cursor=cursor)
    tarefas_raw = service.buscar_tarefas(usuario_id, filtros)
    return TarefasFormatters.formatar_tarefas(tarefas_raw)


def _render_tbody(usuario_id, cursor):
    tarefas = _buscar_tarefas_com_filtros(cursor, usuario_id)
    return render_template(
        'pasta_tarefas/partials/_tbody_tarefas.html.jinja',
        tarefas=tarefas,
        mostrar_inativas=session.get('mostrar_inativas', '0'),
    )


# ==========================================================
# POST — REATIVA 1 TAREFA
# ==========================================================
@login_required
def reativar_tarefa(sequencia):
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        resultado = ReativarTarefaService.reativar_tarefa(cursor, sequencia, usuario_id)
        if not resultado.get('success'):
            conexao.close()
            return '', 404

        # 🔥 Auditoria com ID INTERNO
        AuditoriaService.registrar(
            tarefa_id=resultado['id_interno'],
            acao='reativada',
            campo_alterado='ativo',
            valor_antigo='0',
            valor_novo='1',
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(usuario_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'tarefaReativada': {'message': f'Tarefa "{resultado["titulo"]}" reativada!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao reativar tarefa sequencia={sequencia} usuario_id={user_id}")
        conexao.close()
        return '', 500