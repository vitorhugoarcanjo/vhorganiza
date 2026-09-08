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
        float(valor)
    except (ValueError, TypeError):
        erros.append({'campo': 'valor_total', 'mensagem': 'Valor inválido'})
    
    # Valida total parcelas
    try:
        total_parcelas = int(dados.get('total_parcelas', 1))
        if total_parcelas < 1 or total_parcelas > 100:
            erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas inválido (1-100)'})
    except (ValueError, TypeError):
        erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas inválido'})
    
    return erros