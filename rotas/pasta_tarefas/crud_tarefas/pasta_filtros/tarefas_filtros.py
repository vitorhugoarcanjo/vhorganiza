from datetime import timedelta, date, datetime
from calendar import monthrange
from flask import session, request
import os
import sqlite3

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

# FUNÇÃO - FILTRA DATAS
def filtro_datas(data_hoje):
    """ FUNÇÃO QUE PROCESSA OS FILTROS E RETORNA DATAS """

    # Limpa sessão antiga se necessário
    if 'dia_corrente' in session and isinstance(session['dia_corrente'], str) and 'GMT' in session['dia_corrente']:
        session.pop('dia_corrente', None)

    data_inicio = None
    data_fim = None

    # Inicializa os modos na sessão
    if 'modo' not in session:
        session['modo'] = 'dia'  # 'dia', 'mes_completo', 'intervalo'
    if 'mes_corrente' not in session:
        session['mes_corrente'] = (data_hoje.year, data_hoje.month)
    if 'dia_corrente' not in session:
        session['dia_corrente'] = data_hoje.strftime('%Y-%m-%d')
    if 'dia_referencia' not in session:
        session['dia_referencia'] = data_hoje.day
    if 'data_inicio_intervalo' not in session:
        session['data_inicio_intervalo'] = None
    if 'data_fim_intervalo' not in session:
        session['data_fim_intervalo'] = None

    if request.method == 'POST':
        tipo_filtro = request.form.get('tipo_filtro')

        # ===== FILTRO HOJE (reseta tudo) =====
        if tipo_filtro == 'hoje':
            data_inicio = data_hoje
            data_fim = data_hoje
            session['modo'] = 'dia'
            session['mes_corrente'] = (data_hoje.year, data_hoje.month)
            session['dia_corrente'] = data_hoje.strftime('%Y-%m-%d')
            session['dia_referencia'] = data_hoje.day
            session['data_inicio_intervalo'] = None
            session['data_fim_intervalo'] = None
        
        # ===== NAVEGAÇÃO DE DIAS =====
        elif tipo_filtro == 'ontem':
            if session['modo'] == 'intervalo':
                # Modo intervalo: mexe nas duas datas
                inicio = datetime.strptime(session['data_inicio_intervalo'], '%Y-%m-%d').date()
                fim = datetime.strptime(session['data_fim_intervalo'], '%Y-%m-%d').date()
                novo_inicio = inicio - timedelta(days=1)
                novo_fim = fim - timedelta(days=1)
                session['data_inicio_intervalo'] = novo_inicio.strftime('%Y-%m-%d')
                session['data_fim_intervalo'] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            elif session['modo'] == 'mes_completo':
                # Modo mês completo: vira intervalo deslocado
                ano, mes = session['mes_corrente']
                primeiro_dia = date(ano, mes, 1)
                ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
                novo_inicio = primeiro_dia - timedelta(days=1)
                novo_fim = ultimo_dia - timedelta(days=1)
                session['modo'] = 'intervalo'
                session['data_inicio_intervalo'] = novo_inicio.strftime('%Y-%m-%d')
                session['data_fim_intervalo'] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            else:
                # Modo dia único
                dia_atual = datetime.strptime(session['dia_corrente'], '%Y-%m-%d').date()
                dia_novo = dia_atual - timedelta(days=1)
                session['modo'] = 'dia'
                session['dia_corrente'] = dia_novo.strftime('%Y-%m-%d')
                session['dia_referencia'] = dia_novo.day
                session['mes_corrente'] = (dia_novo.year, dia_novo.month)
                data_inicio = dia_novo
                data_fim = dia_novo
        
        elif tipo_filtro == 'amanha':
            if session['modo'] == 'intervalo':
                # Modo intervalo: mexe nas duas datas
                inicio = datetime.strptime(session['data_inicio_intervalo'], '%Y-%m-%d').date()
                fim = datetime.strptime(session['data_fim_intervalo'], '%Y-%m-%d').date()
                novo_inicio = inicio + timedelta(days=1)
                novo_fim = fim + timedelta(days=1)
                session['data_inicio_intervalo'] = novo_inicio.strftime('%Y-%m-%d')
                session['data_fim_intervalo'] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            elif session['modo'] == 'mes_completo':
                # Modo mês completo: vira intervalo deslocado
                ano, mes = session['mes_corrente']
                primeiro_dia = date(ano, mes, 1)
                ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
                novo_inicio = primeiro_dia + timedelta(days=1)
                novo_fim = ultimo_dia + timedelta(days=1)
                session['modo'] = 'intervalo'
                session['data_inicio_intervalo'] = novo_inicio.strftime('%Y-%m-%d')
                session['data_fim_intervalo'] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            else:
                # Modo dia único
                dia_atual = datetime.strptime(session['dia_corrente'], '%Y-%m-%d').date()
                dia_novo = dia_atual + timedelta(days=1)
                session['modo'] = 'dia'
                session['dia_corrente'] = dia_novo.strftime('%Y-%m-%d')
                session['dia_referencia'] = dia_novo.day
                session['mes_corrente'] = (dia_novo.year, dia_novo.month)
                data_inicio = dia_novo
                data_fim = dia_novo

        # ===== INÍCIO/FIM DO MÊS =====
        elif tipo_filtro == 'mes':
            ano, mes = session['mes_corrente']
            data_inicio = date(ano, mes, 1)
            data_fim = date(ano, mes, monthrange(ano, mes)[1])
            session['modo'] = 'mes_completo'
            session['data_inicio_intervalo'] = None
            session['data_fim_intervalo'] = None

        # ===== NAVEGAÇÃO ENTRE MESES =====
        elif tipo_filtro == 'mes_passado':
            ano, mes = session['mes_corrente']
            if mes == 1:
                ano -= 1
                mes = 12
            else:
                mes -= 1
            session['mes_corrente'] = (ano, mes)
            
            if session['modo'] == 'mes_completo':
                data_inicio = date(ano, mes, 1)
                data_fim = date(ano, mes, monthrange(ano, mes)[1])
            elif session['modo'] == 'intervalo':
                dia_ref = session['dia_referencia']
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session['modo'] = 'dia'
                session['dia_corrente'] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref
            else:
                dia_ref = session['dia_referencia']
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session['dia_corrente'] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref

        elif tipo_filtro == 'mes_proximo':
            ano, mes = session['mes_corrente']
            if mes == 12:
                ano += 1
                mes = 1
            else:
                mes += 1
            session['mes_corrente'] = (ano, mes)
            
            if session['modo'] == 'mes_completo':
                data_inicio = date(ano, mes, 1)
                data_fim = date(ano, mes, monthrange(ano, mes)[1])
            elif session['modo'] == 'intervalo':
                dia_ref = session['dia_referencia']
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session['modo'] = 'dia'
                session['dia_corrente'] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref
            else:
                dia_ref = session['dia_referencia']
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session['dia_corrente'] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref

        # ===== FILTRO PERSONALIZADO =====
        else:  # 'personalizado'
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')
            if data_inicio and data_fim:
                data_obj_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_obj_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                session['modo'] = 'intervalo'
                session['data_inicio_intervalo'] = data_inicio
                session['data_fim_intervalo'] = data_fim
                session['dia_referencia'] = data_obj_inicio.day
                session['mes_corrente'] = (data_obj_inicio.year, data_obj_inicio.month)
            elif data_inicio:
                data_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                session['modo'] = 'dia'
                session['dia_corrente'] = data_inicio
                session['dia_referencia'] = data_obj.day
                session['mes_corrente'] = (data_obj.year, data_obj.month)

    return data_inicio, data_fim


