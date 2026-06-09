# reativar_transacao.py
from flask import session, jsonify
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

def ini_reativar_financas(bp):  # <-- RECEBE o blueprint

    # Adicione esta rota NO MESMO ARQUIVO

    @bp.route('/verificar_reativacao/<int:transacao_seq>', methods=['GET'])
    @login_required
    def verificar_reativacao(transacao_seq):
        """Apenas verifica o tipo da transação, sem alterar nada"""
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 401
        
        conexao, cursor = ini_conexao()

        cursor.execute("""
            SELECT descricao, status, tipo, ativo, transacao_pai_id, total_parcelas
            FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 0
        """, (transacao_seq, user_id))
        
        transacao = cursor.fetchone()

        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada ou já está ativa!'}), 404
        
        # Só retorna as informações, NÃO FAZ UPDATE
        # Na rota de verificação, quando for parcela
        if transacao[4] is not None:
            # Busca o ID do pai
            transacao_pai_id = transacao[4]
            
            return jsonify({
                'tipo': 'parcela',
                'mensagem': f'Esta é uma parcela. Deseja reativar o parcelamento COMPLETO?',
                'transacao_pai_id': transacao_pai_id,
                'total_parcelas': transacao[5],
                'descricao': transacao[0]
            })
        
        if transacao[5] > 1:
            return jsonify({
                'tipo': 'parcelamento',
                'mensagem': f'Esta transação possui {transacao[5]} parcelas. Deseja reativar tudo?',
                'total_parcelas': transacao[5],
                'descricao': transacao[0]
            })
        
        # É transação simples
        return jsonify({
            'tipo': 'simples',
            'descricao': transacao[0],
            'mensagem': f'Deseja reativar a transação "{transacao[0]}"?'
        })



    @bp.route('/reativar/<int:transacao_seq>', methods=['POST'])
    @login_required
    def reativar_transacao(transacao_seq):
        """Reativa a transação (já sabe que é simples)"""
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'Usuário não encontrado!'}), 401
        
        conexao, cursor = ini_conexao()
        
        # Verifica se existe e está inativa
        cursor.execute("""
            SELECT descricao
            FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 0
        """, (transacao_seq, user_id))
        
        transacao = cursor.fetchone()
        
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada ou já está ativa!'}), 404
        
        # Reativa
        cursor.execute("""
            UPDATE transacoes
            SET ativo = 1,
                excluido_em = NULL,
                excluido_por = NULL,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 0
        """, (transacao_seq, user_id))
        
        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Transação "{transacao[0]}" reativada com sucesso!'
        })
    
    # Rota para reativar parcelamento completo
    @bp.route('/reativar_parcelamento/<int:transacao_pai_id>', methods=['POST'])
    @login_required
    def reativar_parcelamento(transacao_pai_id):
        """Reativa transação principal e TODAS as parcelas"""
        try:
            conexao, cursor = ini_conexao()
            
            cursor.execute("""
                SELECT descricao, total_parcelas
                FROM transacoes
                WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 0
            """, (transacao_pai_id, session['user_id']))
            
            parcelamento = cursor.fetchone()
            
            if not parcelamento:
                return jsonify({
                    'success': False,
                    'error': 'Parcelamento não encontrado ou já está ativo.'
                }), 404
            
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 1,
                    excluido_em = NULL,
                    excluido_por = NULL,
                    data_alteracao = CURRENT_TIMESTAMP
                WHERE (sequencia_transacoes = %s OR transacao_pai_id = %s)
                AND user_id = %s
                AND ativo = 0
            """, (transacao_pai_id, transacao_pai_id, session['user_id']))
            
            conexao.commit()
            
            return jsonify({
                'success': True,
                'message': f'Parcelamento "{parcelamento[0]}" e suas {parcelamento[1]} parcelas foram reativados!'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro ao reativar parcelamento: {str(e)}'
            }), 500