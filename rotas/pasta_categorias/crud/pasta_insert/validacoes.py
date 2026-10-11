# rotas/pasta_categorias/crud/pasta_insert/validacoes.py
# ==========================================================
# INSERIR CATEGORIA - VALIDAÇÕES
# ==========================================================


def validar_dados_insercao(dados):
    """Valida os dados antes de inserir"""
    erros = []

    # 1. Nome (obrigatório)
    nome = (dados.get('nome') or '').strip()
    if not nome:
        erros.append({'campo': 'nome', 'mensagem': 'Nome é obrigatório'})
    elif len(nome) > 100:
        erros.append({'campo': 'nome', 'mensagem': 'Nome não pode passar de 100 caracteres'})

    # 2. Módulo (obrigatório)
    modulo = dados.get('modulo') or ''
    if modulo not in ('tarefas', 'financas'):
        erros.append({'campo': 'modulo', 'mensagem': 'Módulo inválido'})

    # 3. Cor (opcional, mas se vier tem que ser válida)
    cor = (dados.get('cor') or '').strip()
    if cor and not cor.startswith('#'):
        erros.append({'campo': 'cor', 'mensagem': 'Cor inválida'})

    return erros