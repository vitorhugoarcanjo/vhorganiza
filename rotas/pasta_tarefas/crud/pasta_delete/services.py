# rotas/pasta_tarefas/crud/pasta_delete/services.py
# ==========================================================
# INATIVAR TAREFA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class DeleteTarefaService:

    @staticmethod
    def inativar_tarefa(cursor, sequencia, usuario_id):
        # Busca dados antes + id interno
        cursor.execute("""
            SELECT id, titulo FROM tarefas
            WHERE tarefa_sequencia = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, usuario_id))
        tarefa = cursor.fetchone()

        if not tarefa:
            return {'success': False, 'error': 'Tarefa não encontrada ou já inativada.'}

        id_interno = tarefa[0]
        titulo = tarefa[1] or 'Sem título'

        cursor.execute("""
            UPDATE tarefas
            SET ativo = 0,
                excluido_em = CURRENT_TIMESTAMP,
                excluido_por = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s
        """, (usuario_id, id_interno, usuario_id))

        return {
            'success': True,
            'id_interno': id_interno,
            'titulo': titulo,
        }