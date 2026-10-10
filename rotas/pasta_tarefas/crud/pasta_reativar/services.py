# rotas/pasta_tarefas/crud/pasta_reativar/services.py
# ==========================================================
# REATIVAR TAREFA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class ReativarTarefaService:

    @staticmethod
    def reativar_tarefa(cursor, sequencia, usuario_id):
        # Busca dados antes + id interno
        cursor.execute("""
            SELECT id, titulo FROM tarefas
            WHERE tarefa_sequencia = %s AND usuario_id = %s AND ativo = 0
        """, (sequencia, usuario_id))
        tarefa = cursor.fetchone()

        if not tarefa:
            return {'success': False, 'error': 'Tarefa não encontrada ou já está ativa.'}

        id_interno = tarefa[0]
        titulo = tarefa[1] or 'Sem título'

        cursor.execute("""
            UPDATE tarefas
            SET ativo = 1,
                excluido_em = NULL,
                excluido_por = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s AND ativo = 0
        """, (id_interno, usuario_id))

        return {
            'success': True,
            'id_interno': id_interno,
            'titulo': titulo,
        }