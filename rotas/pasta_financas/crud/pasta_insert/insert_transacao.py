import traceback
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

# IMPORTAÇÃO CENTRALIZADA (Remove o fuso redundante criado com timedelta)
from utils.fomatacoes.data_reutilizavel import obter_hoje_cuiaba

from .services import InserirTransacaoService
from .validacoes import validar_dados_insercao, converter_valor_br


# ========================================================== #
# 1. GET - RETORNA O HTML DO MODAL
# ========================================================== #
@login_required
def nova_transacao_modal():
    """Retorna o HTML do modal de nova transação"""
    user_id = session.get('user_id')
    hoje = obter_hoje_cuiaba()

    # O Flask/g gerencia a abertura e o fechamento no teardown
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
    hoje = obter_hoje_cuiaba()

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

        # 🔥 Coleta parcelas com VALOR e VENCIMENTO individuais
        parcelas = []
        for i in range(1, dados['total_parcelas'] + 1):
            valor = request.form.get(f'parcela_valor_{i}')
            vencimento = request.form.get(f'parcela_vencimento_{i}')
            if valor:
                parcelas.append({
                    'numero': i,
                    'valor': converter_valor_br(valor),
                    'vencimento': vencimento,
                })
        if parcelas:
            dados['parcelas'] = parcelas

        # Executa validações de formulário
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400

        # Processamento conforme o número de parcelas
        if dados['total_parcelas'] <= 1:
            sucesso, resultado = InserirTransacaoService.criar_transacao_simples(cursor, user_id, dados)

            if not sucesso:
                conexao.rollback()
                return jsonify({'success': False, 'error': resultado}), 400

            conexao.commit()

            transacao_id = resultado.get('transacao_id')
            InserirTransacaoService.registrar_auditoria(transacao_id, dados['descricao'])

            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada com sucesso!',
                'sequencia': resultado.get('sequencia'),
                'transacao_id': transacao_id
            }), 201

        else:
            sucesso, resultado = InserirTransacaoService.criar_transacao_parcelada(cursor, user_id, dados)

            if not sucesso:
                conexao.rollback()
                return jsonify({'success': False, 'error': resultado}), 400

            conexao.commit()

            pai_id = resultado.get('pai_id')
            total_parcelas = resultado.get('total_parcelas', dados['total_parcelas'])

            InserirTransacaoService.registrar_auditoria(pai_id, dados['descricao'], total_parcelas)

            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada em {total_parcelas}x com sucesso!',
                'sequencia': resultado.get('sequencia_pai'),
                'pai_id': pai_id,
                'total_parcelas': total_parcelas
            }), 201

    except Exception as e:
        conexao.rollback()
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao salvar a transação.',
            'details': str(e)
        }), 500