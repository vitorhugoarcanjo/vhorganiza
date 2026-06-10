from flask import render_template, session, request, redirect, url_for
from rotas.middleware.autenticacao import login_required
from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas
from utils.fomatacoes.data_reutilizavel import formatar_data_br, formatar_moeda_br
from utils.database.conexao_global import ini_conexao

@login_required
def ini_financas():
    data_hoje = date.today()
    user_id = session['user_id']

    is_htmx = request.headers.get('HX-Request') == 'true'

    # 🔥 NOVO: Pegar mostrar_inativas da URL (GET) primeiro
    mostrar_inativas_url = request.args.get('mostrar_inativas')

    # Se veio da URL, salva na sessão e já usa
    if mostrar_inativas_url is not None:
        session['financas_mostrar_inativas'] = mostrar_inativas_url

    # ===== FILTRO DE DATA (COM PREFIXO) =====
    data_inicio, data_fim, tipo_data = filtro_datas(data_hoje, prefixo='financas')
    
    # 🔥 CORREÇÃO: Se tipo_data for 'inicio' (padrão do tarefas), muda para 'emissao'
    if tipo_data == 'inicio':
        tipo_data = 'emissao'
        session['financas_tipo_data'] = 'emissao'
    else:
        session['financas_tipo_data'] = tipo_data

    # ===== PROCESSAMENTO DOS FILTROS (POST) =====
    if request.method == 'POST':
        descricao = request.form.get('descricao', '')
        tipo = request.form.get('tipo', '')
        status = request.form.get('status', '')
        categorias = request.form.getlist('categorias')
        
        # Salva na session para persistir entre requisições
        session['financas_descricao'] = descricao
        session['financas_tipo'] = tipo
        session['financas_status'] = status
        session['financas_categorias'] = categorias
        
        # 🔥 Também pega mostrar_inativas do POST
        mostrar_inativas_post = request.form.get('mostrar_inativas')
        if mostrar_inativas_post is not None:
            session['financas_mostrar_inativas'] = mostrar_inativas_post
            session.pop('financas_mostrar_inativas_url', None)
            
    
    # ===== RECUPERA OS FILTROS DA SESSION =====
    descricao = session.get('financas_descricao', '')
    tipo = session.get('financas_tipo', '')
    status = session.get('financas_status', '')
    categorias_filtro = session.get('financas_categorias', [])
    mostrar_inativas = session.get('financas_mostrar_inativas', '0')



    # ===== BUSCA CATEGORIAS DO USUÁRIO =====
    categorias_usuario = []
    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT id, nome, cor 
        FROM categorias_financas 
        WHERE user_id = %s 
        ORDER BY nome
    """, (user_id,))
    categorias_usuario = cursor.fetchall()

    # ===== MONTA A QUERY =====
    query = """
        SELECT t.sequencia_transacoes, t.id, t.tipo, t.valor_total, t.descricao, 
            t.data_emissao, c.nome AS categoria_nome, c.cor AS categoria_cor, 
            t.status, t.data_vencimento, t.ativo,
            t.numero_parcela, t.total_parcelas, t.transacao_pai_id
        FROM transacoes t
        LEFT JOIN categorias_financas c ON c.id = t.categoria_id
        WHERE t.user_id = %s
        AND (t.transacao_pai_id IS NOT NULL OR t.total_parcelas <= 1)
    """
    params = [user_id]

    # ===== FILTRO DATA =====
    if data_inicio and data_fim:
        if tipo_data == 'emissao':
            query += " AND DATE(t.data_emissao) BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        elif tipo_data == 'vencimento':
            query += " AND DATE(t.data_vencimento) BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])


    # ===== FILTRO ATIVO/INATIVO =====
    if request.method == 'POST':
        # pega do formulario se veio
        session['financas_mostrar_inativas'] = mostrar_inativas

    # APLICAR FILTRO
    if mostrar_inativas == '1':
        query += " AND t.ativo = 0"

    elif mostrar_inativas == '2':
        pass

    else:
        query += " AND t.ativo = 1"
    # ===== FILTRO ATIVO/INATIVO =====


    # ===== FILTRO CATEGORIAS =====
    if categorias_filtro:
        categorias_conditions = []
        for cat in categorias_filtro:
            if cat == 'null':
                categorias_conditions.append("(t.categoria_id IS NULL OR t.categoria_id = '')")
            else:
                categorias_conditions.append("t.categoria_id = %s")
                params.append(cat)
        
        if categorias_conditions:
            query += " AND (" + " OR ".join(categorias_conditions) + ")"

    # ===== FILTRO DESCRIÇÃO =====
    if descricao:
        query += " AND t.descricao LIKE %s"
        params.append(f"%{descricao}%")

    # ===== FILTRO TIPO =====
    if tipo:
        query += " AND t.tipo = %s"
        params.append(tipo)

    # ===== FILTRO STATUS =====
    if status:
        query += " AND t.status = %s"
        params.append(status)

    # ===== ORDENAÇÃO =====
    query += " ORDER BY t.data_emissao DESC, t.sequencia_transacoes DESC"

    cursor.execute(query, params)
    transacoes_raw = cursor.fetchall()

    # ===== FORMATA OS VALORES =====
    transacoes = []
    for t in transacoes_raw:
        transacao_lista = list(t)

        # Se for parcela (numero_parcela existe), mostra "descrição (X/Y)"
        numero_parcela = t[11] if len(t) > 11 else None
        total_parcelas = t[12] if len(t) > 12 else None
        transacao_pai_id = t[13] if len(t) > 13 else None

        descricao_original = transacao_lista[4]

        if numero_parcela and total_parcelas and total_parcelas > 1:
            transacao_lista[4] = f"{descricao_original} ({numero_parcela}/{total_parcelas})"
        
        # 🔥 Formata valor (coluna 3) - Já aplica a máscara
        transacao_lista[3] = formatar_moeda_br(transacao_lista[3])
        
        # 🔥 Formata data emissão (coluna 5)
        transacao_lista[5] = formatar_data_br(transacao_lista[5])
        
        # 🔥 Formata data vencimento (coluna 9)
        transacao_lista[9] = formatar_data_br(transacao_lista[9])
        
        transacoes.append(transacao_lista)

    if is_htmx:
        from flask import render_template_string

        # RENDERIZA SÓ A TABELA
        tabela_html = render_template('pasta_financas/_tabela_financas.html', transacoes=transacoes, data_inicio=data_inicio, data_fim=data_fim)

        # RENDERIZA OS CAMPOSDE DATA ATUALIZADOS
        inputs_html = f"""
                <input type="date" name="data_inicio" id="data_inicio_input" class="form-control" value="{data_inicio or ''}" hx-swap-oob="outerHTML:#data_inicio_input">
                <input type="date" name="data_fim" id="data_fim_input" class="form-control" value="{data_fim or ''}" hx-swap-oob="outerHTML:#data_fim_input">
                <input type="hidden" name="mostrar_inativas" value="{mostrar_inativas}" id="mostrar_inativas_input" hx-swap-oob="outerHTML:#mostrar_inativas_input">
