# rotas/pasta_tela_pos_login/queries.py
# ==========================================================
# QUERIES SQL - TELA PÓS-LOGIN ("Meu Dia")
# ==========================================================

class PosLoginQueries:

    @staticmethod
    def get_vencendo_financas():
        """Despesas em aberto com vencimento <= hoje (vencidas ou vencendo hoje)"""
        return """
            SELECT t.id,
                   t.sequencia_transacoes,
                   t.descricao,
                   t.valor_total,
                   t.valor_parcela,
                   t.transacao_pai_id,
                   t.numero_parcela,
                   t.total_parcelas,
                   t.data_vencimento,
                   c.nome  AS categoria_nome,
                   c.cor   AS categoria_cor
            FROM transacoes t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'financas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'aberto'
              AND t.tipo = 'despesa'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_vencimento IS NOT NULL
              AND t.data_vencimento <= %s
            ORDER BY t.data_vencimento ASC
        """

    @staticmethod
    def get_vencendo_tarefas():
        """Tarefas pendentes/andamento com data_final <= hoje"""
        return """
            SELECT t.id,
                   t.tarefa_sequencia,
                   t.titulo,
                   t.status,
                   t.prioridade,
                   t.data_final,
                   c.nome AS categoria_nome,
                   c.cor  AS categoria_cor
            FROM tarefas t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'tarefas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status IN ('pendente', 'em andamento')
              AND t.data_final IS NOT NULL
              AND t.data_final <= %s
            ORDER BY t.data_final ASC, 
                     CASE t.prioridade
                        WHEN 'alta'  THEN 1
                        WHEN 'media' THEN 2
                        WHEN 'baixa' THEN 3
                        ELSE 4
                     END ASC
        """

    @staticmethod
    def get_proximos_financas():
        """Despesas em aberto com vencimento entre amanhã e hoje+7"""
        return """
            SELECT t.id,
                   t.sequencia_transacoes,
                   t.descricao,
                   t.valor_total,
                   t.valor_parcela,
                   t.transacao_pai_id,
                   t.numero_parcela,
                   t.total_parcelas,
                   t.data_vencimento,
                   c.nome  AS categoria_nome,
                   c.cor   AS categoria_cor
            FROM transacoes t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'financas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status = 'aberto'
              AND t.tipo = 'despesa'
              AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
              AND t.data_vencimento IS NOT NULL
              AND t.data_vencimento > %s
              AND t.data_vencimento <= %s
            ORDER BY t.data_vencimento ASC
        """

    @staticmethod
    def get_proximos_tarefas():
        """Tarefas pendentes/andamento com data_final entre amanhã e hoje+7"""
        return """
            SELECT t.id,
                   t.tarefa_sequencia,
                   t.titulo,
                   t.status,
                   t.prioridade,
                   t.data_final,
                   c.nome AS categoria_nome,
                   c.cor  AS categoria_cor
            FROM tarefas t
            LEFT JOIN categorias c ON c.id = t.categoria_id AND c.modulo = 'tarefas'
            WHERE t.usuario_id = %s
              AND t.ativo = 1
              AND t.status IN ('pendente', 'em andamento')
              AND t.data_final IS NOT NULL
              AND t.data_final > %s
              AND t.data_final <= %s
            ORDER BY t.data_final ASC,
                     CASE t.prioridade
                        WHEN 'alta'  THEN 1
                        WHEN 'media' THEN 2
                        WHEN 'baixa' THEN 3
                        ELSE 4
                     END ASC
        """

    # ==========================================================
    # RESUMO RÁPIDO (KPIs do mês corrente)
    # ==========================================================

    @staticmethod
    def get_saldo_mes():
        """Soma de receitas e despesas QUITADAS no mês corrente"""
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
              AND t.data_quitamento >= %s
              AND t.data_quitamento <= %s
        """

    @staticmethod
    def get_total_a_pagar_mes():
        """Soma de despesas EM ABERTO que vencem no mês corrente"""
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
              AND t.data_vencimento >= %s
              AND t.data_vencimento <= %s
        """

    @staticmethod
    def get_contagem_tarefas_pendentes():
        """Count de tarefas pendentes/andamento ativas"""
        return """
            SELECT COUNT(*)
            FROM tarefas
            WHERE usuario_id = %s
              AND ativo = 1
              AND status IN ('pendente', 'em andamento')
        """