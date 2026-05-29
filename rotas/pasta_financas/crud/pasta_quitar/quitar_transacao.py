from flask import Blueprint, redirect, url_for, session, flash, request, jsonify
import sqlite3
import os
from datetime import date
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_quitar = Blueprint('quitar_transacao', __name__)

@bp_quitar.route('/<int:sequencia>', methods=['POST'])  # 👈 Adiciona POST
def iniquitacao(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()
        
        # Busca dados ANTES
        cursor.execute("""
            SELECT descricao, status, tipo 
            FROM transacoes 
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (sequencia, user_id))
        
        transacao = cursor.fetchone()
        
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'})
        
        # Define novo status baseado no tipo
        if transacao[2] == 'receita':
            novo_status = 'recebido'
            acao = 'recebida'
        else:
            novo_status = 'quitado'
            acao = 'quitada'
        
        # Update
        cursor.execute("""
            UPDATE transacoes 
            SET status = ?, 
                data_quitamento = ? 
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (novo_status, hoje, sequencia, user_id))
        conn.commit()
        
        # Auditoria
        AuditoriaFinanceiraService.registrar(
            transacao_id=sequencia,
            acao=acao,
            campo_alterado='status',
            valor_antigo=transacao[1],
            valor_novo=novo_status
        )

    return jsonify({'success': True})