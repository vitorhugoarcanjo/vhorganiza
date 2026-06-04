import json
from flask import request, session, g
from utils.database.conexao_global import ini_conexao, get_conexao_direct

class AuditoriaService:
    
    @staticmethod
    def get_db_connection():
        """Retorna conexão do contexto atual do Flask"""
        return ini_conexao()
    
    @staticmethod
    def get_db_connection_direct():
        """Retorna conexão direta para uso fora do contexto Flask"""
        return get_conexao_direct()
    
    @staticmethod
    def registrar(tarefa_id, acao, campo_alterado=None, valor_antigo=None, valor_novo=None, conexao=None):
        """
        Registra uma ação na auditoria
        
        Args:
        conexao: Opcional. Se fornecida, usa a MESMA conexão (não faz commit separado)
        """
       
        try:
            propria_conexao = False
            if conexao is None:
                conexao = AuditoriaService.get_db_connection()
                propria_conexao = True

            cursor = conexao.cursor()
            
            if valor_antigo and len(str(valor_antigo)) > 500:
                valor_antigo = str(valor_antigo)[:500] + "..."
            if valor_novo and len(str(valor_novo)) > 500:
                valor_novo = str(valor_novo)[:500] + "..."
            
            cursor.execute("""
                INSERT INTO tarefas_auditoria 
                (tarefa_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tarefa_id,
                acao,
                campo_alterado,
                valor_antigo,
                valor_novo,
                session.get('user_id'),
                request.remote_addr
            ))
            if propria_conexao:
                conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")
            if propria_conexao:
                conexao.rollback()
            return False
    
    @staticmethod
    def listar_por_tarefa(tarefa_id, limite=50):
        """Lista todas as ações de uma tarefa"""
        try:
            conexao = AuditoriaService.get_db_connection()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT ta.*, u.nome as usuario_nome
                FROM tarefas_auditoria ta
                LEFT JOIN cadastre_se u ON ta.usuario_id = u.id
                WHERE ta.tarefa_id = ?
                ORDER BY ta.data_hora DESC
                LIMIT ?
            """, (tarefa_id, limite))
            
            auditoria = cursor.fetchall()
            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria: {e}")
            return []
        
    @staticmethod
    def listar_por_tarefa_formatado(tarefa_id, limite=50):
        """Lista auditoria com formatação para exibição (converte JSON)"""
        try:
            conexao = AuditoriaService.get_db_connection()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT 
                    ta.*, 
                    u.nome as usuario_nome,
                    strftime('%d/%m/%Y %H:%M:%S', ta.data_hora, 'localtime') as data_hora_br
                FROM tarefas_auditoria ta
                LEFT JOIN cadastre_se u ON ta.usuario_id = u.id
                WHERE ta.tarefa_id = ?
                ORDER BY ta.data_hora DESC
                LIMIT ?
            """, (tarefa_id, limite))
            
            auditoria = []
            for row in cursor.fetchall():
                item = dict(row)
                
                item['data_hora'] = item.get('data_hora_br', item.get('data_hora'))
                
                # Converte JSON
                if item.get('campo_alterado') in ['múltiplos', 'todos'] and item.get('valor_novo'):
                    try:
                        item['alteracoes'] = json.loads(item['valor_novo'])
                    except:
                        item['alteracoes'] = []
                else:
                    item['alteracoes'] = []
                
                auditoria.append(item)
            
            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria formatada: {e}")
            return []