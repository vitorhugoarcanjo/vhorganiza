# rotas/pasta_tarefas/crud/pasta_reabrir/reabrir_tarefa.py
# ==========================================================
# REABRIR TAREFA - HTMX puro (devolve <tbody> + HX-Trigger)
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

from .services import ReabrirTarefaService

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — formata data/hora BR
# ==========================================================
def _fmt_data_hora_br(data_str):
    """Converte 'YYYY-MM-DD HH:MM:SS' pra 'DD/MM/YYYY HH:MM:SS'."""
    if not data_str:
        return '(vazio)'
    s = str(data_str).strip()
    if len(s) >= 10 and s[4] == '-' and s[7] == '-':
        ano = s[0:4]
        mes = s[5:7]
        dia = s[8:10]
        resto = s[10:]  # ' HH:MM:SS' ou vazio
        return f'{dia}/{mes}/{ano}{resto}'
    return s


# ==========================================================
# HELPER — busca tarefas com filtros da sessão
# ==========================================================
def _buscar_tarefas_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = TarefasFilters.processar_filtros_data()
    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
        'categorias': TarefasFilters.filtro_categorias(user_id, cursor)[0],
        'status': TarefasFilters.filtro_status(),
        'prioridade': TarefasFilters.filtro_prioridade(),
        'descricao': TarefasFilters.filtro_descricao(),
        'mostrar_inativas': TarefasFilters.processar_mostrar_inativas(),
    }

    service = TarefasServices(conexao=None, cursor=cursor)
    tarefas_raw = service.buscar_tarefas(user_id, filtros)
    return TarefasFormatters.formatar_tarefas(tarefas_raw)


def _render_tbody(user_id, cursor):
    tarefas = _buscar_tarefas_com_filtros(cursor, user_id)
    return render_template(
        'pasta_tarefas/partials/_tbody_tarefas.html.jinja',
        tarefas=tarefas,
        mostrar_inativas=session.get('mostrar_inativas', '0'),
    )


# ==========================================================
# POST — REABRE 1 TAREFA
# ==========================================================
@login_required
def reabrir_tarefa(sequencia):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        resultado = ReabrirTarefaService.reabrir_tarefa(cursor, sequencia, user_id)
        if not resultado.get('success'):
            conexao.close()
            return '', 404

        # 🔥 Auditoria com ID INTERNO — 3 campos alterados
        alteracoes = [
            {
                'campo': 'Status',
                'antes': resultado['status_antes'] or 'concluido',
                'depois': 'pendente',
            },
            {
                'campo': 'Data Finalização',
                'antes': _fmt_data_hora_br(resultado['data_finalizacao_antes']),
                'depois': '(vazio)',
            },
            {
                'campo': 'Motivo Conclusão',
                'antes': resultado['motivo_antes'] or '(vazio)',
                'depois': '(vazio)',
            },
        ]

        AuditoriaService.registrar(
            tarefa_id=resultado['id_interno'],
            acao='reaberta',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(user_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'tarefaReaberta': {'message': f'Tarefa "{resultado["titulo"]}" reaberta!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao reabrir tarefa sequencia={sequencia} user_id={user_id}")
        conexao.close()
        return '', 500