# rotas/pasta_financas/crud/pasta_edit/validacoes.py
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

    # 🔥 Valida valor (aceita float direto OU string BR)
    valor = dados.get('valor_total', 0)
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            erros.append({'campo': 'valor_total', 'mensagem': 'Valor deve ser maior que zero'})
    except (ValueError, TypeError):
        valor_float = 0.0
        erros.append({'campo': 'valor_total', 'mensagem': 'Valor inválido'})

    # 🔥 Validação: soma das parcelas deve bater com o valor total
    parcelas = dados.get('parcelas', [])
    if len(parcelas) > 1:
        try:
            soma = round(sum(float(p['valor']) for p in parcelas), 2)
            if abs(valor_float - soma) > 0.01:
                fmt = lambda v: f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                erros.append({
                    'campo': 'valor_total',
                    'mensagem': f'A soma das parcelas ({fmt(soma)}) precisa ser igual ao Valor Total ({fmt(valor_float)}).'
                })
        except (ValueError, TypeError, KeyError):
            erros.append({'campo': 'parcelas', 'mensagem': 'Erro ao validar valores das parcelas'})

    return erros


def converter_valor_br(valor_str):
    """
    Converte formato brasileiro '1.234,56' para float.
    🔥 Só usar quando o valor vier como STRING do form.
    """
    if not valor_str:
        return 0.0
    if isinstance(valor_str, (int, float)):
        return float(valor_str)
    valor_str = str(valor_str).replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)