from flask import jsonify
def validacao_campos_obrigatorios(tipo):
    """Valida campos obrigatórios das finanças"""
    erros = []

    # VALIDAÇÃO DO ---- TIPO -----
    if not tipo or tipo == '':
        erros.append('Escolha se é Receita ou Despesa!')
    
    elif tipo not in ['receita', 'despesa']:
        erros.append('Tipo inválido! Escolha Receita ou Despesa')

    return erros