# rotas/pasta_orcamentos/crud/pasta_reativar/services.py
# ==========================================================
# REATIVAR ORÇAMENTO - SERVICE
# ==========================================================

import logging

from rotas.pasta_orcamentos.queries import OrcamentosQueries

logger = logging.getLogger(__name__)


class ReativarOrcamentoService:

    # ==========================================================
    # BUSCAR ORÇAMENTO INATIVO
    # ==========================================================
    @staticmethod
    def buscar_orcamento_inativo(cursor, sequencia, user_id):
        """Busca orçamento inativo pela sequência. Retorna dict ou None."""
        cursor.execute("""
            SELECT id, titulo
            FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 0
        """, (sequencia, user_id))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'id_interno': row[0],
            'titulo':     row[1] or '',
        }

    # ==========================================================
    # REATIVAR ORÇAMENTO
    # ==========================================================
    @staticmethod
    def reativar_orcamento(cursor, sequencia, user_id):
        """
        Reativa um orçamento (soft undelete).
        Retorna (sucesso, resultado_ou_erro).
        """
        try:
            # 1. Busca orçamento inativo
            dados = ReativarOrcamentoService.buscar_orcamento_inativo(cursor, sequencia, user_id)
            if not dados:
                return False, 'Orçamento não encontrado ou já está ativo'

            # 2. UPDATE ativo = 1
            cursor.execute(
                OrcamentosQueries.reativar_orcamento(),
                (sequencia, user_id)
            )

            return True, {
                'id_interno': dados['id_interno'],
                'titulo':     dados['titulo'],
            }

        except Exception as e:
            msg = f'Erro ao reativar orçamento: {str(e)}'
            logger.error(msg)
            return False, msg