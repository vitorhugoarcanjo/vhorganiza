# rotas/auditoria_geral/pasta_financas/services_auditoria.py
import json
from flask import request, session
from utils.database.conexao_global import ini_conexao


class AuditoriaFinanceiraService:

    @staticmethod
    def get_db_connection():
        return ini_conexao()

    @staticmethod
    def registrar(transacao_id, acao, campo_alterado=None, valor_antigo=None,
                  valor_novo=None, conexao=None):
        """
        Registra uma ação na auditoria de finanças.
        Se `conexao` fornecida, usa a MESMA (não faz commit separado) — transacional.
        """
        propria_conexao = False
        try:
            if conexao is None:
                conexao, cursor = AuditoriaFinanceiraService.get_db_connection()
                propria_conexao = True
            else:
                cursor = conexao.cursor()

            if valor_antigo and len(str(valor_antigo)) > 500:
                valor_antigo = str(valor_antigo)[:500] + "..."
            if valor_novo and len(str(valor_novo)) > 500:
                valor_novo = str(valor_novo)[:500] + "..."

            cursor.execute("""
                INSERT INTO financas_auditoria
                (transacao_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                transacao_id,
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
            print(f"Erro ao registrar auditoria financeira: {e}")
            if propria_conexao:
                conexao.rollback()
            return False

    @staticmethod
    def listar_por_transacao(transacao_id, limite=50):
        """Lista todas as ações de uma transação"""
        try:
            conexao, cursor = AuditoriaFinanceiraService.get_db_connection()

            cursor.execute("""
                SELECT fa.*, u.nome as usuario_nome
                FROM financas_auditoria fa
                LEFT JOIN cadastre_se u ON fa.usuario_id = u.id
                WHERE fa.transacao_id = %s
                ORDER BY fa.data_hora DESC
                LIMIT %s
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
            conexao, cursor = AuditoriaFinanceiraService.get_db_connection()

            # 🔥 Define os nomes das colunas manualmente (o cursor do projeto
            # aparentemente não expõe .description corretamente)
            colunas = [
                'id', 'transacao_id', 'acao', 'campo_alterado',
                'valor_antigo', 'valor_novo', 'usuario_id', 'data_hora', 'ip',
                'usuario_nome', 'data_hora_br'
            ]

            cursor.execute("""
                SELECT
                    fa.id, fa.transacao_id, fa.acao, fa.campo_alterado,
                    fa.valor_antigo, fa.valor_novo, fa.usuario_id, fa.data_hora, fa.ip,
                    u.nome as usuario_nome,
                    TO_CHAR(fa.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br
                FROM financas_auditoria fa
                LEFT JOIN cadastre_se u ON fa.usuario_id = u.id
                WHERE fa.transacao_id = %s
                ORDER BY fa.data_hora DESC
                LIMIT %s
            """, (transacao_id, limite))

            auditoria = []
            for row in cursor.fetchall():
                # 🔥 Converte tupla → dict manualmente (não usa dict(row))
                item = dict(zip(colunas, row))

                item['data_hora'] = item.get('data_hora_br') or str(item.get('data_hora') or '')
                item['alteracoes'] = []

                if item.get('campo_alterado') in ['multiplos', 'edicao_completa'] and item.get('valor_novo'):
                    try:
                        item['alteracoes'] = json.loads(item['valor_novo'])
                    except Exception:
                        item['alteracoes'] = []

                auditoria.append(item)

            return auditoria
        except Exception as e:
            print(f"Erro ao listar auditoria financeira formatada: {e}")
            return []