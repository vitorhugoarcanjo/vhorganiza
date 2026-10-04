# rotas/auditoria_geral/pasta_tarefas/services_auditoria.py
# ==========================================================
# AUDITORIA DE TAREFAS - SERVICE
# ==========================================================

import json
from flask import request, session
from utils.database.conexao_global import ini_conexao, get_conexao_direct


class AuditoriaService:

    @staticmethod
    def get_db_connection():
        return ini_conexao()

    @staticmethod
    def get_db_connection_direct():
        return get_conexao_direct()

    @staticmethod
    def registrar(tarefa_id, acao, campo_alterado=None, valor_antigo=None,
                  valor_novo=None, conexao=None):
        """Registra uma ação na auditoria. Se `conexao` fornecida, usa a MESMA."""
        propria_conexao = False
        try:
            if conexao is None:
                conexao, cursor = AuditoriaService.get_db_connection()
                propria_conexao = True
            else:
                cursor = conexao.cursor()

            if valor_antigo and len(str(valor_antigo)) > 500:
                valor_antigo = str(valor_antigo)[:500] + "..."
            if valor_novo and len(str(valor_novo)) > 500:
                valor_novo = str(valor_novo)[:500] + "..."

            cursor.execute("""
                INSERT INTO tarefas_auditoria
                (tarefa_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            conexao, cursor = AuditoriaService.get_db_connection()

            cursor.execute("""
                SELECT ta.*, u.nome as usuario_nome
                FROM tarefas_auditoria ta
                LEFT JOIN cadastre_se u ON ta.usuario_id = u.id
                WHERE ta.tarefa_id = %s
                ORDER BY ta.data_hora DESC
                LIMIT %s
            """, (tarefa_id, limite))

            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar auditoria: {e}")
            return []

    @staticmethod
    def listar_por_tarefa_formatado(tarefa_id, limite=50):
        """Lista auditoria com formatação (igual Finanças, com colunas explícitas)"""
        try:
            conexao, cursor = AuditoriaService.get_db_connection()

            # 🔥 Colunas explícitas (evita bug de dict(row))
            colunas = [
                'id', 'tarefa_id', 'acao', 'campo_alterado',
                'valor_antigo', 'valor_novo', 'usuario_id', 'data_hora', 'ip',
                'usuario_nome', 'data_hora_br'
            ]

            cursor.execute("""
                SELECT
                    ta.id, ta.tarefa_id, ta.acao, ta.campo_alterado,
                    ta.valor_antigo, ta.valor_novo, ta.usuario_id, ta.data_hora, ta.ip,
                    u.nome as usuario_nome,
                    TO_CHAR(ta.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br
                FROM tarefas_auditoria ta
                LEFT JOIN cadastre_se u ON ta.usuario_id = u.id
                WHERE ta.tarefa_id = %s
                ORDER BY ta.data_hora DESC
                LIMIT %s
            """, (tarefa_id, limite))

            auditoria = []
            for row in cursor.fetchall():
                item = dict(zip(colunas, row))

                item['data_hora'] = item.get('data_hora_br') or str(item.get('data_hora') or '')
                item['alteracoes'] = []

                # 🔥 Padrão 2099: só 'multiplos' tem lista de alterações
                if item.get('campo_alterado') == 'multiplos' and item.get('valor_novo'):
                    try:
                        item['alteracoes'] = json.loads(item['valor_novo'])
                    except Exception:
                        item['alteracoes'] = []

                auditoria.append(item)

            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria formatada: {e}")
            return []