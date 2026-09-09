# ==========================================================
# INSERIR TRANSAÇÃO - FUNÇÕES (view_funcs)
# ==========================================================

from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from datetime import date
from utils.database.conexao_global import ini_conexao
from .services import InserirTransacaoService
from .validacoes import validar_dados_insercao, converter_valor_br

# ========================================================== #
# 1. GET - RETORNA O MODAL
# ========================================================== #
@login_required
def nova_transacao_modal():
    """Retorna o HTML do modal de nova transação"""
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
    categorias = InserirTransacaoService.buscar_categorias(cursor, user_id)
    conexao.close()
    
    # 🔥 ADICIONA ESTES LOGS
    print(f"🔍 User ID: {user_id}")
    print(f"📦 Categorias encontradas: {categorias}")
    print(f"📦 Total de categorias: {len(categorias)}")
    
    return render_template(
        'pasta_financas/modais/modal_nova_transacao.html.jinja',
        hoje=hoje,
        categorias=categorias
    )

# ========================================================== #
# 2. POST - SALVA A TRANSAÇÃO
# ========================================================== #
@login_required
def salvar_nova_transacao():
    """Salva a nova transação"""
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    try:
        # 🔥 EXTRAI DADOS DO FORM
        dados = {
            'tipo': request.form.get('tipo'),
            'valor_total': converter_valor_br(request.form.get('valor_total')),
            'descricao': request.form.get('descricao', '').strip(),
            'data_emissao': request.form.get('data_emissao', hoje),
            'data_vencimento': request.form.get('data_vencimento'),
            'categoria_id': request.form.get('categoria_id') or None,
            'total_parcelas': int(request.form.get('total_parcelas', 1)),
            'intervalo_dias': int(request.form.get('intervaloDias', 30)),
            'primeiro_vencimento': request.form.get('primeiroVencimento'),
        }
        
        # 🔥 COLETA OS VALORES DAS PARCELAS (SE HOUVER)
        parcelas = []
        for i in range(1, dados['total_parcelas'] + 1):
            valor = request.form.get(f'parcela_valor_{i}')
            if valor:
                parcelas.append(converter_valor_br(valor))
        if parcelas:
            dados['valores_parcelas'] = parcelas
        
        # 🔥 VALIDA
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400
        
        # 🔥 SALVA
        conexao, cursor = ini_conexao()
        
        if dados['total_parcelas'] <= 1:
            sequencia = InserirTransacaoService.criar_transacao_simples(cursor, user_id, dados)
            conexao.commit()
            InserirTransacaoService.registrar_auditoria(sequencia, dados['descricao'])
            
            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada com sucesso!',
                'sequencia': sequencia
            })
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
                'message': f'Transação "{dados["descricao"]}" cadastrada com {total_parcelas} parcelas!',
                'sequencia': sequencia_pai,
                'total_parcelas': total_parcelas
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500