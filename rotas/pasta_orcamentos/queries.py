# rotas/pasta_orcamentos/queries.py
# ==========================================================
# QUERIES DO MÓDULO DE ORÇAMENTOS
# ==========================================================

class OrcamentosQueries:

    @staticmethod
    def get_orcamentos_base():
        """Query base — filtros aplicados em cima"""
        return """
            SELECT o.id, o.titulo, o.cliente, o.status, o.created_at
            FROM orcamentos o
            WHERE o.usuario_id = %s
        """

    @staticmethod
    def get_orcamento_detalhes():
        return """
            SELECT id, titulo, cliente, status, estrutura, created_at
            FROM orcamentos
            WHERE id = %s AND usuario_id = %s
        """

    @staticmethod
    def criar_orcamento():
        return """
            INSERT INTO orcamentos (usuario_id, titulo, cliente, status, estrutura)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

    @staticmethod
    def atualizar_orcamento():
        return """
            UPDATE orcamentos
            SET titulo = %s, cliente = %s, status = %s, estrutura = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

    @staticmethod
    def excluir_orcamento():
        return """
            DELETE FROM orcamentos
            WHERE id = %s AND usuario_id = %s
        """