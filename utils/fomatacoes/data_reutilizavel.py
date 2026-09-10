from datetime import datetime, date
from zoneinfo import ZoneInfo

# Constantes de Fuso Horário
FUSO_CUIABA = ZoneInfo("America/Cuiaba")


# ==========================================
# 1. MÉTODOS DE DATA ATUAL (TIMEZONE)
# ==========================================
def obter_hoje_cuiaba() -> str:
    """Retorna a data atual no fuso de Cuiabá formatada como YYYY-MM-DD."""
    return datetime.now(FUSO_CUIABA).strftime('%Y-%m-%d')


def obter_agora_cuiaba() -> datetime:
    """Retorna o objeto datetime completo no fuso de Cuiabá."""
    return datetime.now(FUSO_CUIABA)


# ==========================================
# 2. FUNÇÕES LEGADAS (Compatibilidade)
# ==========================================
def formatar_data(data):
    """Formata data para dd/mm/aaaa (versão legada)"""
    if not data:
        return '-'
    if isinstance(data, str):
        if '/' in data:
            return data
        try:
            return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return data
    return data.strftime('%d/%m/%Y') if hasattr(data, 'strftime') else str(data)


def formatar_moeda(valor):
    """Formata valor para R$ 1.234,56 (versão legada)"""
    if valor is None:
        return 'R$ 0,00'
    return f"R$ {valor:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')


# ==========================================
# 3. NOVAS FUNÇÕES (Robustas)
# ==========================================
def formatar_moeda_br(valor) -> str:
    """Formata valor para R$ 1.234,56 usando f-string limpa"""
    if valor is None:
        return 'R$ 0,00'
    try:
        valor_float = float(valor)
        # Formata com separador de milhar por ponto e decimal por vírgula
        return f"R$ {valor_float:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except (ValueError, TypeError):
        return 'R$ 0,00'


def formatar_data_br(data_str) -> str:
    """Formata data de YYYY-MM-DD para DD/MM/YYYY"""
    if not data_str or data_str == '-':
        return '-'

    if isinstance(data_str, (date, datetime)):
        return data_str.strftime('%d/%m/%Y')

    try:
        data_obj = datetime.strptime(str(data_str).strip(), '%Y-%m-%d')
        return data_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return str(data_str)


def formatar_data_hora_br(data_str) -> str:
    """Formata data/hora para DD/MM/YYYY HH:MM:SS"""
    if not data_str:
        return '-'
    if isinstance(data_str, datetime):
        return data_str.strftime('%d/%m/%Y %H:%M:%S')
    try:
        data_obj = datetime.strptime(str(data_str).strip(), '%Y-%m-%d %H:%M:%S')
        return data_obj.strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return str(data_str)


def converter_valor_br_para_float(valor_str) -> float:
    """Converte '1.234,56' ou 'R$ 1.234,56' para 1234.56"""
    if not valor_str:
        return 0.0
    try:
        texto_limpo = str(valor_str).replace('R$', '').strip()
        texto_limpo = texto_limpo.replace('.', '').replace(',', '.')
        return float(texto_limpo)
    except (ValueError, TypeError):
        return 0.0