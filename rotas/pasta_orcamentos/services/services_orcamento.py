# rotas/pasta_orcamentos/services/services_orcamento.py
# ==========================================================
# SERVICES DO MÓDULO DE ORÇAMENTOS (igual Finanças)
# ==========================================================

import logging
from rotas.pasta_orcamentos.queries import OrcamentosQueries
from rotas.pasta_orcamentos.filters import OrcamentosFilters

logger = logging.getLogger(__name__)


class OrcamentosServices:

    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    # ==========================================================
    # SEQUÊNCIA VISUAL
    # ==========================================================
    def get_proxima_sequencia(self, user_id):
        """Retorna a próxima sequência de orçamentos pro usuário."""
        self.cursor.execute(
            OrcamentosQueries.get_proxima_sequencia(),
            (user_id,)
        )
        res = self.cursor.fetchone()
        return res[0] if res else 1

    # ==========================================================
    # BUSCAS
    # ==========================================================
    def buscar_orcamentos(self, user_id, filtros):
        """ BUSCA orçamentos com FILTROS """
        query = OrcamentosQueries.get_orcamentos_base()
        params = [user_id]

        # Aplica o filtro
        query, params = OrcamentosFilters.aplicar_filtros_query(query, params, filtros)

        # Ordenação
        query += " ORDER BY o.created_at DESC, o.sequencia_orcamentos DESC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def buscar_detalhes_orcamento(self, sequencia, user_id):
        self.cursor.execute(
            OrcamentosQueries.get_orcamento_detalhes(),
            (sequencia, user_id)
        )
        return self.cursor.fetchone()

    def buscar_id_interno_por_sequencia(self, sequencia, user_id):
        """Traduz sequência visual → id interno."""
        self.cursor.execute(
            OrcamentosQueries.buscar_id_interno_por_sequencia(),
            (sequencia, user_id)
        )
        res = self.cursor.fetchone()
        return res[0] if res else None