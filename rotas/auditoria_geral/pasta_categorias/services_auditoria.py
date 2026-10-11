# rotas/auditoria_geral/pasta_categorias/services_auditoria.py
# ==========================================================
# AUDITORIA DE CATEGORIAS - SERVICE
# ==========================================================

import json
from flask import request, session
from utils.database.conexao_global import ini_conexao, get_conexao_direct


class AuditoriaCategoriasService:

    @staticmethod
    def get_db_connection():
        return ini_conexao()

    @staticmethod
    def get_db_connection_direct():
        return get_conexao_direct()

    @staticmethod
    def registrar(categoria_id, acao, campo_alterado=None, valor_antigo=None,
                  valor_novo=None, conexao=None):
        """
        Registra uma ação na auditoria.
        Se `conexao` fornecida, usa a MESMA (transacional).
        """
        propria_conexao = False
        try:
            if conexao is None:
                conexao, cursor = AuditoriaCategoriasService.get_db_connection()
                propria_conexao = True
            else:
                cursor = conexao.cursor()

            if valor_antigo and len(str(valor_antigo)) > 2000:
                valor_antigo = str(valor_antigo)[:2000] + "..."
            if valor_novo and len(str(valor_novo)) > 2000:
                valor_novo = str(valor_novo)[:2000] + "..."

            cursor.execute("""
                INSERT INTO categorias_auditoria
                (categoria_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                categoria_id,
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
            print(f"Erro ao registrar auditoria de categorias: {e}")
            if propria_conexao:
                conexao.rollback()
            return False

    @staticmethod
    def listar_por_categoria(categoria_id, limite=50):
        """Lista todas as ações de uma categoria"""
        try:
            conexao, cursor = AuditoriaCategoriasService.get_db_connection()

            cursor.execute("""
                SELECT ca.*, u.nome as usuario_nome
                FROM categorias_auditoria ca
                LEFT JOIN cadastre_se u ON ca.usuario_id = u.id
                WHERE ca.categoria_id = %s
                ORDER BY ca.data_hora DESC
                LIMIT %s
            """, (categoria_id, limite))

            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar auditoria de categorias: {e}")
            return []

    @staticmethod
    def listar_por_categoria_formatado(categoria_id, limite=50):
        """Lista auditoria com formatação (padrão 2099)"""
        try:
            conexao, cursor = AuditoriaCategoriasService.get_db_connection()

            # 🔥 Colunas explícitas (evita bug de dict(row))
            colunas = [
                'id', 'categoria_id', 'acao', 'campo_alterado',
                'valor_antigo', 'valor_novo', 'usuario_id', 'data_hora', 'ip',
                'usuario_nome', 'data_hora_br'
            ]

            cursor.execute("""
                SELECT
                    ca.id, ca.categoria_id, ca.acao, ca.campo_alterado,
                    ca.valor_antigo, ca.valor_novo, ca.usuario_id, ca.data_hora, ca.ip,
                    u.nome as usuario_nome,
                    TO_CHAR(ca.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br
                FROM categorias_auditoria ca
                LEFT JOIN cadastre_se u ON ca.usuario_id = u.id
                WHERE ca.categoria_id = %s
                ORDER BY ca.data_hora DESC
                LIMIT %s
            """, (categoria_id, limite))

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
            print(f"Erro ao listar auditoria de categorias formatada: {e}")
            return []