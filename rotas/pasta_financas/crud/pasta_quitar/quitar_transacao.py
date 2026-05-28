from flask import Blueprint, redirect, url_for, session, flash, request, jsonify
import sqlite3
import os
from datetime import date
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_quitar = Blueprint('quitar_transacao', __name__)

@bp_quitar.route('/<int:sequencia>')
def iniquitacao(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()
        
        # 🔥 Busca dados ANTES de quitar (pra auditoria)
        cursor.execute("""
            SELECT descricao, status 
            FROM transacoes 
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (sequencia, user_id))
        
        transacao = cursor.fetchone()
        
        if not transacao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Transação não encontrada'})

        # Faz o UPDATE
        cursor.execute("""
            UPDATE transacoes 
            SET status = 'quitado', 
                data_quitamento = ? 
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (hoje, sequencia, user_id))
        conn.commit()
        
        # 🔥 REGISTRA AUDITORIA
        status_map = {
            'aberto': '🔴 Aberto', 
            'quitado': '✅ Quitado', 
            'recebido': '💰 Recebido'
        }
        
        AuditoriaFinanceiraService.registrar(
            transacao_id=sequencia,
            acao='quitada',
            campo_alterado='status',
            valor_antigo=status_map.get(transacao[1], transacao[1]),
            valor_novo='✅ Quitado'
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
