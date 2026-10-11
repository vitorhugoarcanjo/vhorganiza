# rotas/pasta_categorias/services/services_categorias.py
# ==========================================================
# SERVICES DO MÓDULO DE CATEGORIAS
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class CategoriasServices:

    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    def buscar_categorias(self, usuario_id, filtros):
        """
        Busca categorias com filtros aplicados.
        Reaproveitado por todos os CRUDs (padrão 2099).
        """
        from rotas.pasta_categorias.queries import CategoriasQueries
        from rotas.pasta_categorias.filters import CategoriasFilters

        query = CategoriasQueries.get_categorias_base()
        params = [usuario_id]
        query, params = CategoriasFilters.aplicar_filtros_query(query, params, filtros)
        query += " ORDER BY c.modulo ASC, c.sequencia_categorias ASC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def buscar_categorias_por_modulo(self, usuario_id, modulo):
        """Busca categorias ativas de um módulo específico (pro <select>)"""
        self.cursor.execute("""
            SELECT id, nome, cor
            FROM categorias
            WHERE usuario_id = %s AND modulo = %s AND ativo = 1
            ORDER BY nome ASC
        """, (usuario_id, modulo))
        return self.cursor.fetchall()