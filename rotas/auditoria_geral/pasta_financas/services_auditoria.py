import json
from flask import request, session
from utils.database.conexao_global import ini_conexao

class AuditoriaFinanceiraService:
    
    @staticmethod
    def get_db_connection():
        return ini_conexao()
    
    @staticmethod
    def registrar(transacao_id, acao, campo_alterado=None, valor_antigo=None, valor_novo=None):
        """Registra uma ação na auditoria de finanças"""
        try:
            conexao = AuditoriaFinanceiraService.get_db_connection()
            cursor = conexao.cursor()
            
            if valor_antigo and len(str(valor_antigo)) > 500:
                valor_antigo = str(valor_antigo)[:500] + "..."
            if valor_novo and len(str(valor_novo)) > 500:
                valor_novo = str(valor_novo)[:500] + "..."
            
            cursor.execute("""
                INSERT INTO financas_auditoria 
                (transacao_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transacao_id,
                acao,
                campo_alterado,
                valor_antigo,
                valor_novo,
                session.get('user_id'),
                request.remote_addr
            ))
            conexao.commit()

            return True
        except Exception as e:
            print(f"Erro ao registrar auditoria financeira: {e}")
            return False
    
    @staticmethod
    def listar_por_transacao(transacao_id, limite=50):
        """Lista todas as ações de uma transação"""
        try:
            conexao = AuditoriaFinanceiraService.get_db_connection()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT fa.*, u.nome as usuario_nome
                FROM financas_auditoria fa
                LEFT JOIN cadastre_se u ON fa.usuario_id = u.id
                WHERE fa.transacao_id = ?
                ORDER BY fa.data_hora DESC
                LIMIT ?
            """, (transacao_id, limite))
            auditoria = cursor.fetchall()

            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria financeira: {e}")
            return []
        
    @staticmethod
    def listar_por_transacao_formatado(transacao_id, limite=50):
        """Lista auditoria com formatação para exibição"""
        try:
            conexao = AuditoriaFinanceiraService.get_db_connection()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT 
                    fa.*, 
                    u.nome as usuario_nome,
                    strftime('%d/%m/%Y %H:%M:%S', fa.data_hora, 'localtime') as data_hora_br
                FROM financas_auditoria fa
                LEFT JOIN cadastre_se u ON fa.usuario_id = u.id
                WHERE fa.transacao_id = ?
                ORDER BY fa.data_hora DESC
                LIMIT ?
            """, (transacao_id, limite))
            
            auditoria = []
            for row in cursor.fetchall():
                item = dict(row)
                item['data_hora'] = item.get('data_hora_br', item.get('data_hora'))
                item['alteracoes'] = []
                
                if item.get('campo_alterado') in ['multiplos', 'edicao_completa'] and item.get('valor_novo'):
                    try:
                        item['alteracoes'] = json.loads(item['valor_novo'])
                    except:
                        item['alteracoes'] = []
                
                auditoria.append(item)

            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria financeira formatada: {e}")
            return []