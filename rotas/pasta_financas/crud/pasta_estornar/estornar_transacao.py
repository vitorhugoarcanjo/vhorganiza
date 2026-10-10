# rotas/pasta_financas/crud/pasta_estornar/estornar_transacao.py
import json
from flask import session, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters


@login_required
def estornar_transacao_view(sequencia):
    usuario_id = session.get('user_id')
    if not usuario_id:
        return '', 401

    conexao, cursor = ini_conexao()

    # 🔥 Busca + pai (se for filha)
    cursor.execute("""
        SELECT id, descricao, status, tipo, data_quitamento, transacao_pai_id
        FROM transacoes
        WHERE sequencia_transacoes = %s AND usuario_id = %s
    """, (sequencia, usuario_id))

    transacao = cursor.fetchone()
    if not transacao:
        conexao.close()
        return '', 404

    id_interno = transacao[0]
    status_anterior = transacao[2]
    data_quitamento_anterior = transacao[4]
    transacao_pai_id = transacao[5]

    # 🔥 Se for FILHA, usa o ID do PAI
    auditoria_id = transacao_pai_id if transacao_pai_id else id_interno

    if status_anterior not in ['quitado', 'recebido']:
        conexao.close()
        return '', 400

    cursor.execute("""
        UPDATE transacoes
        SET status = 'aberto',
            data_quitamento = NULL,
            data_alteracao = CURRENT_TIMESTAMP
        WHERE id = %s AND usuario_id = %s
    """, (id_interno, usuario_id))

    # 🔥 Auditoria CONSOLIDADA
    alteracoes = [
        {
            'campo': 'Status',
            'antes': status_anterior,
            'depois': 'aberto',
        },
        {
            'campo': 'Data Quitamento',
            'antes': str(data_quitamento_anterior) if data_quitamento_anterior else '(vazio)',
            'depois': '(vazio)',
        },
    ]

    AuditoriaFinanceiraService.registrar(
        transacao_id=auditoria_id,   # 🔥 ID do PAI (se filha) ou próprio
        acao='estornada',
        campo_alterado='multiplos',
        valor_antigo=None,
        valor_novo=json.dumps(alteracoes, ensure_ascii=False),
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
        LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'financas'
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
    resp.headers['HX-Trigger'] = 'transacaoEstornada'
    return resp