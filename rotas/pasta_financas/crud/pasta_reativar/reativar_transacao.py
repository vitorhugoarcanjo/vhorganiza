# rotas/pasta_financas/crud/pasta_reativar/reativar_transacao.py
from flask import session, jsonify, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters
from rotas.pasta_financas.services.services_financas import FinancasServices
from rotas.pasta_financas.filters import FinancasFilters


# ==========================================================
# HELPER — busca as transações da listagem COM FILTROS
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


# ==========================================================
# GET — verifica o tipo (JSON)
# ==========================================================
@login_required
def verificar_reativacao_view(transacao_seq):
    usuario_id = session.get('user_id')
    if not usuario_id:
        return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 401

    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT descricao, status, tipo, ativo, transacao_pai_id, total_parcelas
        FROM transacoes
        WHERE sequencia_transacoes = %s AND usuario_id = %s AND ativo = 0
    """, (transacao_seq, usuario_id))

    transacao = cursor.fetchone()
    conexao.close()

    if not transacao:
        return jsonify({'success': False, 'error': 'Transação não encontrada ou já está ativa!'}), 404

    # Parcela (tem pai)
    if transacao[4] is not None:
        return jsonify({
            'tipo': 'parcela',
            'mensagem': 'Esta é uma parcela. Deseja reativar o parcelamento COMPLETO?',
            'transacao_pai_id': transacao[4],
            'total_parcelas': transacao[5],
            'descricao': transacao[0]
        })

    # Parcelamento (é o pai)
    if transacao[5] > 1:
        return jsonify({
            'tipo': 'parcelamento',
            'mensagem': f'Esta transação possui {transacao[5]} parcelas. Deseja reativar tudo?',
            'total_parcelas': transacao[5],
            'descricao': transacao[0]
        })

    # Simples
    return jsonify({
        'tipo': 'simples',
        'descricao': transacao[0],
        'mensagem': f'Deseja reativar a transação "{transacao[0]}"?'
    })


# ==========================================================
# POST — reativa 1 transação (simples) → devolve 1 <tr>
# ==========================================================
@login_required
def reativar_view(transacao_seq):
    usuario_id = session.get('user_id')
    if not usuario_id:
        return '', 401

    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT id, descricao
        FROM transacoes
        WHERE sequencia_transacoes = %s AND usuario_id = %s AND ativo = 0
    """, (transacao_seq, usuario_id))

    transacao = cursor.fetchone()
    if not transacao:
        conexao.close()
        return '', 404

    id_interno = transacao[0]   # 🆕

    cursor.execute("""
        UPDATE transacoes
        SET ativo = 1,
            excluido_em = NULL,
            excluido_por = NULL,
            data_alteracao = CURRENT_TIMESTAMP
        WHERE id = %s AND usuario_id = %s AND ativo = 0
    """, (id_interno, usuario_id))

    # 🔥 Auditoria
    AuditoriaFinanceiraService.registrar(
        transacao_id=id_interno,
        acao='reativada',
        campo_alterado='ativo',
        valor_antigo='0',
        valor_novo='1',
        conexao=conexao,
    )

    conexao.commit()

    # Busca atualizada
    cursor.execute("""
        SELECT t.sequencia_transacoes, t.id, t.tipo, t.valor_total, t.descricao, t.data_emissao,
               c.nome AS categoria_nome, c.cor AS categoria_cor,
               t.status, t.data_vencimento, t.ativo,
               t.numero_parcela, t.total_parcelas, t.transacao_pai_id, t.valor_parcela
        FROM transacoes t
        LEFT JOIN categorias_financas c ON c.id = t.categoria_id
        WHERE t.id = %s AND t.usuario_id = %s
    """, (id_interno, usuario_id))

    transacao_atualizada = cursor.fetchone()
    conexao.close()

    if not transacao_atualizada:
        return '', 404

    transacao_formatada = FinancasFormatters.formatar_transacoes([transacao_atualizada])[0]

    html = render_template(
        'pasta_financas/partials/_linha_transacao.html.jinja',
        transacao=transacao_formatada,
        mostrar_inativas='0',
        data_inicio='', data_fim='', tipo_data='emissao'
    )

    resp = make_response(html)
    resp.headers['HX-Trigger'] = 'transacaoReativada'
    return resp


# ==========================================================
# POST — reativa parcelamento completo → devolve o TBODY
# ==========================================================
@login_required
def reativar_parcelamento_view(transacao_pai_id):
    usuario_id = session.get('user_id')
    if not usuario_id:
        return '', 401

    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT id FROM transacoes
        WHERE id = %s AND usuario_id = %s AND ativo = 0
    """, (transacao_pai_id, usuario_id))

    pai = cursor.fetchone()
    if not pai:
        conexao.close()
        return '', 404

    cursor.execute("""
        UPDATE transacoes
        SET ativo = 1,
            excluido_em = NULL,
            excluido_por = NULL,
            data_alteracao = CURRENT_TIMESTAMP
        WHERE (id = %s OR transacao_pai_id = %s)
        AND usuario_id = %s
        AND ativo = 0
    """, (transacao_pai_id, transacao_pai_id, usuario_id))

    # 🔥 Auditoria (usa o id do PAI)
    AuditoriaFinanceiraService.registrar(
        transacao_id=transacao_pai_id,
        acao='reativada_parcelada',
        campo_alterado='ativo',
        valor_antigo='0',
        valor_novo='1',
        conexao=conexao,
    )

    conexao.commit()

    transacoes_formatadas = _buscar_transacoes_com_filtros(cursor, usuario_id)
    conexao.close()

    html = render_template(
        'pasta_financas/partials/_tbody_transacoes.html.jinja',
        transacoes=transacoes_formatadas,
        mostrar_inativas=session.get('financas_mostrar_inativas', '0'),
        data_inicio='', data_fim='', tipo_data='emissao'
    )

    resp = make_response(html)
    resp.headers['HX-Trigger'] = 'transacaoReativada'
    return resp