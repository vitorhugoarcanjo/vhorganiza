# crud_tarefas/utils.py
from datetime import datetime
from utils.fomatacoes.data_reutilizavel import formatar_data

def formatar_tarefas(tarefas):
    """ Formata todas as datas das tarefas """
    tarefas_formatadas = []
    for tarefa in tarefas:
        tarefa_lista = list(tarefa)
        
        # data_inicio é o índice 3
        if len(tarefa_lista) > 4:
            tarefa_lista[4] = formatar_data(tarefa_lista[4])
        
        # data_fim (prazo) é o índice 5
        if len(tarefa_lista) > 5:
            tarefa_lista[5] = formatar_data(tarefa_lista[5])
        
        # data_finalizacao é o índice 5 (NOVO)
        if len(tarefa_lista) > 6:
            tarefa_lista[6] = formatar_data(tarefa_lista[6])
        
        tarefas_formatadas.append(tarefa_lista)
    return tarefas_formatadas