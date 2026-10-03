# rotas/pasta_financas/crud/pasta_estornar/estornar_transacao.py
from flask import session, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters


@login_required
def estornar_transacao_view(sequencia):
    user_id = session.get('user_id')

    if not user_id:
        return '', 401

    conexao, cursor = ini_conexao()

    # Busca dados ANTES
    cursor.execute("""
        SELECT descricao, status, tipo, data_quitamento
        FROM transacoes
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (sequencia, user_id))

    transacao = cursor.fetchone()
    if not transacao:
        conexao.close()
        return '', 404

    # Só estorna se estiver quitado/recebido
    if transacao[1] not in ['quitado', 'recebido']:
        conexao.close()
        return '', 400

    status_anterior = transacao[1]
    data_quitamento_anterior = transacao[3]

    # Estorna: volta pra 'aberto' e limpa data_quitamento
    cursor.execute("""
        UPDATE transacoes
        SET status = 'aberto',
            data_quitamento = NULL,
            data_alteracao = CURRENT_TIMESTAMP
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (sequencia, user_id))
    conexao.commit()

    # Auditoria: status
    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao='estornada',
        campo_alterado='status',
        valor_antigo=status_anterior,
        valor_novo='aberto'
    )

    # Auditoria: data_quitamento
    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao='estornada',
        campo_alterado='data_quitamento',
        valor_antigo=data_quitamento_anterior or 'null',
        valor_novo='null'
    )

    # Busca atualizada (mesma query da listagem)
    cursor.execute("""
        SELECT t.sequencia_transacoes, t.id, t.tipo, t.valor_total, t.descricao, t.data_emissao,
               c.nome AS categoria_nome, c.cor AS categoria_cor,
               t.status, t.data_vencimento, t.ativo,
               t.numero_parcela, t.total_parcelas, t.transacao_pai_id, t.valor_parcela
        FROM transacoes t
        LEFT JOIN categorias_financas c ON c.id = t.categoria_id
        WHERE t.sequencia_transacoes = %s AND t.user_id = %s
    """, (sequencia, user_id))

    transacao_atualizada = cursor.fetchone()
    conexao.close()

    if not transacao_atualizada:
        return '', 404

    # Formata pro template (reaproveita o formatter da listagem)
    transacao_formatada = FinancasFormatters.formatar_transacoes([transacao_atualizada])[0]

    # Renderiza o partial da linha
    html = render_template(
        'pasta_financas/partials/_linha_transacao.html.jinja',
        transacao=transacao_formatada,
        mostrar_inativas='0',
        data_inicio='', data_fim='', tipo_data='emissao'
    )

    resp = make_response(html)
    resp.headers['HX-Trigger'] = 'transacaoEstornada'
    return resp