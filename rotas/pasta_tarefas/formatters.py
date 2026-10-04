# rotas/pasta_tarefas/formatters.py
# ==========================================================
# FORMATADORES DO MÓDULO DE TAREFAS
# ==========================================================

from utils.fomatacoes.data_reutilizavel import formatar_data


class TarefasFormatters:

    # Mapa de status pra label visual
    STATUS_LABELS = {
        'pendente':     '⏰ Pendente',
        'em andamento': '⏳ Andamento',
        'concluido':    '✅ Concluída',
    }

    PRIORIDADE_LABELS = {
        'baixa': '🟢 Baixa',
        'media': '🟡 Média',
        'alta':  '🔴 Alta',
    }

    @staticmethod
    def formatar_tarefas(tarefas_raw):
        """
        Recebe lista de tuplas do banco e devolve lista de dicionários.
        Ordem da query em TarefasQueries.get_tarefas_base():
          0 tarefa_sequencia
          1 titulo
          2 descricao
          3 status
          4 data_inicio
          5 data_final
          6 data_finalizacao
          7 categoria_id
          8 prioridade
          9 categoria_nome
          10 categoria_cor
          11 ativo
        """
        resultado = []

        for t in tarefas_raw:
            resultado.append({
                'sequencia':          t[0],
                'titulo':             t[1] or 'Sem título',
                'descricao':          t[2] or '',
                'status':             t[3] or 'pendente',
                'status_label':       TarefasFormatters.STATUS_LABELS.get(t[3], t[3] or ''),
                'data_inicio':        formatar_data(t[4]),
                'data_final':         formatar_data(t[5]),
                'data_finalizacao':   formatar_data(t[6]),
                'categoria_id':       t[7],
                'prioridade':         t[8] or 'media',
                'prioridade_label':   TarefasFormatters.PRIORIDADE_LABELS.get(t[8], t[8] or ''),
                'categoria_nome':     t[9],
                'categoria_cor':      t[10] or '#6c757d',
                'ativo':              t[11],
            })

        return resultado

    @staticmethod
    def formatar_detalhes(tarefa_raw):
        """
        Formata UMA tarefa (usado no /detalhes/<seq>).
        Ordem da query em TarefasQueries.get_detalhes_tarefa():
          0 tarefa_sequencia
          1 titulo
          2 descricao
          3 status
          4 data_inicio
          5 data_final
          6 data_finalizacao
          7 prioridade
          8 motivo_conclusao
          9 categoria_nome
          10 categoria_cor
        """
        if not tarefa_raw:
            return None

        return {
            'sequencia':        tarefa_raw[0],
            'titulo':           tarefa_raw[1] or 'Sem título',
            'descricao':        tarefa_raw[2] or 'Sem descrição',
            'status':           tarefa_raw[3],
            'status_label':     TarefasFormatters.STATUS_LABELS.get(tarefa_raw[3], tarefa_raw[3] or ''),
            'data_inicio':      formatar_data(tarefa_raw[4]),
            'data_final':       formatar_data(tarefa_raw[5]),
            'data_finalizacao': formatar_data(tarefa_raw[6]),
            'prioridade':       tarefa_raw[7],
            'prioridade_label': TarefasFormatters.PRIORIDADE_LABELS.get(tarefa_raw[7], tarefa_raw[7] or ''),
            'motivo_conclusao': tarefa_raw[8],
            'categoria':        tarefa_raw[9] or 'Sem categoria',
            'categoria_cor':    tarefa_raw[10] or '#6c757d',
        }