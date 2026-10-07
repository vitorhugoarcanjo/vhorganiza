# rotas/pasta_orcamentos/crud/pasta_edit/validacoes.py
# ==========================================================
# EDITAR ORÇAMENTO - VALIDAÇÕES
# ==========================================================

from rotas.pasta_orcamentos.crud.pasta_insert.validacoes import (
    limpar_texto,
    parse_valor_br,
    calcular_valor_total,
)


def validar_dados_edicao(dados):
    """
    Valida os dados de edição.
    Retorna lista de erros: [{'campo': ..., 'mensagem': ...}]
    """
    erros = []

    # 1. Título
    titulo = dados.get('titulo') or ''
    if not titulo.strip():
        erros.append({'campo': 'titulo', 'mensagem': 'Título é obrigatório'})
    elif len(titulo) > 200:
        erros.append({'campo': 'titulo', 'mensagem': 'Título deve ter no máximo 200 caracteres'})

    # 2. Cliente
    cliente = dados.get('cliente') or ''
    if not cliente.strip():
        erros.append({'campo': 'cliente', 'mensagem': 'Cliente é obrigatório'})
    elif len(cliente) > 200:
        erros.append({'campo': 'cliente', 'mensagem': 'Cliente deve ter no máximo 200 caracteres'})

    # 3. Status
    status = dados.get('status') or 'rascunho'
    status_validos = ['rascunho', 'enviado', 'aprovado', 'rejeitado']
    if status not in status_validos:
        erros.append({
            'campo': 'status',
            'mensagem': f'Status inválido. Deve ser um de: {", ".join(status_validos)}'
        })

    # 4. Estrutura
    estrutura = dados.get('estrutura')
    if estrutura is not None and not isinstance(estrutura, list):
        erros.append({'campo': 'estrutura', 'mensagem': 'Estrutura deve ser uma lista'})

    return erros