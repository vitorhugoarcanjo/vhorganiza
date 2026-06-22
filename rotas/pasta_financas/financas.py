from flask import render_template, session, request, redirect, url_for
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from .filters import FinancasFilters
from .services.services_financas import FinancasServices
from .formatters import FinancasFormatters

@login_required
def ini_financas():
    """ Página principal de finanças """
    user_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. PROCESSA FILTROS
    if request.method == 'POST':
        FinancasFilters.salvar_filtros_post(request, session)

    data_inicio, data_fim, tipo_data = FinancasFilters.processar_filtros_data()
    session['financas_tipo_data'] = tipo_data

    filtros = FinancasFilters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data
    })            
    
    # 2. Busca dados
    conexao, cursor = ini_conexao()
    service = FinancasServices(conexao, cursor)

    # Busca categorias (só se não for HTMX)
    categorias_usuario = []
    if not is_htmx:
        categorias_usuario = service.buscar_categorias(user_id)

    # BUSCA TRANSACOES
    transacoes_raw = service.buscar_transacoes(user_id, filtros)
    transacoes = FinancasFormatters.formatar_transacoes(transacoes_raw)
    

    # 3. Renderiza para o HTMX
    if is_htmx:
        return _renderizar_htmx(transacoes, data_inicio, data_fim, filtros)

    return render_template('pasta_financas/tela_financas.html',
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          tipo_data=tipo_data,
                          descricao=filtros['descricao'],
                          tipo=filtros['tipo'],
                          status=filtros['status'],
                          transacoes=transacoes,
                          categorias_usuario=categorias_usuario,
                          categorias_filtro=filtros['categorias'],
                          mostrar_inativas=filtros['mostrar_inativas'],
                          user_nome=session.get('user_nome'))


def _renderizar_htmx(transacoes, data_inicio, data_fim, filtros):
    """ RENDERIZA APENAS A TABELA PARA HTMX """
    tabela_html = render_template('pasta_financas/_tabela_financas.html',
                                  transacoes=transacoes,
                                  data_inicio=data_inicio,
                                  data_fim=data_fim)
    
    inputs_html = f"""
        <input type="date" name="data_inicio" id="data_inicio_input" 
               class="form-control" value="{data_inicio or ''}" 
               hx-swap-oob="outerHTML:#data_inicio_input">
        <input type="date" name="data_fim" id="data_fim_input" 
               class="form-control" value="{data_fim or ''}" 
               hx-swap-oob="outerHTML:#data_fim_input">
        <input type="hidden" name="mostrar_inativas" 
               value="{filtros['mostrar_inativas']}" 
               id="mostrar_inativas_input" 
               hx-swap-oob="outerHTML:#mostrar_inativas_input">
"""
    
    return tabela_html + inputs_html


# DETALHES DA TRANSAÇÃO
@login_required
def detalhes_transacao(transacao_id):
    """ Detalhes da transação via JSON """
    conexao, cursor = ini_conexao()
    service = FinancasServices(conexao, cursor)
    
    transacao = service.buscar_detalhes_transacao(transacao_id, session['user_id'])
    if not transacao:
        return {"error": "Transação não encontrada"}, 404
    
    return FinancasFormatters.formatar_detalhes(transacao)

# LIMPA FILTRO
@login_required
def limpar_filtros():
    """ Limpa todos os filtros """
    FinancasFilters.limpar_filtros(session)
    return redirect(url_for('financas.ini_financas'))