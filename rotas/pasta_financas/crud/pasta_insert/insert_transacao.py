import traceback
from datetime import date
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from .services import InserirTransacaoService
from .validacoes import validar_dados_insercao, converter_valor_br

# ========================================================== #
# 1. GET - RETORNA O HTML DO MODAL
# ========================================================== #
@login_required
def nova_transacao_modal():
    """Retorna o HTML do modal de nova transação"""
    user_id = session.get('user_id')
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
    categorias = InserirTransacaoService.buscar_categorias(cursor, user_id)
    
    return render_template(
        'pasta_financas/modais/modal_nova_transacao.html.jinja',
        hoje=hoje,
        categorias=categorias
    )

# ========================================================== #
# 2. POST - SALVA A TRANSAÇÃO VIA AJAX
# ========================================================== #
@login_required
def salvar_nova_transacao():
    """Salva a nova transação e retorna JSON"""
    user_id = session.get('user_id')
    hoje = date.today().isoformat()
    
    # Obtém conexão e cursor atrelados ao contexto atual (g)
    conexao, cursor = ini_conexao()
    
    try:
        # Extrai e limpa dados do FORM
        dados = {
            'tipo': request.form.get('tipo'),
            'valor_total': converter_valor_br(request.form.get('valor_total')),
            'descricao': request.form.get('descricao', '').strip(),
            'data_emissao': request.form.get('data_emissao') or hoje,
            'data_vencimento': request.form.get('data_vencimento') or hoje,
            'categoria_id': request.form.get('categoria_id') or None,
            'total_parcelas': int(request.form.get('total_parcelas') or 1),
            'intervalo_dias': int(request.form.get('intervaloDias') or 30),
            'primeiro_vencimento': request.form.get('primeiroVencimento') or request.form.get('data_vencimento') or hoje,
        }
        
        # Coleta parcelas dinâmicas se houver
        parcelas = []
        for i in range(1, dados['total_parcelas'] + 1):
            valor = request.form.get(f'parcela_valor_{i}')
            if valor:
                parcelas.append(converter_valor_br(valor))
        if parcelas:
            dados['valores_parcelas'] = parcelas
        
        # Executa validações
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400
        
        if dados['total_parcelas'] <= 1:
            sequencia = InserirTransacaoService.criar_transacao_simples(cursor, user_id, dados)
            conexao.commit()
            InserirTransacaoService.registrar_auditoria(sequencia, dados['descricao'])
            
            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada com sucesso!',
                'sequencia': sequencia
            }), 201
        else:
            sequencia_pai, total_parcelas = InserirTransacaoService.criar_transacao_parcelada(
                cursor, user_id, dados
            )
            conexao.commit()
            InserirTransacaoService.registrar_auditoria(
                sequencia_pai, dados['descricao'], total_parcelas
            )
            
            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada em {total_parcelas}x com sucesso!',
                'sequencia': sequencia_pai,
                'total_parcelas': total_parcelas
            }), 201
            
    except Exception as e:
        conexao.rollback()  # Garante rollback se der erro na gravação
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': 'Erro interno no servidor ao salvar a transação.',
            'details': str(e)
        }), 500