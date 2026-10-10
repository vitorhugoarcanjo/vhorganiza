# rotas/pasta_tarefas/queries.py
# ==========================================================
# TODAS AS QUERIES SQL DO MÓDULO DE TAREFAS
# ==========================================================


class TarefasQueries:

    @staticmethod
    def get_categorias_usuario():
        return """
            SELECT id, nome, cor
            FROM categorias_tarefas
            WHERE usuario_id = %s
            ORDER BY nome
        """

    @staticmethod
    def get_tarefas_base():
        """Query base — os filtros são aplicados em cima desta"""
        return """
            SELECT t.tarefa_sequencia,
                   t.titulo,
                   t.descricao,
                   t.status,
                   t.data_inicio,
                   t.data_final,
                   t.data_finalizacao,
                   t.categoria_id,
                   t.prioridade,
                   c.nome AS categoria_nome,
                   c.cor  AS categoria_cor,
                   t.ativo
            FROM tarefas t
            LEFT JOIN categorias_tarefas c ON c.id = t.categoria_id
            WHERE t.usuario_id = %s
        """

    @staticmethod
    def get_detalhes_tarefa():
        return """
            SELECT t.tarefa_sequencia,
                   t.titulo,
                   t.descricao,
                   t.status,
                   t.data_inicio,
                   t.data_final,
                   t.data_finalizacao,
                   t.prioridade,
                   t.motivo_conclusao,
                   c.nome AS categoria_nome,
                   c.cor  AS categoria_cor
            FROM tarefas t
            LEFT JOIN categorias_tarefas c ON c.id = t.categoria_id
            WHERE t.tarefa_sequencia = %s AND t.usuario_id = %s
        """