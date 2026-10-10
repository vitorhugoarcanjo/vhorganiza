# rotas/pasta_financas/crud/pasta_quitar/quitar_transacao.py
from flask import session, make_response, render_template
from datetime import date

from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters


@login_required
def quitar_transacao_view(sequencia):
    usuario_id = session['user_id']
    hoje = date.today().isoformat()

    conexao, cursor = ini_conexao()

    # 🔥 Busca a transação + o pai (se for filha)
    cursor.execute("""
        SELECT id, descricao, status, tipo, transacao_pai_id
        FROM transacoes
        WHERE sequencia_transacoes = %s AND usuario_id = %s
    """, (sequencia, usuario_id))

    transacao = cursor.fetchone()
    if not transacao:
        conexao.close()
        return '', 404

    id_interno = transacao[0]
    status_antes = transacao[2]
    transacao_pai_id = transacao[4]

    # 🔥 Se for FILHA, usa o ID do PAI pra auditoria
    if transacao_pai_id:
        auditoria_id = transacao_pai_id
    else:
        auditoria_id = id_interno

    if transacao[3] == 'receita':
        novo_status = 'recebido'
        acao = 'recebida'
    else:
        novo_status = 'quitado'
        acao = 'quitada'

    cursor.execute("""
        UPDATE transacoes
        SET status = %s, data_quitamento = %s
        WHERE id = %s AND usuario_id = %s
    """, (novo_status, hoje, id_interno, usuario_id))

    # 🔥 Auditoria com ID do PAI (se for parcelada) ou da própria (se simples)
    AuditoriaFinanceiraService.registrar(
        transacao_id=auditoria_id,
        acao=acao,
        campo_alterado='status',
        valor_antigo=status_antes,
        valor_novo=novo_status,
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
        WHERE t.sequencia_transacoes = %s AND t.usuario_id = %s
    """, (sequencia, usuario_id))

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