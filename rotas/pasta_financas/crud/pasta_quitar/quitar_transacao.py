# rotas/pasta_financas/crud/pasta_quitar/quitar_transacao.py
from flask import session, make_response, render_template
from datetime import date
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters


@login_required
def quitar_transacao_view(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()

    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT descricao, status, tipo
        FROM transacoes
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (sequencia, user_id))

    transacao = cursor.fetchone()
    if not transacao:
        return '', 404

    if transacao[2] == 'receita':
        novo_status = 'recebido'
        acao = 'recebida'
    else:
        novo_status = 'quitado'
        acao = 'quitada'

    cursor.execute("""
        UPDATE transacoes
        SET status = %s, data_quitamento = %s
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (novo_status, hoje, sequencia, user_id))
    conexao.commit()

    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao=acao,
        campo_alterado='status',
        valor_antigo=transacao[1],
        valor_novo=novo_status
    )

    # Busca atualizada
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

    transacao_formatada = FinancasFormatters.formatar_transacoes([transacao_atualizada])[0]

    html = render_template(
        'pasta_financas/partials/_linha_transacao.html.jinja',
        transacao=transacao_formatada,
        mostrar_inativas='0',
        data_inicio='', data_fim='', tipo_data='emissao'
    )

    resp = make_response(html)
    resp.headers['HX-Trigger'] = 'transacaoQuitada'
    return resp