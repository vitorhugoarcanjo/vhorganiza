# rotas/pasta_tarefas/crud/pasta_concluir/services.py
# ==========================================================
# CONCLUIR TAREFA - SERVICES
# ==========================================================

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class ConcluirTarefaService:

    @staticmethod
    def agora_cuiaba():
        """Retorna 'YYYY-MM-DD HH:MM:SS' no fuso Cuiabá (-4)"""
        fuso = timezone(timedelta(hours=-4))
        return datetime.now(fuso).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def concluir_tarefa(cursor, sequencia, usuario_id, motivo):
        # 🔥 Busca dados antes + id interno
        cursor.execute("""
            SELECT id, titulo, status FROM tarefas
            WHERE tarefa_sequencia = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, usuario_id))
        tarefa = cursor.fetchone()

        if not tarefa:
            return {'success': False, 'error': 'Tarefa não encontrada ou já inativada.'}

        id_interno = tarefa[0]
        titulo = tarefa[1] or 'Sem título'
        status_antes = tarefa[2]

        if status_antes == 'concluido':
            return {'success': False, 'error': 'Tarefa já está concluída.'}

        agora = ConcluirTarefaService.agora_cuiaba()

        cursor.execute("""
            UPDATE tarefas
            SET status = 'concluido',
                data_finalizacao = %s,
                updated_at = %s,
                motivo_conclusao = %s
            WHERE id = %s AND usuario_id = %s
        """, (
            agora,
            agora,
            motivo if motivo else None,
            id_interno,
            usuario_id,
        ))

        return {
            'success': True,
            'id_interno': id_interno,
            'titulo': titulo,
            'status_antes': status_antes,
            'data_finalizacao': agora,
        }