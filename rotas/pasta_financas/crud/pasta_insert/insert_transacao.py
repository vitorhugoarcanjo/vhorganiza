# rotas\pasta_financas\crud\pasta_insert\insert_transacao.py

import logging
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

# IMPORTAÇÃO CENTRALIZADA (Remove o fuso redundante criado com timedelta)
from utils.fomatacoes.data_reutilizavel import obter_hoje_cuiaba

from .services import InserirTransacaoService
from .validacoes import validar_dados_insercao, converter_valor_br

logger = logging.getLogger(__name__)

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
        payload = request.json or {}

        dados = {
            'tipo': payload.get('tipo'),
            'valor_total': converter_valor_br(payload.get('valor_total')),
            'descricao': (payload.get('descricao') or '').strip(),
            'data_emissao': payload.get('data_emissao') or hoje,
            'data_vencimento': payload.get('data_vencimento') or hoje,
            'categoria_id': payload.get('categoria_id') or None,
            'total_parcelas': int(payload.get('total_parcelas') or 1),
            'intervalo_dias': int(payload.get('intervaloDias') or 30),
            'primeiro_vencimento': payload.get('primeiroVencimento') or payload.get('data_vencimento') or hoje,
        }

        # 🔥 MUDANÇA GRANDE: agora as parcelas JÁ VÊM COMO ARRAY do front
        parcelas = []
        for p in (payload.get('parcelas') or []):
            parcelas.append({
                'numero': int(p.get('numero') or 0),
                'valor': converter_valor_br(p.get('valor')),
                'vencimento': p.get('vencimento'),
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
        logger.exception(f"Erro ao salvar nova transação user_id={user_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao salvar a transação.',
            'details': str(e)
        }), 500