# rotas/pasta_orcamentos/crud/pasta_delete/excluir_orcamento.py
# ==========================================================
# EXCLUIR (INATIVAR) ORÇAMENTO — SOFT DELETE
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
from rotas.pasta_orcamentos.queries import OrcamentosQueries

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
# POST — INATIVA 1 ORÇAMENTO (soft delete)
# ==========================================================
@login_required
def excluir_orcamento(sequencia):
    """Inativa um orçamento (soft delete). Recebe SEQUÊNCIA visual."""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        # 1. Busca id_interno + título ANTES de inativar
        cursor.execute("""
            SELECT id, titulo FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, user_id))

        resultado = cursor.fetchone()
        if not resultado:
            conexao.close()
            return '', 404

        id_interno = resultado[0]
        titulo = resultado[1]

        # 2. Inativa (soft delete)
        cursor.execute(
            OrcamentosQueries.inativar_orcamento(),
            (user_id, sequencia, user_id)
        )

        # 3. 🔥 Auditoria transacional (usa id_interno)
        AuditoriaOrcamentosService.registrar(
            orcamento_id=id_interno,
            acao='inativada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        # 4. Renderiza tbody atualizado
        html = _render_tbody(user_id, cursor)
        conexao.close()

        # 5. Retorna HTML + HX-Trigger
        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'orcamentoInativado': {'message': f'Orçamento "{titulo}" inativado!'}
        })
        return resp

    except Exception as e:
        if conexao:
            conexao.rollback()
            conexao.close()
        logger.exception(f"Erro ao inativar orçamento sequencia={sequencia}")
        return '', 500