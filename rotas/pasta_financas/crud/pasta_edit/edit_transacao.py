# ==========================================================
# EDITAR TRANSAÇÃO - FUNÇÕES (view_funcs)
# ==========================================================

from flask import request, session, jsonify, render_template, redirect, url_for
from rotas.middleware.autenticacao import login_required
from datetime import date, datetime
from utils.database.conexao_global import ini_conexao
from .services import EditarTransacaoService
from .validacoes import validar_dados_edicao, converter_valor_br


def _formatar_data_iso(valor):
    """Auxiliar para converter date/datetime em string 'YYYY-MM-DD' sem explodir se já for str"""
    if not valor:
        return ''
    if isinstance(valor, (date, datetime)):
        return valor.strftime('%Y-%m-%d')
    return str(valor)[:10]


# ========================================================== #
# 1. GET - RETORNA O MODAL COM DADOS
# ========================================================== #
@login_required
def editar_modal(sequencia):
    """Só renderiza o esqueleto do modal. Os dados vêm via /dados/<seq>."""
    user_id = session['user_id']
    hoje = date.today().isoformat()

    conexao, cursor = ini_conexao()
    try:
        # Categorias são necessárias pra montar o <select> no HTML
        categorias = EditarTransacaoService.buscar_categorias(cursor, user_id) \
                     if hasattr(EditarTransacaoService, 'buscar_categorias') else []

        return render_template(
            'pasta_financas/modais/modal_editar_transacao.html.jinja',
            categorias=categorias,
            sequencia=sequencia,
            hoje=hoje,
        )
    finally:
        conexao.close()


# ========================================================== #
# 2. GET - RETORNA OS DADOS EM JSON
# ========================================================== #
@login_required
def dados_json(sequencia):
    """Retorna os dados da transação em JSON"""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        transacao, pai_id = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, user_id)
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404

        parcelas_raw = EditarTransacaoService.buscar_parcelas_filhas(cursor, pai_id)

        return jsonify({
            'success': True,
            'data': {
                'id': transacao[0],
                'sequencia': sequencia,   # 🔥 FIX: antes era transacao[1] (None no pai)
                'tipo': transacao[2],
                'descricao': transacao[3] or '',
                'valor_total': float(transacao[4]) if transacao[4] else 0.0,
                'data_vencimento': _formatar_data_iso(transacao[5]),
                'categoria_id': transacao[6],
                'status': transacao[7],
                'numero_parcelas': transacao[8] or 1,
                'total_parcelas': transacao[9] or 1,
                'transacao_pai_id': transacao[10],
                'parcelas': [
                    {
                        'id': p[0],
                        'sequencia': p[1],
                        'numero_parcela': p[2],
                        'valor': float(p[3]) if p[3] else 0.0,
                        'data_vencimento': _formatar_data_iso(p[4]),
                        'status': p[5],
                        'descricao': p[6]
                    } for p in parcelas_raw
                ]
            }
        })
    finally:
        conexao.close()


# ========================================================== #
# 3. POST - SALVA A EDIÇÃO
# ========================================================== #
@login_required
def salvar_edicao(sequencia):
    """Salva a edição da transação"""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        dados = request.json or {}

        if dados.get('valor_total'):
            dados['valor_total'] = converter_valor_br(str(dados.get('valor_total')))
        else:
            dados['valor_total'] = 0.0

        dados['intervaloDias'] = dados.get('intervaloDias') or dados.get('intervalo_dias', 30)
        dados['primeiroVencimento'] = (
            dados.get('primeiroVencimento')
            or dados.get('primeiro_vencimento')
            or dados.get('data_vencimento')
        )

        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400

        resultado = EditarTransacaoService.atualizar_transacao(
            cursor, conexao, sequencia, user_id, dados
        )

        if not resultado.get('success'):
            return jsonify({'success': False, 'error': resultado.get('error')}), 400

        conexao.commit()

        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso!'
        })

    except Exception as e:
        conexao.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()