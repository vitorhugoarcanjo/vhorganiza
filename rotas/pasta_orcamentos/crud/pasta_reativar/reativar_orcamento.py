# rotas/pasta_orcamentos/crud/pasta_reativar/reativar_orcamento.py
# ==========================================================
# REATIVAR ORÇAMENTO — VIEW (padrão 2099)
# ==========================================================

from flask import session, make_response, render_template
import json
import logging
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_orcamentos.services_auditoria import AuditoriaOrcamentosService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_orcamentos.services.services_orcamento import OrcamentosServices
from rotas.pasta_orcamentos.filters import OrcamentosFilters
from rotas.pasta_orcamentos.formatters import OrcamentosFormatters

from .services import ReativarOrcamentoService

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — busca orçamentos com filtros da sessão
# ==========================================================
def _buscar_orcamentos_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = OrcamentosFilters.processar_filtros_data()
    filtros = OrcamentosFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
    })
    service = OrcamentosServices(conexao=None, cursor=cursor)
    orcamentos_raw = service.buscar_orcamentos(user_id, filtros)
    return OrcamentosFormatters.formatar_lista(orcamentos_raw)


def _render_tbody(user_id, cursor):
    orcamentos = _buscar_orcamentos_com_filtros(cursor, user_id)
    return render_template(
        'pasta_orcamentos/partials/_tbody_orcamentos.html.jinja',
        orcamentos=orcamentos,
        mostrar_inativas=session.get('orcamentos_mostrar_inativas', '0'),
    )


# ==========================================================
# POST — REATIVA 1 ORÇAMENTO
# ==========================================================
@login_required
def reativar_orcamento(sequencia):
    """Reativa um orçamento (soft undelete). Recebe SEQUÊNCIA visual."""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        # 1. Reativa (service)
        sucesso, resultado = ReativarOrcamentoService.reativar_orcamento(
            cursor, sequencia, user_id
        )
        if not sucesso:
            return '', 404

        id_interno = resultado['id_interno']
        titulo = resultado['titulo']

        # 2. Auditoria transacional
        AuditoriaOrcamentosService.registrar(
            orcamento_id=id_interno,
            acao='reativada',
            campo_alterado='ativo',
            valor_antigo='0',
            valor_novo='1',
            conexao=conexao,
        )

        conexao.commit()

        # 3. Renderiza tbody atualizado
        html = _render_tbody(user_id, cursor)

        # 4. Retorna HTML + HX-Trigger
        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'orcamentoReativado': {'message': f'Orçamento "{titulo}" reativado!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao reativar orçamento sequencia={sequencia}")
        return '', 500