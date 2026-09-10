# ==========================================================
# INSERIR TRANSAÇÃO - VALIDAÇÕES
# ==========================================================

from datetime import datetime


def converter_valor_br(valor):
    """
    Converte formato brasileiro '1.234,56' ou entrada genérica para float.
    Retorna 0.0 caso ocorra falha na conversão.
    """
    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        valor_str = str(valor).replace('R$', '').strip()
        # Se contiver vírgula, assume formato BR (ex: 1.234,56 -> 1234.56)
        if ',' in valor_str:
            valor_str = valor_str.replace('.', '').replace(',', '.')
        return float(valor_str)
    except (ValueError, TypeError):
        return 0.0


def validar_dados_insercao(dados):
    """Valida os dados sanitizados antes de prosseguir com a inserção"""
    erros = []

    # 1. Valida tipo
    tipo = dados.get('tipo')
    if not tipo:
        erros.append({'campo': 'tipo', 'mensagem': 'Selecione o tipo (Receita ou Despesa)'})
    elif tipo not in ['receita', 'despesa']:
        erros.append({'campo': 'tipo', 'mensagem': 'Tipo inválido'})

    # 2. Valida descrição
    descricao = str(dados.get('descricao') or '').strip()
    if not descricao:
        erros.append({'campo': 'descricao', 'mensagem': 'Descrição é obrigatória'})

    # 3. Valida valor total
    valor = dados.get('valor_total', 0.0)
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            erros.append({'campo': 'valor_total', 'mensagem': 'Valor deve ser maior que zero'})
    except (ValueError, TypeError):
        erros.append({'campo': 'valor_total', 'mensagem': 'Valor informado é inválido'})

    # 4. Valida parcelas
    try:
        total_parcelas = int(dados.get('total_parcelas', 1))
        if total_parcelas < 1 or total_parcelas > 100:
            erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas deve ser entre 1 e 100'})
    except (ValueError, TypeError):
        erros.append({'campo': 'total_parcelas', 'mensagem': 'Número de parcelas inválido'})

    # 5. Valida formato das datas (Evita quebra no PostgreSQL ao tentar inserir string malformada)
    for campo_data in ['data_emissao', 'data_vencimento', 'primeiro_vencimento']:
        val_data = dados.get(campo_data)
        if val_data:
            try:
                datetime.strptime(str(val_data), '%Y-%m-%d')
            except ValueError:
                erros.append({'campo': campo_data, 'mensagem': f'Data inválida no campo {campo_data}'})

    return erros