# rotas/pasta_tarefas/services/services_tarefas.py
# ==========================================================
# SERVICES DO MÓDULO DE TAREFAS
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class TarefasServices:

    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    def buscar_categorias(self, usuario_id):
        self.cursor.execute("""
            SELECT id, nome, cor FROM categorias_tarefas
            WHERE usuario_id = %s ORDER BY nome
        """, (usuario_id,))
        return self.cursor.fetchall()

    def buscar_tarefas(self, usuario_id, filtros):
        """
        Busca tarefas com filtros aplicados.
        Reaproveitado por todos os CRUDs (padrão 2099).
        """
        from rotas.pasta_tarefas.queries import TarefasQueries
        from rotas.pasta_tarefas.filters import TarefasFilters

        query = TarefasQueries.get_tarefas_base()
        params = [user_id]
        query, params = TarefasFilters.aplicar_filtros_query(query, params, filtros)
        query += " ORDER BY t.tarefa_sequencia ASC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()