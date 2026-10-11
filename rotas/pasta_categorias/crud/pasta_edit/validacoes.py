# rotas/pasta_categorias/crud/pasta_edit/validacoes.py
# ==========================================================
# EDITAR CATEGORIA - VALIDAÇÕES
# ==========================================================


def validar_dados_edicao(dados):
    """Valida os dados antes de editar"""
    erros = []

    # 1. Nome (obrigatório)
    nome = (dados.get('nome') or '').strip()
    if not nome:
        erros.append({'campo': 'nome', 'mensagem': 'Nome é obrigatório'})
    elif len(nome) > 100:
        erros.append({'campo': 'nome', 'mensagem': 'Nome não pode passar de 100 caracteres'})

    # 2. Cor (opcional, mas se vier tem que ser válida)
    cor = (dados.get('cor') or '').strip()
    if cor and not cor.startswith('#'):
        erros.append({'campo': 'cor', 'mensagem': 'Cor inválida'})

    return erros