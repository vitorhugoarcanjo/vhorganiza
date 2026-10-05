# rotas/auditoria_geral/pasta_orcamentos/services_auditoria.py
# ==========================================================
# SERVICE DE AUDITORIA DE ORÇAMENTOS
# ==========================================================

import json
from flask import request, session
from utils.database.conexao_global import ini_conexao


class AuditoriaOrcamentosService:

    @staticmethod
    def get_db_connection():
        return ini_conexao()

    @staticmethod
    def registrar(orcamento_id, acao, campo_alterado=None,
                  valor_antigo=None, valor_novo=None, conexao=None):
        """Registra uma ação. Se `conexao` fornecida, usa a MESMA (transacional)."""
        propria_conexao = False
        try:
            if conexao is None:
                conexao, cursor = AuditoriaOrcamentosService.get_db_connection()
                propria_conexao = True
            else:
                cursor = conexao.cursor()

            if valor_antigo and len(str(valor_antigo)) > 500:
                valor_antigo = str(valor_antigo)[:500] + "..."
            if valor_novo and len(str(valor_novo)) > 500:
                valor_novo = str(valor_novo)[:500] + "..."

            cursor.execute("""
                INSERT INTO orcamentos_auditoria
                (orcamento_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                orcamento_id,
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
            print(f"Erro ao registrar auditoria de orçamento: {e}")
            if propria_conexao:
                conexao.rollback()
            return False

    @staticmethod
    def listar_por_orcamento_formatado(orcamento_id, limite=50):
        """Lista auditoria com formatação (colunas explícitas + zip)"""
        try:
            conexao, cursor = AuditoriaOrcamentosService.get_db_connection()

            colunas = [
                'id', 'orcamento_id', 'acao', 'campo_alterado',
                'valor_antigo', 'valor_novo', 'usuario_id', 'data_hora', 'ip',
                'usuario_nome', 'data_hora_br'
            ]

            cursor.execute("""
                SELECT
                    oa.id, oa.orcamento_id, oa.acao, oa.campo_alterado,
                    oa.valor_antigo, oa.valor_novo, oa.usuario_id, oa.data_hora, oa.ip,
                    u.nome as usuario_nome,
                    TO_CHAR(oa.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br
                FROM orcamentos_auditoria oa
                LEFT JOIN cadastre_se u ON oa.usuario_id = u.id
                WHERE oa.orcamento_id = %s
                ORDER BY oa.data_hora DESC
                LIMIT %s
            """, (orcamento_id, limite))

            auditoria = []
            for row in cursor.fetchall():
                item = dict(zip(colunas, row))
                item['data_hora'] = item.get('data_hora_br') or str(item.get('data_hora') or '')
                item['alteracoes'] = []

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