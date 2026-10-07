# rotas/pasta_orcamentos/crud/pasta_dados/dados.py
# ==========================================================
# DADOS DO ORÇAMENTO (para o modal de edição)
# ==========================================================

import logging
from flask import jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

logger = logging.getLogger(__name__)


@login_required
def get_dados_orcamento(sequencia):
    """Busca dados do orçamento pra popular o modal de edição."""
    user_id = session['user_id']

    try:
        conexao, cursor = ini_conexao()

        cursor.execute("""
            SELECT id, sequencia_orcamentos, numero,
                   titulo, cliente, status, estrutura,
                   valor_total, data_emissao, data_validade, data_entrega,
                   created_at
            FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, user_id))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                'success': False,
                'message': 'Orçamento não encontrado'
            }), 404

        return jsonify({
            'success':              True,
            'id':                   row[0],
            'sequencia_orcamentos': row[1],
            'numero':               row[2] or '',
            'titulo':               row[3] or '',
            'cliente':              row[4] or '',
            'status':               row[5] or 'rascunho',
            'estrutura':            row[6] if row[6] else [],
            'valor_total':          float(row[7] or 0),
            'data_emissao':         str(row[8]) if row[8] else '',
            'data_validade':        str(row[9]) if row[9] else '',
            'data_entrega':         str(row[10]) if row[10] else '',
            'created_at':           row[11].strftime('%Y-%m-%d') if row[11] else '',
        })

    except Exception as e:
        logger.exception(f"Erro ao buscar dados do orçamento seq={sequencia}")
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar dados: {str(e)}'
        }), 500