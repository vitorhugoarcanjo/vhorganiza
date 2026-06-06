from flask import Blueprint, jsonify, session
import sqlite3
import os
from datetime import date
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.middleware.autenticacao import login_required

bp_estornar = Blueprint('estornar_transacao', __name__)

@bp_estornar.route('/<int:sequencia>', methods=['POST'])
@login_required
def iniestornar(sequencia):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    
    conexao, cursor = ini_conexao()
        
    # Busca dados ANTES do estorno
    cursor.execute("""
        SELECT descricao, status, tipo, data_quitamento 
        FROM transacoes 
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (sequencia, user_id))
    
    transacao = cursor.fetchone()
    
    if not transacao:
        return jsonify({'success': False, 'error': 'Transação não encontrada'})
    
    # Verifica se a transação está quitada/recebida
    if transacao[1] not in ['quitado', 'recebido']:
        return jsonify({'success': False, 'error': 'Esta transação já está aberta'})
    
    # Define a ação para auditoria
    acao = 'estornada'
    status_anterior = transacao[1]
    
    # Estorna: volta para status 'aberto' e limpa data_quitamento
    cursor.execute("""
        UPDATE transacoes 
        SET status = 'aberto', 
            data_quitamento = NULL,
            data_alteracao = CURRENT_TIMESTAMP
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (sequencia, user_id))
    
    conexao.commit()
    
    # Registra auditoria
    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao=acao,
        campo_alterado='status',
        valor_antigo=status_anterior,
        valor_novo='aberto'
    )
    
    # Registra também a limpeza da data
    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao=acao,
        campo_alterado='data_quitamento',
        valor_antigo=transacao[3] if transacao[3] else 'null',
        valor_novo='null'
    )
    
    return jsonify({'success': True, 'message': f'Transação "{transacao[0]}" estornada com sucesso!'})