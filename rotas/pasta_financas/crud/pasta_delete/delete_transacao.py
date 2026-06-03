from flask import jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
import sqlite3
import logging

logger = logging.getLogger(__name__)

def ini_inativar_financas(bp):
    
    # INATIVAR FINANCAS UNICO
    @bp.route('/excluir/<int:transacao_id>', methods=['DELETE'])
    @login_required
    def inativar_financa(transacao_id):
        try:
            conexao = ini_conexao()
            cursor = conexao.cursor()

            #1. Verifica se existe
            cursor.execute("""
                SELECT descricao, valor_parcela, valor_total, total_parcelas, numero_parcela, transacao_pai_id, tipo, status
                FROM transacoes
                WHERE sequencia_transacoes = ? AND user_id = ? AND ativo = 1
""", (transacao_id, session['user_id']))
            
            transacao = cursor.fetchone()

            if not transacao:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada ou já inativada.'
                }), 404
            
            # 2. VALIDAÇÃO: Verifica se é parcela de um parcelamento
            total_parcelas = transacao['total_parcelas']
            numero_parcela = transacao['numero_parcela']
            transacao_pai_id = transacao['transacao_pai_id']

            # Caso 1: É uma parcela (tem pai)
            if transacao_pai_id is not None:
                return jsonify({
                    'success': False,
                    'tipo_parcelamento': 'parcela',
                    'mensagem': f'Esta é a parcela {numero_parcela}/{total_parcelas} de um parcelamento.',
                    'tipo': transacao['tipo'],
                    'transacao_pai_id': transacao_pai_id,
                    'numero_parcela': numero_parcela,
                    'total_parcelas': total_parcelas,
                    'descricao': transacao['descricao']
                }), 400
            
            # Caso 2: É a transação principal com parcelas
            if total_parcelas and total_parcelas > 1:
                return jsonify({
                    'success': False,
                    'tipo_parcelamento': 'transacao_com_parcelas',
                    'mensagem': f'Esta transação possui {total_parcelas} parcelas.',
                    'tipo': transacao['tipo'],
                    'total_parcelas': total_parcelas,
                    'transacao_id': transacao_id,
                    'descricao': transacao['descricao']
                }), 400

            # 3. Caso 3: Transação simples (sem parcelas) - PODE EXCLUIR
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 0,
                    excluido_em = datetime('now', 'localtime'),
                    excluido_por = ?,
                    data_alteracao = datetime('now', 'localtime')
                WHERE sequencia_transacoes = ? AND user_id = ? AND ativo = 1                
""", (session['user_id'], transacao_id, session['user_id']))
            conexao.commit()

            return jsonify({
                'success': True,
                'message': f'Transação "{transacao['descricao']}" inativada com sucesso!'
            }), 200


        except sqlite3.Error as e:
            logger.error(f"Erro SQLite: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro no banco de dados: {str(e)}'
            }), 500       

        except Exception as e:
            logger.error(f"Erro inesperado {e}")
            return jsonify ({
                'success': False,
                'error': f'Erro inesperado {str(e)}'
            }), 500



    # INATIVAR FINANCAS PARCELADO
    @bp.route('/excluir_parcelamento/<int:transacao_pai_id>', methods=['DELETE'])
    @login_required
    def excluir_parcelamento_completo(transacao_pai_id):
        """ INATIVA A TRANSAÇÃO PRINCIPAL E TODAS AS SUAS PARCELAS """

        try:
            conexao = ini_conexao()
            cursor = conexao.cursor()

            # BUSCA A DESCRICAO DA TRANSACAO PRINCIPAL
            cursor.execute("""
                SELECT descricao, data_vencimento, status, total_parcelas
                FROM transacoes
                WHERE sequencia_transacoes = ? AND user_id = ?
""", (transacao_pai_id, session['user_id']))
            
            transacao_principal = cursor.fetchone()

            if not transacao_principal:
                return jsonify({
                    'success': False,
                    'error': 'Transação principal não encontrada.'
                }), 404


            # INATIVA A TRANSAÇÃO PRINCIPAL E TODAS AS PARCELAS
            cursor.execute("""
            UPDATE transacoes
            SET ativo = 0,
                excluido_em = datetime('now', 'localtime'),
                excluido_por = ?,
                data_alteracao = datetime('now', 'localtime')
            WHERE (sequencia_transacoes = ? OR transacao_pai_id = ?)
            AND user_id = ?
            AND ativo = 1
""", (session['user_id'], transacao_pai_id, transacao_pai_id, session['user_id']))
            conexao.commit()

            total_afetadas = cursor.rowcount

            return jsonify({
                'success': True,
                'message': f'Parcelamento "{transacao_principal["descricao"]}" e suas {transacao_principal["total_parcelas"]} parcelas foram inativados.',
                'total_parcelas': total_afetadas
            }), 200
        
        except Exception as e:
            logger.error(f"Erro ao inativar parcelamento: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro ao inativar parcelamento: {str(e)}'
            })
