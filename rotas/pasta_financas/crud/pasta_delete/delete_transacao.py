from flask import jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
import logging

logger = logging.getLogger(__name__)

def ini_inativar_financas(bp):
    
    # INATIVAR FINANCAS UNICO
    @bp.route('/excluir/<int:transacao_id>', methods=['DELETE'])
    @login_required
    def inativar_financa(transacao_id):
        try:
            conexao, cursor = ini_conexao()

            # 1. Verifica se existe
            cursor.execute("""
                SELECT descricao, valor_parcela, valor_total, total_parcelas, numero_parcela, transacao_pai_id, tipo, status
                FROM transacoes
                WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 1
            """, (transacao_id, session['user_id']))
            
            transacao = cursor.fetchone()

            if not transacao:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada ou já inativada.'
                }), 404
            
            # Índices: 0=descricao, 1=valor_parcela, 2=valor_total, 3=total_parcelas, 4=numero_parcela, 5=transacao_pai_id, 6=tipo, 7=status
            descricao = transacao[0]
            tipo = transacao[6]
            total_parcelas = transacao[3]
            numero_parcela = transacao[4]
            transacao_pai_id = transacao[5]

            # Caso 1: É uma parcela (tem pai)
            if transacao_pai_id is not None:
                return jsonify({
                    'success': False,
                    'tipo_parcelamento': 'parcela',
                    'mensagem': f'Esta é a parcela {numero_parcela}/{total_parcelas} de um parcelamento.',
                    'tipo': tipo,
                    'transacao_pai_id': transacao_pai_id,
                    'numero_parcela': numero_parcela,
                    'total_parcelas': total_parcelas,
                    'descricao': descricao
                }), 400
            
            # Caso 2: É a transação principal com parcelas
            if total_parcelas and total_parcelas > 1:
                return jsonify({
                    'success': False,
                    'tipo_parcelamento': 'transacao_com_parcelas',
                    'mensagem': f'Esta transação possui {total_parcelas} parcelas.',
                    'tipo': tipo,
                    'total_parcelas': total_parcelas,
                    'transacao_id': transacao_id,
                    'descricao': descricao
                }), 400

            # 3. Caso 3: Transação simples (sem parcelas) - PODE EXCLUIR
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 0,
                    excluido_em = CURRENT_TIMESTAMP,
                    excluido_por = %s,
                    data_alteracao = CURRENT_TIMESTAMP
                WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 1
            """, (session['user_id'], transacao_id, session['user_id']))
            conexao.commit()

            return jsonify({
                'success': True,
                'message': f'Transação "{descricao}" inativada com sucesso!'
            }), 200

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro inesperado: {str(e)}'
            }), 500

    # INATIVAR FINANCAS PARCELADO
    @bp.route('/excluir_parcelamento/<int:transacao_pai_id>', methods=['DELETE'])
    @login_required
    def excluir_parcelamento_completo(transacao_pai_id):
        """ INATIVA A TRANSAÇÃO PRINCIPAL E TODAS AS SUAS PARCELAS """

        try:
            conexao, cursor = ini_conexao()

            # BUSCA A DESCRICAO DA TRANSACAO PRINCIPAL
            cursor.execute("""
                SELECT descricao, data_vencimento, status, total_parcelas
                FROM transacoes
                WHERE sequencia_transacoes = %s AND user_id = %s
            """, (transacao_pai_id, session['user_id']))
            
            transacao_principal = cursor.fetchone()

            if not transacao_principal:
                return jsonify({
                    'success': False,
                    'error': 'Transação principal não encontrada.'
                }), 404

            # Índices: 0=descricao, 1=data_vencimento, 2=status, 3=total_parcelas
            descricao = transacao_principal[0]
            total_parcelas = transacao_principal[3]

            # INATIVA A TRANSAÇÃO PRINCIPAL E TODAS AS PARCELAS
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 0,
                    excluido_em = CURRENT_TIMESTAMP,
                    excluido_por = %s,
                    data_alteracao = CURRENT_TIMESTAMP
                WHERE (sequencia_transacoes = %s OR transacao_pai_id = %s)
                AND user_id = %s
                AND ativo = 1
            """, (session['user_id'], transacao_pai_id, transacao_pai_id, session['user_id']))
            conexao.commit()

            total_afetadas = cursor.rowcount

            return jsonify({
                'success': True,
                'message': f'Parcelamento "{descricao}" e suas {total_parcelas} parcelas foram inativados.',
                'total_parcelas': total_afetadas
            }), 200
        
        except Exception as e:
            logger.error(f"Erro ao inativar parcelamento: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro ao inativar parcelamento: {str(e)}'
            }), 500