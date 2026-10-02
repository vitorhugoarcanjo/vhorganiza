# rotas\pasta_financas\crud\pasta_edit\validacoes.py
# ==========================================================
# EDITAR TRANSAÇÃO - VALIDAÇÕES
# ==========================================================

def validar_dados_edicao(dados):
    """Valida os dados de edição"""
    erros = []
    
    # Valida descrição
    descricao = dados.get('descricao', '').strip()
    if not descricao:
        erros.append({'campo': 'descricao', 'mensagem': 'Descrição é obrigatória'})
    
    # Valida valor
    valor = dados.get('valor_total', 0)
    if isinstance(valor, str):
        valor = valor.replace('R$', '').strip().replace('.', '').replace(',', '.')
    try:
        if float(valor) <= 0:
            erros.append({'campo': 'valor_total', 'mensagem': 'Valor deve ser maior que zero'})
    except (ValueError, TypeError):
        erros.append({'campo': 'valor_total', 'mensagem': 'Valor inválido'})
    
    return erros

def converter_valor_br(valor_str):
    """Converte formato brasileiro '1.234,56' para float"""
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)