# rotas/pasta_categorias/queries.py
# ==========================================================
# TODAS AS QUERIES SQL DO MÓDULO DE CATEGORIAS
# ==========================================================


class CategoriasQueries:

    @staticmethod
    def get_categorias_base():
        """Query base — os filtros são aplicados em cima desta"""
        return """
            SELECT c.id,
                   c.usuario_id,
                   c.modulo,
                   c.sequencia_categorias,
                   c.numero,
                   c.nome,
                   c.cor,
                   c.ativo,
                   c.created_at,
                   c.updated_at
            FROM categorias c
            WHERE c.usuario_id = %s
        """

    @staticmethod
    def get_detalhes_categoria():
        return """
            SELECT c.id,
                   c.usuario_id,
                   c.modulo,
                   c.sequencia_categorias,
                   c.numero,
                   c.nome,
                   c.cor,
                   c.ativo,
                   c.created_at,
                   c.updated_at
            FROM categorias c
            WHERE c.id = %s AND c.usuario_id = %s
        """

    @staticmethod
    def get_proxima_sequencia():
        """Retorna a próxima sequência visual do usuário + módulo"""
        return """
            SELECT COALESCE(MAX(sequencia_categorias), 0) + 1
            FROM categorias
            WHERE usuario_id = %s AND modulo = %s
        """

    @staticmethod
    def criar_categoria():
        return """
            INSERT INTO categorias (
                usuario_id, modulo, sequencia_categorias, numero,
                nome, cor, ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            RETURNING id, sequencia_categorias, numero
        """

    @staticmethod
    def atualizar_categoria():
        return """
            UPDATE categorias
            SET nome = %s,
                cor = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s
        """

    @staticmethod
    def inativar_categoria():
        return """
            UPDATE categorias
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 1
        """

    @staticmethod
    def reativar_categoria():
        return """
            UPDATE categorias
            SET ativo = 1,
                excluido_em = NULL,
                excluido_por = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 0
        """