# FUNÇÃO - FILTRA CATEGORIAS
def filtro_categorias(user_id):
    """ FUNÇÃO QUE FILTRA CATEGORIAS """

    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = ? ORDER BY nome
""", (user_id,))
        categorias_usuario = cursor.fetchall()


    categorias_selecionadas = request.form.getlist('categorias')    # PEGA AS CATEGORIAS SELECIONADAS (pode ser várias)

    # LÓGICA: se marcou "todas" ou não selecionou nada
    if not categorias_selecionadas:
        return [], categorias_usuario
    
    return categorias_selecionadas, categorias_usuario


# FUNÇÃO - FILTRA STATUS
def filtro_status():
    """ FUNÇÃO QUE FILTRA STATUS """
    status = request.form.get('status', '')
    tipo_filtro = request.form.get('tipo_filtro', '')
    
    # Se veio do POST (qualquer tipo), salva na sessão
    if request.method == 'POST':
        session['status_filtro'] = status
        return status
    
    # Se não, retorna o da sessão
    return session.get('status_filtro', '')



# FUNÇÃO - FILTRA PRIORIDADE
def filtro_prioridade():
    """ FUNÇÃO QUE FILTRA PRIORIDADE """
    prioridade = request.form.get('prioridade', '')
    tipo_filtro = request.form.get('tipo_filtro', '')
    
    # Se veio do POST (qualquer tipo), salva na sessão
    if request.method == 'POST':
        session['prioridade_filtro'] = prioridade
        return prioridade
    
    # Se não, retorna o da sessão
    return session.get('prioridade_filtro', '')


def filtro_descricao():
    """ FUNÇÃO QUE GERENCIA O FILTRO DE DESCRIÇÃO """
    tipo_filtro = request.form.get('tipo_filtro', '')
    descricao = request.form.get('descricao', '')
    
    # Salva se veio descrição (qualquer tipo de POST)
    if descricao:
        session['descricao_filtro'] = descricao
        return descricao
    
    return session.get('descricao_filtro', '')

