# rotas/pasta_tarefas/crud/pasta_insert/services.py
# ==========================================================
# INSERIR TAREFA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class InserirTarefaService:

    @staticmethod
    def get_proxima_sequencia(cursor, usuario_id):
        """Retorna a próxima sequência visual de tarefas do usuário"""
        cursor.execute("""
            SELECT COALESCE(MAX(tarefa_sequencia), 0) + 1
            FROM tarefas
            WHERE usuario_id = %s
        """, (usuario_id,))
        res = cursor.fetchone()
        return res[0] if res else 1

    @staticmethod
    def buscar_categorias(cursor, usuario_id):
        try:
            cursor.execute("""
                SELECT id, nome, cor FROM categorias_tarefas
                WHERE usuario_id = %s ORDER BY nome ASC
            """, (usuario_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao buscar categorias do user {user_id}: {e}")
            return []

    @staticmethod
    def buscar_nome_categoria(cursor, categoria_id):
        """Retorna o nome da categoria pelo ID (ou '(vazio)')"""
        if not categoria_id:
            return '(vazio)'
        try:
            cursor.execute("SELECT nome FROM categorias_tarefas WHERE id = %s", (categoria_id,))
            c = cursor.fetchone()
            return c[0] if c else '(vazio)'
        except Exception:
            return '(vazio)'

    @staticmethod
    def criar_tarefa(cursor, usuario_id, dados):
        """
        Cria uma nova tarefa.
        Retorna (sucesso: bool, resultado: dict|str)
        """
        try:
            sequencia = InserirTarefaService.get_proxima_sequencia(cursor, usuario_id)

            cursor.execute("""
                INSERT INTO tarefas (
                    usuario_id, tarefa_sequencia, titulo, descricao, status,
                    prioridade, data_inicio, data_final, categoria_id, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                RETURNING id
            """, (
                usuario_id,
                sequencia,
                dados['titulo'],
                dados['descricao'],
                dados['status'],
                dados['prioridade'],
                dados['data_inicio'],
                dados['data_final'],
                dados['categoria_id'],
            ))

            tarefa_id = cursor.fetchone()[0]

            return True, {
                'tarefa_id': tarefa_id,
                'tarefa_sequencia': sequencia,
                'mensagem': 'Tarefa criada com sucesso!'
            }

        except Exception as e:
            msg = f"Erro ao inserir tarefa: {e}"
            logger.error(msg)
            return False, msg