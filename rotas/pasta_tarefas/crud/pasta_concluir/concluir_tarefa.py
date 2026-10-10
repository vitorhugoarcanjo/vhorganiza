# rotas/pasta_tarefas/crud/pasta_concluir/concluir_tarefa.py
# ==========================================================
# CONCLUIR TAREFA - HTMX puro (devolve <tbody> + HX-Trigger)
# ==========================================================

import logging
import json
from flask import request, session, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_tarefas.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from rotas.pasta_tarefas.services.services_tarefas import TarefasServices
from rotas.pasta_tarefas.filters import TarefasFilters
from rotas.pasta_tarefas.formatters import TarefasFormatters

from .services import ConcluirTarefaService

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — formata data/hora BR
# ==========================================================
def _fmt_data_hora_br(data_str):
    """Converte 'YYYY-MM-DD HH:MM:SS' pra 'DD/MM/YYYY HH:MM:SS'."""
    if not data_str:
        return ''
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
# POST — CONCLUI 1 TAREFA
# ==========================================================
@login_required
def concluir(sequencia):
    usuario_id = session['user_id']

    # Motivo vem do form (htmx-include) ou JSON
    motivo = (request.form.get('motivo_conclusao') or '').strip()
    if not motivo and request.is_json:
        motivo = ((request.json or {}).get('motivo_conclusao') or '').strip()

    conexao, cursor = ini_conexao()

    try:
        resultado = ConcluirTarefaService.concluir_tarefa(cursor, sequencia, usuario_id, motivo)
        if not resultado.get('success'):
            conexao.close()
            return '', 404

        # 🔥 Auditoria com ID INTERNO — 3 campos alterados
        alteracoes = [
            {
                'campo': 'Status',
                'antes': resultado['status_antes'] or 'pendente',
                'depois': 'concluido',
            },
            {
                'campo': 'Data Finalização',
                'antes': '(vazio)',
                'depois': _fmt_data_hora_br(resultado['data_finalizacao']),
            },
            {
                'campo': 'Motivo Conclusão',
                'antes': '(vazio)',
                'depois': motivo or '(sem observações)',
            },
        ]

        AuditoriaService.registrar(
            tarefa_id=resultado['id_interno'],
            acao='concluida',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(usuario_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'tarefaConcluida': {'message': f'Tarefa "{resultado["titulo"]}" concluída!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao concluir tarefa sequencia={sequencia} usuario_id={usuario_id}")
        conexao.close()
        return '', 500