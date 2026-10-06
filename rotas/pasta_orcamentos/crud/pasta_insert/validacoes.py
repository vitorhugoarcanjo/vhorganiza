# rotas/pasta_orcamentos/crud/pasta_insert/validacoes.py
# ==========================================================
# INSERIR ORÇAMENTO - VALIDAÇÕES
# ==========================================================

def limpar_texto(valor, max_len=None):
    """Limpa e trunca texto."""
    if valor is None:
        return ''
    texto = str(valor).strip()
    if max_len and len(texto) > max_len:
        texto = texto[:max_len]
    return texto


def parse_valor_br(valor_str):
    """
    Converte 'R$ 150,00' ou '150.00' ou '150,00' → 150.0 (float).
    Retorna 0.0 em caso de erro.
    """
    if valor_str is None:
        return 0.0
    if isinstance(valor_str, (int, float)):
        return float(valor_str)

    try:
        limpo = str(valor_str).replace('R$', '').strip()
        if ',' in limpo:
            limpo = limpo.replace('.', '').replace(',', '.')
        return float(limpo)
    except (ValueError, TypeError):
        return 0.0


def calcular_valor_total(estrutura):
    """
    Percorre a estrutura (lista de blocos) e soma os valores dos blocos tipo 'valor'.
    Retorna float.
    """
    if not isinstance(estrutura, list):
        return 0.0

    total = 0.0
    for bloco in estrutura:
        if not isinstance(bloco, dict):
            continue
        if bloco.get('tipo') == 'valor':
            total += parse_valor_br(bloco.get('valor'))

    return round(total, 2)


def validar_dados_insercao(dados):
    """
    Valida os dados sanitizados antes de inserir.
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