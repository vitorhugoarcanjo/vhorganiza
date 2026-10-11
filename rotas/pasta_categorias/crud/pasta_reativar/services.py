# rotas/pasta_categorias/crud/pasta_reativar/services.py
# ==========================================================
# REATIVAR CATEGORIA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class ReativarCategoriaService:

    @staticmethod
    def buscar_categoria(cursor, categoria_id, usuario_id):
        """Busca categoria inativa pra reativar"""
        cursor.execute("""
            SELECT id, nome, modulo
            FROM categorias
            WHERE id = %s AND usuario_id = %s AND ativo = 0
        """, (categoria_id, usuario_id))
        return cursor.fetchone()

    @staticmethod
    def reativar_categoria(cursor, categoria_id, usuario_id):
        """Reativa a categoria"""
        cursor.execute("""
            UPDATE categorias
            SET ativo = 1,
                excluido_em = NULL,
                excluido_por = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 0
        """, (categoria_id, usuario_id))