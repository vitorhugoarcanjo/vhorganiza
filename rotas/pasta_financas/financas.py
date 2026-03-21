from flask import Blueprint, render_template, session, request
import sqlite3
import os
from rotas.middleware.autenticacao import login_required
from datetime import date

# FUNÇÃO PARA VALIDAÇÃO DATA E TIPO
from rotas.pasta_financas.validacoes.financas.data import validacao_data


bp_financas = Blueprint('financas', __name__)
caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

@bp_financas.route('/')
@login_required
def inifinancas():
    hoje = date.today().isoformat()
    user_id = session['user_id']

    # pega filtros diretamente
    data_inicio = request.args.get('data_inicio', hoje)
    data_final = request.args.get('data_final', hoje)
    descricao = request.args.get('descricao')
    tipo = request.args.get('tipo')

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # Monta a query
    query = """
        SELECT sequencia_transacoes, id, tipo, valor_total, descricao, data_emissao, 
               categoria, status, data_vencimento
        FROM transacoes 
        WHERE user_id = ?
    """
    params = [user_id]

    if data_inicio and data_final:
        query += " AND data_emissao BETWEEN ? AND ?"
        params.extend([data_inicio, data_final])
    
    if descricao:
        query += " AND descricao LIKE ?"
        params.append(f"%{descricao}%")
    
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    query += " ORDER BY data_emissao DESC, sequencia_transacoes DESC"
    
    cursor.execute(query, params)
    transacoes_raw = cursor.fetchall()
    conexao.close()
    
    # Formata os valores para exibição
    transacoes = []
    for t in transacoes_raw:
        transacao_lista = list(t)
        # Formata o valor (índice 3) para float com 2 casas decimais
        try:
            transacao_lista[3] = float(transacao_lista[3]) if transacao_lista[3] else 0.0
        except (ValueError, TypeError):
            transacao_lista[3] = 0.0
        transacoes.append(transacao_lista)
    
    return render_template('pasta_financas/tela_financas.html', 
                          hoje=hoje, 
                          data_final=data_final, 
                          data_inicio=data_inicio,
                          transacoes=transacoes, 
                          user_nome=session.get('user_nome'))