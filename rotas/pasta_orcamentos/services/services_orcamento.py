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

    def buscar_orcamentos(self, user_id, filtros):
        """ BUSCA orçamentos com FILTROS """
        query = OrcamentosQueries.get_orcamentos_base()
        params = [user_id]

        # Aplica o filtro
        query, params = OrcamentosFilters.aplicar_filtros_query(query, params, filtros)

        # Ordenação
        query += " ORDER BY o.created_at DESC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def buscar_detalhes_orcamento(self, orcamento_id, user_id):
        self.cursor.execute(
            OrcamentosQueries.get_orcamento_detalhes(),
            (orcamento_id, user_id)
        )
        return self.cursor.fetchone()