class FinancasQueries:
    """ TODAS AS QUERIES SQL DO MÓDULO DE FINANÇAS """
    
    @staticmethod
    def get_categorias_usuario():
        return """
            SELECT id, nome, cor
            FROM categorias_financas
            WHERE user_id = %s
            ORDER BY nome
"""

    @staticmethod
    def get_transacoes_base():
        return """
            SELECT t.sequencia_transacoes, t.id, t.tipo, t.valor_total, t.descricao, t.data_emissao,
                    c.nome AS categoria_nome, c.cor AS categoria_cor,
                    t.status, t.data_vencimento, t.ativo,
                    t.numero_parcela, t.total_parcelas, t.transacao_pai_id
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.user_id = %s
            AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
"""

    @staticmethod
    def get_transacao_detalhes():
        return """
            SELECT t.sequencia_transacoes, t.tipo, t.valor_total, t.descricao,
                    t.data_emissao, t.data_vencimento, t.data_quitamento,
                    t.status, t.numero_parcela, t.total_parcelas,
                    c.nome as categoria_nome, c.cor as categoria_cor
            FROM transacoes t
            LEFT JOIN categorias_financas c ON t.categoria_id = c.id
            WHERE t.sequencia_transacoes = %s AND t.user_id = %s
"""
