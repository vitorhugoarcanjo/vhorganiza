# rotas/pasta_orcamentos/queries.py
# ==========================================================
# QUERIES DO MÓDULO DE ORÇAMENTOS
# ==========================================================

class OrcamentosQueries:

    @staticmethod
    def get_proxima_sequencia():
        """Retorna a próxima sequência visual pro usuário."""
        return """
            SELECT COALESCE(MAX(sequencia_orcamentos), 0) + 1
            FROM orcamentos
            WHERE usuario_id = %s
        """

    @staticmethod
    def get_orcamentos_base():
        """Query base — filtros aplicados em cima"""
        return """
            SELECT o.sequencia_orcamentos, o.id, o.numero, o.titulo, o.cliente,
                   o.status, o.valor_total, o.data_emissao, o.data_validade,
                   o.created_at, o.ativo
            FROM orcamentos o
            WHERE o.usuario_id = %s
        """

    @staticmethod
    def get_orcamento_detalhes():
        return """
            SELECT id, sequencia_orcamentos, numero, titulo, cliente, status,
                   estrutura, valor_total, data_emissao, data_validade,
                   data_entrega, descricao, observacoes, created_at, ativo
            FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s
        """

    @staticmethod
    def criar_orcamento():
        return """
            INSERT INTO orcamentos (
                usuario_id, sequencia_orcamentos, numero,
                titulo, cliente, status, estrutura, valor_total,
                data_emissao, data_validade, data_entrega,
                descricao, observacoes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, sequencia_orcamentos, numero
        """

    @staticmethod
    def atualizar_orcamento():
        return """
            UPDATE orcamentos
            SET titulo = %s, cliente = %s, status = %s, estrutura = %s,
                valor_total = %s,
                data_emissao = %s, data_validade = %s, data_entrega = %s,
                descricao = %s, observacoes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE sequencia_orcamentos = %s AND usuario_id = %s
        """

    @staticmethod
    def inativar_orcamento():
        return """
            UPDATE orcamentos
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """

    @staticmethod
    def reativar_orcamento():
        return """
            UPDATE orcamentos
            SET ativo = 1,
                excluido_em = NULL,
                excluido_por = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 0
        """

    @staticmethod
    def buscar_id_interno_por_sequencia():
        """Traduz sequência visual → id interno."""
        return """
            SELECT id FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s
        """