"""
        return tabela_html + inputs_html

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
                          mostrar_inativas=mostrar_inativas,
                          user_nome=session.get('user_nome'))

        
# ===== DETALHES DA TRANSAÇÃO =====
@login_required
def detalhes_transacao(transacao_id):
    """Retorna os detalhes de uma transação via JSON"""
    conexao, cursor = ini_conexao()

        
    cursor.execute("""
        SELECT t.sequencia_transacoes, t.tipo, t.valor_total, t.descricao,
                t.data_emissao, t.data_vencimento, t.data_quitamento,
                t.status, t.numero_parcela, t.total_parcelas,
                c.nome as categoria_nome, c.cor as categoria_cor
        FROM transacoes t 
        LEFT JOIN categorias_financas c ON t.categoria_id = c.id
        WHERE t.sequencia_transacoes = %s AND t.user_id = %s
    """, (transacao_id, session['user_id']))
        
    transacao = cursor.fetchone()
    
    if not transacao:
        return {"error": "Transação não encontrada"}, 404
    
    return {
        'sequencia_transacoes': transacao[0],
        'tipo': transacao[1],
        'tipo_label': '📈 Receita' if transacao[1] == 'receita' else '📉 Despesa',
        'valor': formatar_moeda_br(transacao[2]),  # 🔥 NOVA
        'descricao': transacao[3] or 'Sem descrição',
        'data_emissao': formatar_data_br(transacao[4]),  # 🔥 NOVA
        'data_vencimento': formatar_data_br(transacao[5]),  # 🔥 NOVA
        'data_quitamento': formatar_data_br(transacao[6]) if transacao[6] else 'Não quitado',  # 🔥 NOVA
        'status': transacao[7],
        'status_label': '🔴 Aberto' if transacao[7] == 'aberto' else '✅ Quitado' if transacao[7] == 'quitado' else '💰 Recebido',
        'numero_parcela': transacao[8],
        'total_parcelas': transacao[9],
        'parcela_label': f"{transacao[8]}/{transacao[9]}" if transacao[8] and transacao[9] else 'À vista',
        'categoria': transacao[10] or 'Sem categoria',
        'categoria_cor': transacao[11] or '#6c757d'
    }


# ===== LIMPAR FILTROS =====
@login_required
def limpar_filtros():
    """ Limpa todos os filtros da sessão (igual ao tarefas) """
    
    prefixo = 'financas'

    # LIMPA FILTROS GERAIS
    session.pop('financas_descricao', None)
    session.pop('financas_tipo', None)
    session.pop('financas_status', None)
    session.pop('financas_categorias', None)
    session.pop('financas_tipo_data', None)
    session.pop('financas_mostrar_inativas', None)  # 👈 NOVO

    # LIMPA FILTROS DE DATA (COM PREFIXO)
    session.pop(f'{prefixo}_data_inicio_intervalo', None)
    session.pop(f'{prefixo}_data_fim_intervalo', None)
    session.pop(f'{prefixo}_modo', None)
    session.pop(f'{prefixo}_mes_corrente', None)
    session.pop(f'{prefixo}_dia_corrente', None)
    session.pop(f'{prefixo}_dia_referencia', None)
    session.pop(f'{prefixo}_tipo_data', None)

    return redirect(url_for('financas.ini_financas'))
