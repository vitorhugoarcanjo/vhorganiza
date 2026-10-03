# rotas/pasta_financas/crud/pasta_delete/delete_transacao.py
from flask import session, make_response, render_template
import json
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.services.services_financas import FinancasServices
from rotas.pasta_financas.filters import FinancasFilters
from rotas.pasta_financas.formatters import FinancasFormatters
import logging

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — busca transações com filtros da sessão
# ==========================================================
def _buscar_transacoes_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = FinancasFilters.processar_filtros_data()
    filtros = FinancasFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
    })
    service = FinancasServices(conexao=None, cursor=cursor)
    transacoes_raw = service.buscar_transacoes(user_id, filtros)
    return FinancasFormatters.formatar_transacoes(transacoes_raw)


def _render_tbody(user_id, cursor):
    transacoes = _buscar_transacoes_com_filtros(cursor, user_id)
    return render_template(
        'pasta_financas/partials/_tbody_transacoes.html.jinja',
        transacoes=transacoes,
        mostrar_inativas=session.get('financas_mostrar_inativas', '0'),
        data_inicio='', data_fim='', tipo_data='emissao'
    )


# ==========================================================
# POST — INATIVA 1 TRANSAÇÃO
# ==========================================================
@login_required
def inativar_financa(transacao_id):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        cursor.execute("""
            SELECT descricao, total_parcelas, numero_parcela, transacao_pai_id
            FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 1
        """, (transacao_id, user_id))

        transacao = cursor.fetchone()
        if not transacao:
            conexao.close()
            return '', 404

        transacao_pai_id = transacao[3]
        eh_parcelamento = (
            transacao_pai_id is not None or
            (transacao[1] and transacao[1] > 1)
        )

        if eh_parcelamento:
            if transacao_pai_id is not None:
                pai_real_id = transacao_pai_id
            else:
                cursor.execute("""
                    SELECT id FROM transacoes
                    WHERE sequencia_transacoes = %s AND user_id = %s
                """, (transacao_id, user_id))
                pai_real = cursor.fetchone()
                pai_real_id = pai_real[0] if pai_real else None

            html = _render_tbody(user_id, cursor)
            conexao.close()

            resp = make_response(html)
            resp.headers['HX-Trigger'] = json.dumps({
                'pedirConfirmacaoParcelamento': {
                    'pai_id': pai_real_id,
                    'descricao': transacao[0]
                }
            })
            return resp

        cursor.execute("""
            UPDATE transacoes
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 1
        """, (user_id, transacao_id, user_id))
        conexao.commit()

        html = _render_tbody(user_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = 'transacaoInativada'
        return resp

    except Exception as e:
        conexao.rollback()
        logger.error(f"Erro ao inativar transação {transacao_id}: {e}")
        conexao.close()
        return '', 500


# ==========================================================
# POST — INATIVA PARCELAMENTO COMPLETO
# ==========================================================
@login_required
def excluir_parcelamento_completo(pai_id):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        cursor.execute("""
            SELECT id FROM transacoes
            WHERE id = %s AND user_id = %s AND ativo = 1
        """, (pai_id, user_id))

        if not cursor.fetchone():
            conexao.close()
            return '', 404

        cursor.execute("""
            UPDATE transacoes
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE (id = %s OR transacao_pai_id = %s)
            AND user_id = %s AND ativo = 1
        """, (user_id, pai_id, pai_id, user_id))
        conexao.commit()

        html = _render_tbody(user_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = 'transacaoInativada'
        return resp

    except Exception as e:
        conexao.rollback()
        logger.error(f"Erro ao inativar parcelamento {pai_id}: {e}")
        conexao.close()
        return '', 500