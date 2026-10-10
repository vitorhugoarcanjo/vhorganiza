# rotas/pasta_financas/crud/pasta_delete/delete_transacao.py
from flask import session, make_response, render_template
import json
import logging
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.services.services_financas import FinancasServices
from rotas.pasta_financas.filters import FinancasFilters
from rotas.pasta_financas.formatters import FinancasFormatters

logger = logging.getLogger(__name__)


# ==========================================================
# HELPER — busca transações com filtros da sessão
# ==========================================================
def _buscar_transacoes_com_filtros(cursor, usuario_id):
    data_inicio, data_fim, tipo_data = FinancasFilters.processar_filtros_data()
    filtros = FinancasFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
    })
    service = FinancasServices(conexao=None, cursor=cursor)
    transacoes_raw = service.buscar_transacoes(usuario_id, filtros)
    return FinancasFormatters.formatar_transacoes(transacoes_raw)


def _render_tbody(usuario_id, cursor):
    transacoes = _buscar_transacoes_com_filtros(cursor, usuario_id)
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
    """transacao_id aqui é a SEQUÊNCIA visual"""
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        cursor.execute("""
            SELECT id, descricao, total_parcelas, numero_parcela, transacao_pai_id
            FROM transacoes
            WHERE sequencia_transacoes = %s AND usuario_id = %s AND ativo = 1
        """, (transacao_id, usuario_id))

        transacao = cursor.fetchone()
        if not transacao:
            conexao.close()
            return '', 404

        id_interno = transacao[0]                # 🆕
        descricao = transacao[1]
        total_parcelas = transacao[2]
        transacao_pai_id = transacao[4]

        eh_parcelamento = (
            transacao_pai_id is not None or
            (total_parcelas and total_parcelas > 1)
        )

        # ==========================================================
        # PARCELAMENTO → pede confirmação
        # ==========================================================
        if eh_parcelamento:
            if transacao_pai_id is not None:
                pai_real_id = transacao_pai_id
            else:
                cursor.execute("""
                    SELECT id FROM transacoes
                    WHERE sequencia_transacoes = %s AND usuario_id = %s
                """, (transacao_id, usuario_id))
                pai_real = cursor.fetchone()
                pai_real_id = pai_real[0] if pai_real else None

            html = _render_tbody(usuario_id, cursor)
            conexao.close()

            resp = make_response(html)
            resp.headers['HX-Trigger'] = json.dumps({
                'pedirConfirmacaoParcelamento': {
                    'pai_id': pai_real_id,
                    'descricao': descricao
                }
            })
            return resp

        # ==========================================================
        # SIMPLES → inativa + audita
        # ==========================================================
        cursor.execute("""
            UPDATE transacoes
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 1
        """, (usuario_id, id_interno, usuario_id))

        # 🔥 Auditoria transacional
        AuditoriaFinanceiraService.registrar(
            transacao_id=id_interno,
            acao='excluida',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(usuario_id, cursor)
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
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        cursor.execute("""
            SELECT id, descricao FROM transacoes
            WHERE id = %s AND usuario_id = %s AND ativo = 1
        """, (pai_id, usuario_id))

        pai = cursor.fetchone()
        if not pai:
            conexao.close()
            return '', 404

        cursor.execute("""
            UPDATE transacoes
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE (id = %s OR transacao_pai_id = %s)
            AND usuario_id = %s AND ativo = 1
        """, (usuario_id, pai_id, pai_id, usuario_id))

        # 🔥 Auditoria (usa o id do PAI)
        AuditoriaFinanceiraService.registrar(
            transacao_id=pai_id,
            acao='excluida_parcelada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        html = _render_tbody(usuario_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = 'transacaoInativada'
        return resp

    except Exception as e:
        conexao.rollback()
        logger.error(f"Erro ao inativar parcelamento {pai_id}: {e}")
        conexao.close()
        return '', 500