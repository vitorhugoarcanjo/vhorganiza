from flask import Blueprint, redirect, url_for, session, flash, request, jsonify
from datetime import date
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao
from rotas.middleware.autenticacao import login_required

bp_quitar = Blueprint('quitar_transacao', __name__)

@bp_quitar.route('/<int:sequencia>', methods=['POST'])  # 👈 Adiciona POST
@login_required
def iniquitacao(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
        
    # Busca dados ANTES
    cursor.execute("""
        SELECT descricao, status, tipo 
        FROM transacoes 
        WHERE sequencia_transacoes = %s AND user_id = %s
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
        SET status = %s, 
            data_quitamento = %s 
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (novo_status, hoje, sequencia, user_id))
    conexao.commit()
    
    # Auditoria
    AuditoriaFinanceiraService.registrar(
        transacao_id=sequencia,
        acao=acao,
        campo_alterado='status',
        valor_antigo=transacao[1],
        valor_novo=novo_status
    )

    return jsonify({'success': True})