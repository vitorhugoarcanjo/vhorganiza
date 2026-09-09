# ==========================================================
# EDITAR TRANSAÇÃO - FUNÇÕES (view_funcs)
# ==========================================================

from flask import request, session, jsonify, render_template, redirect, url_for
from rotas.middleware.autenticacao import login_required
from datetime import date
from utils.database.conexao_global import ini_conexao
from .services import EditarTransacaoService
from .validacoes import validar_dados_edicao, converter_valor_br

# ========================================================== #
# 1. GET - RETORNA O MODAL COM DADOS
# ========================================================== #
@login_required
def editar_modal(sequencia):
    """Retorna o HTML do modal de edição com dados preenchidos"""
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
    
    # 🔥 BUSCA A TRANSAÇÃO (SE FOR PARCELA, BUSCA O PAI)
    transacao, sequencia_usar = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, user_id)
    if not transacao:
        conexao.close()
        return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
    
    # 🔥 BUSCA AS PARCELAS DO PAI
    parcelas_raw = EditarTransacaoService.buscar_parcelas(cursor, sequencia_usar)
    
    # 🔥 FORMATA OS DADOS
    dados = EditarTransacaoService.formatar_transacao_para_modal(transacao, parcelas_raw)
    
    # 🔥 BUSCA CATEGORIAS
    categorias = EditarTransacaoService.buscar_categorias(cursor, user_id)
    
    conexao.close()
    
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

# ========================================================== #
# 2. GET - RETORNA OS DADOS EM JSON
# ========================================================== #
@login_required
def dados_json(sequencia):
    """Retorna os dados da transação em JSON"""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    
    # 🔥 BUSCA A TRANSAÇÃO (SE FOR PARCELA, BUSCA O PAI)
    transacao, sequencia_usar = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, user_id)
    if not transacao:
        conexao.close()
        return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
    
    # 🔥 BUSCA AS PARCELAS DO PAI
    parcelas_raw = EditarTransacaoService.buscar_parcelas(cursor, sequencia_usar)
    
    conexao.close()
    
    return jsonify({
        'success': True,
        'data': {
            'sequencia': transacao[0],
            'tipo': transacao[1],
            'valor_total': float(transacao[2]) if transacao[2] else 0.0,
            'descricao': transacao[3] or '',
            'data_emissao': transacao[4].strftime('%Y-%m-%d') if transacao[4] else '',
            'data_vencimento': transacao[8].strftime('%Y-%m-%d') if transacao[8] else '',
            'categoria_id': transacao[5],
            'total_parcelas': transacao[9] or 1,
            'intervalo_dias': transacao[10] or 30,
            'parcelas': [
                {
                    'numero': p[1],
                    'data_vencimento': p[2].strftime('%Y-%m-%d') if p[2] else '',
                    'valor': float(p[3]) if p[3] else 0.0
                } for p in parcelas_raw
            ]
        }
    })

# ========================================================== #
# 3. POST - SALVA A EDIÇÃO
# ========================================================== #
@login_required
def salvar_edicao(sequencia):
    """Salva a edição da transação"""
    user_id = session['user_id']
    
    try:
        dados = request.json or {}
        
        if dados.get('valor_total'):
            dados['valor_total'] = converter_valor_br(str(dados.get('valor_total')))
        else:
            dados['valor_total'] = 0.0
        
        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400
        
        conexao, cursor = ini_conexao()
        
        resultado = EditarTransacaoService.atualizar_transacao(
            cursor, conexao, sequencia, user_id, dados
        )
        
        if not resultado['success']:
            conexao.close()
            return jsonify({'success': False, 'error': resultado.get('error')}), 400
        
        # 🔥 AUDITORIA (opcional)
        # _registrar_auditoria(cursor, sequencia, resultado)
        
        conexao.commit()
        conexao.close()
        
        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso!'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500