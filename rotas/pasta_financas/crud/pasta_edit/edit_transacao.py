# ==========================================================
# EDITAR TRANSAÇÃO - FUNÇÕES (view_funcs) - Corrigido
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
    """Retorna o HTML do modal de edição com dados preenchidos"""
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
    try:
        # 🔥 BUSCA A TRANSAÇÃO OU O PAI (Retorna os dados do pai e o id interno do pai)
        transacao, sequencia_usar = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, user_id)
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        # 🔥 BUSCA AS PARCELAS DO PAI USANDO O MÉTODO CORRETO
        parcelas_raw = EditarTransacaoService.buscar_parcelas_filhas(cursor, sequencia_usar)
        
        # 🔥 FORMATA OS DADOS
        dados = EditarTransacaoService.formatar_transacao_para_modal(transacao, parcelas_raw)
        
        # 🔥 BUSCA CATEGORIAS
        categorias = EditarTransacaoService.buscar_categorias(cursor, user_id)
        
        return render_template(
            'pasta_financas/modais/modal_editar_transacao.html.jinja',
            transacao=dados['transacao'],
            categorias=categorias,
            sequencia=sequencia_usar,
            total_parcelas=dados['total_parcelas'],
            parcelas_filhas=dados['parcelas'],
            parcelas_filhas_json=dados['parcelas_json'],
            hoje=hoje
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
        transacao, sequencia_usar = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, user_id)
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        parcelas_raw = EditarTransacaoService.buscar_parcelas_filhas(cursor, sequencia_usar)
        
        # Nova estrutura da tupla transacao (com id na posição 0):
        # 0: id, 1: sequencia_transacoes, 2: tipo, 3: valor_total, 4: descricao, 
        # 5: data_emissao, 6: categoria_id, 7: cat_nome, 8: cat_cor, 
        # 9: data_vencimento, 10: total_parcelas, 11: intervalo_dias, 12: pai_id, 13: num_parcela
        return jsonify({
            'success': True,
            'data': {
                'sequencia': transacao[1],
                'tipo': transacao[2],
                'valor_total': float(transacao[3]) if transacao[3] else 0.0,
                'descricao': transacao[4] or '',
                'data_emissao': _formatar_data_iso(transacao[5]),
                'data_vencimento': _formatar_data_iso(transacao[9]),
                'categoria_id': transacao[6],
                'total_parcelas': transacao[10] or 1,
                'intervalo_dias': transacao[11] or 30,
                'parcelas': [
                    {
                        'sequencia': p[0],
                        'numero': p[1],
                        'data_vencimento': _formatar_data_iso(p[2]),
                        'valor': float(p[3]) if p[3] else 0.0,
                        'id': p[4]
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