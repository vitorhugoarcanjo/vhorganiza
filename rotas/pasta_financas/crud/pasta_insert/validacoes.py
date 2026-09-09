# ==========================================================
# INSERIR TRANSAÇÃO - VALIDAÇÕES
# ==========================================================

def validar_dados_insercao(dados):
    """Valida os dados antes de inserir"""
    erros = []
    
    # Valida tipo
    tipo = dados.get('tipo')
    if not tipo:
        erros.append({'campo': 'tipo', 'mensagem': 'Selecione o tipo (Receita ou Despesa)'})
    elif tipo not in ['receita', 'despesa']:
        erros.append({'campo': 'tipo', 'mensagem': 'Tipo inválido'})
    
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
    
    # Valida total parcelas
    total_parcelas = dados.get('total_parcelas', 1)
    try:
        total_parcelas = int(total_parcelas)
        if total_parcelas < 1 or total_parcelas > 100:
            erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas inválido (1-100)'})
    except (ValueError, TypeError):
        erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas inválido'})
    
    return erros

def converter_valor_br(valor_str):
    """Converte formato brasileiro '1.234,56' para float"""
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)