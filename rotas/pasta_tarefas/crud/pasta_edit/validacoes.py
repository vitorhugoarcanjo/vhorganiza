# rotas/pasta_tarefas/crud/pasta_edit/validacoes.py
# ==========================================================
# EDITAR TAREFA - VALIDAÇÕES
# ==========================================================

from datetime import datetime


def validar_dados_edicao(dados):
    """Valida os dados antes de atualizar"""
    erros = []

    # 1. Título (obrigatório)
    titulo = (dados.get('titulo') or '').strip()
    if not titulo:
        erros.append({'campo': 'titulo', 'mensagem': 'Título é obrigatório'})
    elif len(titulo) > 200:
        erros.append({'campo': 'titulo', 'mensagem': 'Título não pode passar de 200 caracteres'})

    # 2. Descrição (obrigatória)
    descricao = (dados.get('descricao') or '').strip()
    if not descricao:
        erros.append({'campo': 'descricao', 'mensagem': 'Descrição é obrigatória'})

    # 3. Data de início (obrigatória)
    data_inicio = dados.get('data_inicio')
    if not data_inicio:
        erros.append({'campo': 'data_inicio', 'mensagem': 'Data de início é obrigatória'})
    else:
        try:
            datetime.strptime(str(data_inicio), '%Y-%m-%d')
        except ValueError:
            erros.append({'campo': 'data_inicio', 'mensagem': 'Data de início inválida'})

    # 4. Status
    status = dados.get('status') or 'pendente'
    if status not in ('pendente', 'em andamento', 'concluido'):
        erros.append({'campo': 'status', 'mensagem': 'Status inválido'})

    # 5. Prioridade
    prioridade = dados.get('prioridade') or 'media'
    if prioridade not in ('baixa', 'media', 'alta'):
        erros.append({'campo': 'prioridade', 'mensagem': 'Prioridade inválida'})

    # 6. Data final (opcional)
    data_final = dados.get('data_final')
    if data_final:
        try:
            datetime.strptime(str(data_final), '%Y-%m-%d')
        except ValueError:
            erros.append({'campo': 'data_final', 'mensagem': 'Data final inválida'})

    return erros