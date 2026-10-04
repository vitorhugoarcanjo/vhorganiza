# rotas/pasta_tarefas/crud/pasta_reabrir/services.py
# ==========================================================
# REABRIR TAREFA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class ReabrirTarefaService:

    @staticmethod
    def reabrir_tarefa(cursor, sequencia, user_id):
        # 🔥 Busca dados antes + id interno + status/motivo/data_finalizacao
        cursor.execute("""
            SELECT id, titulo, status, data_finalizacao, motivo_conclusao
            FROM tarefas
            WHERE tarefa_sequencia = %s AND user_id = %s AND ativo = 1
        """, (sequencia, user_id))
        tarefa = cursor.fetchone()

        if not tarefa:
            return {'success': False, 'error': 'Tarefa não encontrada ou já está ativa.'}

        id_interno = tarefa[0]
        titulo = tarefa[1] or 'Sem título'
        status_antes = tarefa[2]
        data_finalizacao_antes = tarefa[3]
        motivo_antes = tarefa[4]

        if status_antes != 'concluido':
            return {'success': False, 'error': 'Só é possível reabrir tarefas concluídas.'}

        cursor.execute("""
            UPDATE tarefas
            SET status = 'pendente',
                data_finalizacao = NULL,
                motivo_conclusao = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (id_interno, user_id))

        return {
            'success': True,
            'id_interno': id_interno,
            'titulo': titulo,
            'status_antes': status_antes,
            'data_finalizacao_antes': data_finalizacao_antes,
            'motivo_antes': motivo_antes,
        }