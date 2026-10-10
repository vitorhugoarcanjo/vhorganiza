# rotas/pasta_financas/crud/pasta_insert/insert_transacao.py
# ==========================================================
# INSERIR TRANSAÇÃO - VIEW
# ==========================================================

import logging
import json
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from utils.fomatacoes.data_reutilizavel import obter_hoje_cuiaba

from .services import InserirTransacaoService
from .validacoes import validar_dados_insercao, converter_valor_br

logger = logging.getLogger(__name__)


def _fmt_moeda(v):
    """Formata valor pra exibição BR."""
    try:
        return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return str(v)


@login_required
def nova_transacao_modal():
    user_id = session.get('user_id')
    hoje = obter_hoje_cuiaba()

    conexao, cursor = ini_conexao()
    categorias = InserirTransacaoService.buscar_categorias(cursor, usuario_id)

    return render_template(
        'pasta_financas/modais/modal_nova_transacao.html.jinja',
        hoje=hoje,
        categorias=categorias
    )


@login_required
def salvar_nova_transacao():
    user_id = session.get('user_id')
    hoje = obter_hoje_cuiaba()

    conexao, cursor = ini_conexao()

    try:
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

        parcelas = []
        for p in (payload.get('parcelas') or []):
            parcelas.append({
                'numero': int(p.get('numero') or 0),
                'valor': converter_valor_br(p.get('valor')),
                'vencimento': p.get('vencimento'),
            })
        if parcelas:
            dados['parcelas'] = parcelas

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400

        # ==========================================================
        # SIMPLES
        # ==========================================================
        if dados['total_parcelas'] <= 1:
            sucesso, resultado = InserirTransacaoService.criar_transacao_simples(cursor, usuario_id, dados)

            if not sucesso:
                conexao.rollback()
                return jsonify({'success': False, 'error': resultado}), 400

            transacao_id = resultado.get('transacao_id')

            # 🔥 Auditoria — captura TODOS os campos
            alteracoes = [
                {'campo': 'Tipo',         'depois': dados['tipo'].title()},
                {'campo': 'Valor Total',  'depois': _fmt_moeda(dados['valor_total'])},
                {'campo': 'Descrição',    'depois': dados['descricao']},
                {'campo': 'Data Emissão', 'depois': dados['data_emissao']},
                {'campo': 'Vencimento',   'depois': dados['data_vencimento']},
                {'campo': 'Parcelas',     'depois': '1x (à vista)'},
            ]

            AuditoriaFinanceiraService.registrar(
                transacao_id=transacao_id,
                acao='criada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

            conexao.commit()

            return jsonify({
                'success': True,
                'message': f'Transação "{dados["descricao"]}" cadastrada com sucesso!',
                'sequencia': resultado.get('sequencia'),
                'transacao_id': transacao_id
            }), 201

        # ==========================================================
        # PARCELADA
        # ==========================================================
        else:
            sucesso, resultado = InserirTransacaoService.criar_transacao_parcelada(cursor, usuario_id, dados)

            if not sucesso:
                conexao.rollback()
                return jsonify({'success': False, 'error': resultado}), 400

            pai_id = resultado.get('pai_id')
            total_parcelas = resultado.get('total_parcelas', dados['total_parcelas'])

            # 🔥 Auditoria — captura TODOS os campos
            alteracoes = [
                {'campo': 'Tipo',        'depois': dados['tipo'].title()},
                {'campo': 'Valor Total', 'depois': _fmt_moeda(dados['valor_total'])},
                {'campo': 'Descrição',   'depois': dados['descricao']},
                {'campo': 'Data Emissão','depois': dados['data_emissao']},
                {'campo': 'Parcelas',    'depois': f'{total_parcelas}x'},
                {'campo': 'Intervalo',   'depois': f'{dados["intervalo_dias"]} dias'},
            ]

            AuditoriaFinanceiraService.registrar(
                transacao_id=pai_id,
                acao='criada_parcelada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

            conexao.commit()

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