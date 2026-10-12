# rotas/pasta_dashboard/queries.py
# ==========================================================
# QUERIES SQL - DASHBOARD
# Foco: QUITAÇÃO (fluxo real). Exceção: A Pagar/A Receber.
# ==========================================================

class DashboardQueries:

    # ==========================================================
    # KPIs
    # ==========================================================

    @staticmethod
    def get_saldo_periodo():
        """Receitas e despesas QUITADAS no período (por data_quitamento)."""
        return """
            SELECT
                COALESCE(SUM(CASE WHEN t.tipo = 'receita' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS receitas,
                COALESCE(SUM(CASE WHEN t.tipo = 'despesa' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS despesas
            FROM transacoes t
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'quitado'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_quitamento BETWEEN %s AND %s
        """

    @staticmethod
    def get_a_pagar_periodo():
        """Despesas EM ABERTO no período (por data_vencimento)."""
        return """
            SELECT COALESCE(SUM(
                CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
            ), 0)
            FROM transacoes t
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'aberto'
              AND t.tipo = 'despesa'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_vencimento BETWEEN %s AND %s
        """

    @staticmethod
    def get_a_receber_periodo():
        """Receitas EM ABERTO no período (por data_vencimento)."""
        return """
            SELECT COALESCE(SUM(
                CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
            ), 0)
            FROM transacoes t
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'aberto'
              AND t.tipo = 'receita'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_vencimento BETWEEN %s AND %s
        """

    @staticmethod
    def get_saldo_periodo_anterior():
        """Saldo do período anterior (pra tendência) — por quitação."""
        return """
            SELECT
                COALESCE(SUM(CASE WHEN t.tipo = 'receita' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS receitas,
                COALESCE(SUM(CASE WHEN t.tipo = 'despesa' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS despesas
            FROM transacoes t
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'quitado'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_quitamento BETWEEN %s AND %s
        """

    # ==========================================================
    # FLUXO MENSAL — por quitação
    # ==========================================================
    @staticmethod
    def get_fluxo_mensal():
        return """
            SELECT
                TO_CHAR(t.data_quitamento, 'YYYY-MM') AS mes,
                COALESCE(SUM(CASE WHEN t.tipo = 'receita' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS receitas,
                COALESCE(SUM(CASE WHEN t.tipo = 'despesa' THEN
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                    ELSE 0 END), 0) AS despesas
            FROM transacoes t
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'quitado'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_quitamento >= %s
            GROUP BY TO_CHAR(t.data_quitamento, 'YYYY-MM')
            ORDER BY mes ASC
        """

    # ==========================================================
    # TOP CATEGORIAS — por quitação
    # ==========================================================
    @staticmethod
    def get_top_categorias():
        return """
            SELECT
                COALESCE(c.nome, 'Sem categoria') AS categoria_nome,
                COALESCE(c.cor, '#6c757d') AS categoria_cor,
                COALESCE(SUM(
                    CASE WHEN t.transacao_pai_id IS NOT NULL THEN t.valor_parcela ELSE t.valor_total END
                ), 0) AS total
            FROM transacoes t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'financas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'quitado'
              AND t.tipo = 'despesa'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_quitamento BETWEEN %s AND %s
            GROUP BY c.nome, c.cor
            ORDER BY total DESC
            LIMIT 5
        """

    # ==========================================================
    # ÚLTIMAS TRANSAÇÕES — por quitação
    # ==========================================================
    @staticmethod
    def get_ultimas_transacoes():
        return """
            SELECT
                t.id,
                t.sequencia_transacoes,
                t.tipo,
                t.descricao,
                t.valor_total,
                t.valor_parcela,
                t.transacao_pai_id,
                t.status,
                t.data_emissao,
                t.data_vencimento,
                t.data_quitamento,
                c.nome AS categoria_nome,
                c.cor  AS categoria_cor
            FROM transacoes t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'financas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'quitado'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_quitamento BETWEEN %s AND %s
            ORDER BY t.data_quitamento DESC, t.sequencia_transacoes DESC
            LIMIT 10
        """