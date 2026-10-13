# rotas/pasta_financas/crud/pasta_quitar/quitar_transacao.py
# ==========================================================
# QUITAR/RECEBER TRANSAÇÃO
# Aceita data_quitamento do form (fallback: hoje)
# ==========================================================

from flask import session, make_response, render_template, request
from datetime import date
from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br

from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.pasta_financas.formatters import FinancasFormatters


# ==========================================================
# GET — RETORNA O HTML DO MODAL
# ==========================================================
@login_required
def quitar_modal_view(sequencia):
    """Renderiza o modal de quitar com os dados da transação"""
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        cursor.execute("""
            SELECT t.sequencia_transacoes, t.descricao, t.tipo,
                   t.valor_total, t.valor_parcela, t.data_vencimento,
                   t.transacao_pai_id
            FROM transacoes t
            WHERE t.sequencia_transacoes = %s AND t.usuario_id = %s
        """, (sequencia, usuario_id))

        transacao = cursor.fetchone()
        if not transacao:
            return '', 404

        valor_raw = float(transacao[4]) if transacao[5] else float(transacao[3])
        # Monta dict pro template
        dados = {
            'sequencia':                  transacao[0],
            'descricao':                  transacao[1],
            'tipo':                       transacao[2],
            'valor_formatado':            formatar_moeda_br(valor_raw),                              # 🔥
            'data_vencimento_original':   formatar_data_br(transacao[5]) if transacao[5] else '(vazio)',  # 🔥
        }

        return render_template(
            'pasta_financas/modais/modal_quitar_transacao.html.jinja',
            transacao=dados,
            hoje=date.today().isoformat(),
        )
    finally:
        conexao.close()


# ==========================================================
# POST — QUITA A TRANSAÇÃO
# ==========================================================
@login_required
def quitar_transacao_view(sequencia):
    usuario_id = session['user_id']

    # 🔥 Data vem do form (fallback: hoje)
    data_quitamento = (request.form.get('data_quitamento') or '').strip()
    if not data_quitamento:
        data_quitamento = date.today().isoformat()

    conexao, cursor = ini_conexao()

    try:
        # Busca a transação + o pai (se for filha)
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

        # Se for FILHA, usa o ID do PAI pra auditoria
        auditoria_id = transacao_pai_id if transacao_pai_id else id_interno

        # Define status final
        if transacao[3] == 'receita':
            novo_status = 'recebido'
            acao = 'recebida'
        else:
            novo_status = 'quitado'
            acao = 'quitada'

        # UPDATE com a data escolhida
        cursor.execute("""
            UPDATE transacoes
            SET status = %s,
                data_quitamento = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s
        """, (novo_status, data_quitamento, id_interno, usuario_id))

        # Auditoria com data ANTES/DEPOIS
        alteracoes = [
            {'campo': 'Status',           'antes': status_antes, 'depois': novo_status},
            {'campo': 'Data Quitamento',  'antes': '(vazio)',     'depois': data_quitamento},
        ]

        AuditoriaFinanceiraService.registrar(
            transacao_id=auditoria_id,
            acao=acao,
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=__import__('json').dumps(alteracoes, ensure_ascii=False),
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
        resp.headers['HX-Trigger'] = 'transacaoQuitada'
        return resp

    except Exception as e:
        conexao.rollback()
        print(f"Erro ao quitar: {e}")
        conexao.close()
        return '', 500