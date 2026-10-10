# rotas/pasta_tarefas/crud/pasta_edit/services.py
# ==========================================================
# EDITAR TAREFA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class EditarTarefaService:

    # ------------------------------------------------------
    # CATEGORIAS (pro <select> do modal)
    # ------------------------------------------------------
    @staticmethod
    def buscar_categorias(cursor, usuario_id):
        try:
            cursor.execute("""
                SELECT id, nome, cor FROM categorias
                WHERE usuario_id = %s AND modulo = 'tarefas' ORDER BY nome ASC
            """, (usuario_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao buscar categorias: {e}")
            return []

    # ------------------------------------------------------
    # BUSCA BÁSICA POR SEQUÊNCIA
    # ------------------------------------------------------
    @staticmethod
    def buscar_tarefa_por_sequencia(cursor, sequencia, usuario_id):
        """
        Retorna tupla:
          0  tarefa_sequencia
          1  titulo
          2  descricao
          3  status
          4  data_inicio
          5  data_final
          6  data_finalizacao
          7  categoria_id
          8  prioridade
          9  motivo_conclusao
          10 ativo
        """
        cursor.execute("""
            SELECT tarefa_sequencia, titulo, descricao, status,
                   data_inicio, data_final, data_finalizacao,
                   categoria_id, prioridade, motivo_conclusao, ativo
            FROM tarefas
            WHERE tarefa_sequencia = %s AND usuario_id = %s
        """, (sequencia, usuario_id))
        return cursor.fetchone()

    # ------------------------------------------------------
    # ATUALIZAR
    # ------------------------------------------------------
    @staticmethod
    def atualizar_tarefa(cursor, sequencia, usuario_id, dados):
        tarefa_atual = EditarTarefaService.buscar_tarefa_por_sequencia(
            cursor, sequencia, usuario_id
        )
        if not tarefa_atual:
            return {'success': False, 'error': 'Tarefa não encontrada'}

        # Busca o ID interno
        cursor.execute("""
            SELECT id FROM tarefas
            WHERE tarefa_sequencia = %s AND usuario_id = %s
        """, (sequencia, usuario_id))
        row = cursor.fetchone()
        if not row:
            return {'success': False, 'error': 'Tarefa não encontrada'}

        id_interno = row[0]

        # 🆕 Busca o NOME da categoria ANTES
        categoria_antes_nome = '(vazio)'
        categoria_id_antes = tarefa_atual[7]
        if categoria_id_antes:
            cursor.execute("SELECT nome FROM categorias WHERE id = %s AND modulo = 'tarefas'", (categoria_id_antes,))
            c = cursor.fetchone()
            if c:
                categoria_antes_nome = c[0]

        # 🆕 Busca o NOME da categoria DEPOIS
        categoria_depois_nome = '(vazio)'
        categoria_id_depois = dados.get('categoria_id')
        if categoria_id_depois:
            cursor.execute("SELECT nome FROM categorias WHERE id = %s AND modulo = 'tarefas'", (categoria_id_depois,))
            c = cursor.fetchone()
            if c:
                categoria_depois_nome = c[0]

        # 🔥 Dados ANTES (pra auditoria)
        dados_antes = {
            'titulo':              tarefa_atual[1],
            'descricao':           tarefa_atual[2],
            'status':              tarefa_atual[3],
            'data_inicio':         str(tarefa_atual[4]) if tarefa_atual[4] else '',
            'data_final':          str(tarefa_atual[5]) if tarefa_atual[5] else '',
            'categoria_nome':      categoria_antes_nome,   # 🆕 usa o NOME
            'prioridade':          tarefa_atual[8],
        }

        # 🔥 Dados DEPOIS
        dados_depois = {
            'titulo':              dados['titulo'],
            'descricao':           dados['descricao'],
            'status':              dados['status'],
            'data_inicio':         dados.get('data_inicio') or '',
            'data_final':          dados.get('data_final') or '',
            'categoria_nome':      categoria_depois_nome,  # 🆕 usa o NOME
            'prioridade':          dados['prioridade'],
        }

        cursor.execute("""
            UPDATE tarefas
            SET titulo        = %s,
                descricao     = %s,
                status        = %s,
                prioridade    = %s,
                data_inicio   = %s,
                data_final    = %s,
                categoria_id  = %s,
                updated_at    = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s
        """, (
            dados['titulo'],
            dados['descricao'],
            dados['status'],
            dados['prioridade'],
            dados['data_inicio'],
            dados['data_final'],
            dados['categoria_id'],
            id_interno,
            usuario_id,
        ))

        return {
            'success': True,
            'id_interno': id_interno,
            'dados_antes': dados_antes,
            'dados_depois': dados_depois,
        }