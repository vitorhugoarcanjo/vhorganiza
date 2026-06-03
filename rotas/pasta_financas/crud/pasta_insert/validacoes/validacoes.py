from flask import jsonify
def validacao_tipo(tipo):
    if not tipo or tipo == '':
        return None, 'Escolha se é Receita ou Despesa!'
    
    if tipo not in ['receita', 'despesa']:
        return None, 'Tipo inválido! Escolha Receita ou Despesa'

    return tipo, None    