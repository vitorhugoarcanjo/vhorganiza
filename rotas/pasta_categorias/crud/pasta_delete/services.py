# rotas/pasta_categorias/crud/pasta_delete/services.py
# ==========================================================
# INATIVAR CATEGORIA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class InativarCategoriaService:

    @staticmethod
    def buscar_categoria(cursor, categoria_id, usuario_id):
        """Busca categoria ativa pra inativar"""
        cursor.execute("""
            SELECT id, nome, modulo
            FROM categorias
            WHERE id = %s AND usuario_id = %s AND ativo = 1
        """, (categoria_id, usuario_id))
        return cursor.fetchone()

    @staticmethod
    def inativar_categoria(cursor, categoria_id, usuario_id):
        """Inativa a categoria (soft delete)"""
        cursor.execute("""
            UPDATE categorias
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 1
        """, (usuario_id, categoria_id, usuario_id))