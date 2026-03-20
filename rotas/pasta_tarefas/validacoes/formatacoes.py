# crud_tarefas/utils.py
from datetime import datetime

def formatar_data(data_str):
    """ Formata data de YYYY-MM-DD para DD/MM/YYYY """
    if data_str and data_str != '-':
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
            return data.strftime('%d/%m/%Y')
        except:
            return data_str
    return '-'

def formatar_tarefas(tarefas):
    """ Formata todas as datas das tarefas """
    tarefas_formatadas = []
    for tarefa in tarefas:
        tarefa_lista = list(tarefa)
        # data_inicio é o índice 3, data_fim é o índice 4
        tarefa_lista[3] = formatar_data(tarefa_lista[3])  # data_inicio
        tarefa_lista[4] = formatar_data(tarefa_lista[4])  # data_fim
        tarefas_formatadas.append(tarefa_lista)
    return tarefas_formatadas