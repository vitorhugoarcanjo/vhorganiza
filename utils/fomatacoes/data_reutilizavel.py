# utils/formatacoes.py
from datetime import datetime

# ==========================================
# FUNÇÕES LEGADAS (mantém para compatibilidade)
# ==========================================
def formatar_data(data):
    """Formata data para dd/mm/aaaa (versão legada - compatível com tarefas)"""
    if not data:
        return '-'
    if isinstance(data, str):
        if '/' in data:
            return data
        try:
            return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return data
    return data.strftime('%d/%m/%Y') if hasattr(data, 'strftime') else str(data)

def formatar_moeda(valor):
    """Formata valor para R$ 1.234,56 (versão legada)"""
    if valor is None:
        return 'R$ 0,00'
    return f'R$ {valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')


# ==========================================
# NOVAS FUNÇÕES (mais robustas)
# ==========================================
def formatar_moeda_br(valor):
    """Formata valor para R$ 1.234,56 (com try/except)"""
    if valor is None:
        return 'R$ 0,00'
    try:
        valor_float = float(valor)
        return f'R$ {valor_float:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
    except (ValueError, TypeError):
        return 'R$ 0,00'

def formatar_data_br(data_str):
    """Formata data de YYYY-MM-DD para DD/MM/YYYY"""
    if not data_str or data_str == '-':
        return '-'
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        return data_obj.strftime('%d/%m/%Y')
    except:
        return data_str

def formatar_data_hora_br(data_str):
    """Formata data/hora para DD/MM/YYYY HH:MM:SS"""
    if not data_str:
        return '-'
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
        return data_obj.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return data_str

def converter_valor_br_para_float(valor_str):
    """Converte '1.234,56' para 1234.56"""
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)