from flask import Blueprint, render_template, session, request, redirect, url_for
import sqlite3
import os
from rotas.middleware.autenticacao import login_required
from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas

bp_financas = Blueprint('financas', __name__)
caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')


@bp_financas.route('/', methods=['GET', 'POST'])
@login_required
def inifinancas():
    data_hoje = date.today()
    user_id = session['user_id']

    # 🔥 FILTRO DE DATA (processa POST e GET)
    data_inicio, data_fim, tipo_data = filtro_datas(data_hoje, prefixo='financas')

    # ===== PROCESSA POST E SALVA NA SESSION =====
    if request.method == 'POST':
        descricao = request.form.get('descricao', '')
        tipo = request.form.get('tipo', '')
        status = request.form.get('status', '')
        categorias = request.form.getlist('categorias')
        
        session['financas_descricao'] = descricao
        session['financas_tipo'] = tipo
        session['financas_status'] = status
        session['financas_categorias'] = categorias
        
        # 🔥 NÃO FAZ REDIRECT - deixa a função filtro_datas processar o POST
    
    # ===== RECUPERA DA SESSION =====
    descricao = session.get('financas_descricao', '')
    tipo = session.get('financas_tipo', '')
    status = session.get('financas_status', '')
    categorias_filtro = session.get('financas_categorias', [])

    # ===== BUSCA CATEGORIAS DO USUÁRIO =====
    categorias_usuario = []
    with sqlite3.connect(caminho_banco) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nome, cor FROM categorias_financas WHERE user_id = ? ORDER BY nome", (user_id,))
        categorias_usuario = cur.fetchall()

    # ===== MONTA QUERY =====
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    query = """
        SELECT t.sequencia_transacoes, t.id, t.tipo, t.valor_total, t.descricao, t.data_emissao, 
               c.nome AS categoria_nome, c.cor AS categoria_cor, t.status, t.data_vencimento
        FROM transacoes t
        LEFT JOIN categorias_financas c ON c.id = t.categoria_id
        WHERE t.user_id = ?
    """
    params = [user_id]

    # ===== FILTRO DATA =====
    if data_inicio and data_fim:
        if tipo_data == 'emissao':
            query += " AND t.data_emissao BETWEEN ? AND ?"
            params.extend([data_inicio, data_fim])
        elif tipo_data == 'vencimento':
            query += " AND t.data_vencimento BETWEEN ? AND ?"
            params.extend([data_inicio, data_fim])

    # ===== FILTRO CATEGORIAS =====
    if categorias_filtro:
        categorias_conditions = []
        for cat in categorias_filtro:
            if cat == 'null':
                categorias_conditions.append("(t.categoria_id IS NULL OR t.categoria_id = '')")
            else:
                categorias_conditions.append("t.categoria_id = ?")
                params.append(cat)
        
        if categorias_conditions:
            query += " AND (" + " OR ".join(categorias_conditions) + ")"

    # ===== FILTRO DESCRIÇÃO =====
    if descricao:
        query += " AND t.descricao LIKE ?"
        params.append(f"%{descricao}%")

    # ===== FILTRO TIPO =====
    if tipo:
        query += " AND t.tipo = ?"
        params.append(tipo)

    # ===== FILTRO STATUS =====
    if status:
        query += " AND t.status = ?"
        params.append(status)

    query += " ORDER BY t.data_emissao DESC, t.sequencia_transacoes DESC"

    cursor.execute(query, params)
    transacoes_raw = cursor.fetchall()
    conexao.close()

    # Formata valores
    transacoes = []
    for t in transacoes_raw:
        transacao_lista = list(t)
        try:
            transacao_lista[3] = float(transacao_lista[3]) if transacao_lista[3] else 0.0
        except (ValueError, TypeError):
            transacao_lista[3] = 0.0
        transacoes.append(transacao_lista)

    return render_template('pasta_financas/tela_financas.html',
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          tipo_data=tipo_data,
                          descricao=descricao,
                          tipo=tipo,
                          status=status,
                          transacoes=transacoes,
                          categorias_usuario=categorias_usuario,
                          categorias_filtro=categorias_filtro,
                          user_nome=session.get('user_nome'))


@bp_financas.route('/limpar_filtros')
@login_required
def limpar_filtros():
    """ Limpa todos os filtros da sessão """

    prefixo = 'financas'

    # FILTROS GERAIS DA TELA
    session.pop('financas_descricao', None)
    session.pop('financas_tipo', None)
    session.pop('financas_status', None)
    session.pop('financas_categorias', None)

    # FILTROS DE DATA (COM PREFIXO)
    session.pop(f'{prefixo}_data_inicio_intervalo', None)
    session.pop(f'{prefixo}_data_fim_intervalo', None)
    session.pop(f'{prefixo}_modo', None)
    session.pop(f'{prefixo}_mes_corrente', None)
    session.pop(f'{prefixo}_dia_corrente', None)
    session.pop(f'{prefixo}_dia_referencia', None)
    session.pop(f'{prefixo}_tipo_data', None)

    return redirect(url_for('financas.inifinancas'))