from flask import Blueprint, jsonify, session
import sqlite3
import os
from rotas.middleware.autenticacao import login_required
from utils.fomatacoes.data_reutilizavel import formatar_data_br

bp_vinculos = Blueprint('api_vinculos', __name__)
caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')


@bp_vinculos.route('/vinculos/<int:sequencia>', methods=['GET'])
@login_required
def buscar_vinculos(sequencia):
    user_id = session.get('user_id')
    
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()
        
        # Busca a transação
        cursor.execute("""
            SELECT sequencia_transacoes, transacao_pai_id, total_parcelas, 
                   numero_parcela, tipo, descricao
            FROM transacoes 
            WHERE sequencia_transacoes = ? AND user_id = ? AND ativo = 1
        """, (sequencia, user_id))
        
        transacao = cursor.fetchone()
        
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        sequencia_atual, transacao_pai_id, total_parcelas, numero_parcela, tipo, descricao = transacao
        
        vinculos = []
        
        # Caso 1: É uma parcela (tem pai) - busca todas parcelas do mesmo pai
        if transacao_pai_id:
            cursor.execute("""
                SELECT sequencia_transacoes, numero_parcela, total_parcelas, 
                       valor_parcela, data_vencimento, status
                FROM transacoes
                WHERE transacao_pai_id = ? AND user_id = ? AND ativo = 1
                ORDER BY numero_parcela
            """, (transacao_pai_id, user_id))
            
            for row in cursor.fetchall():
                vinculos.append({
                    'sequencia': row[0],
                    'numero_parcela': row[1],
                    'total_parcelas': row[2],
                    'valor': row[3] if row[3] else 0,
                    'data_vencimento': formatar_data_br(row[4]) if row[4] else '—',
                    'status': row[5]  # 🔥 ADICIONADO
                })
        
        # Caso 2: É uma transação PAI (tem parcelas filhas)
        elif total_parcelas > 1 and not transacao_pai_id:
            cursor.execute("""
                SELECT sequencia_transacoes, numero_parcela, total_parcelas, 
                       valor_parcela, data_vencimento, status
                FROM transacoes
                WHERE transacao_pai_id = ? AND user_id = ? AND ativo = 1
                ORDER BY numero_parcela
            """, (sequencia, user_id))
            
            for row in cursor.fetchall():
                vinculos.append({
                    'sequencia': row[0],
                    'numero_parcela': row[1],
                    'total_parcelas': row[2],
                    'valor': row[3] if row[3] else 0,
                    'data_vencimento': formatar_data_br(row[4]) if row[4] else '—',
                    'status': row[5]  # 🔥 ADICIONADO
                })
        
        return jsonify({
            'success': True,
            'vinculos': vinculos,
            'tipo': tipo,
            'descricao': descricao,
            'total': len(vinculos)
        })