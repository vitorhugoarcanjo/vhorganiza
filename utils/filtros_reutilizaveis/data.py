from datetime import timedelta, date, datetime
from calendar import monthrange
from flask import session, request


def filtro_datas(data_hoje, prefixo='tarefas'):
    """
    FUNÇÃO QUE PROCESSA OS FILTROS E RETORNA DATAS E TIPO
    COM PREFIXO PARA ISOLAR POR TELA (tarefas, financas, dashboard)
    """

    # ===== PREFIXO DINÂMICO =====
    def s(chave):
        return f"{prefixo}_{chave}"

    # ===== LIMPEZA DE BUG ANTIGO =====
    if s('dia_corrente') in session and isinstance(session[s('dia_corrente')], str) and 'GMT' in session[s('dia_corrente')]:
        session.pop(s('dia_corrente'), None)

    data_inicio = None
    data_fim = None
    tipo_data = session.get(s('tipo_data'), 'inicio')

    # ===== PADRÃO DIA ATUAL (quando não há filtros) =====
    if (request.method == 'GET' and 
        not request.args.get('tipo_filtro') and 
        not request.args.get('data_inicio') and 
        not request.args.get('data_fim') and
        not session.get(s('modo')) and
        not session.get(s('data_inicio_intervalo'))):
        
        data_inicio = data_hoje.strftime('%Y-%m-%d')
        data_fim = data_hoje.strftime('%Y-%m-%d')
        
        session[s('modo')] = 'dia'
        session[s('mes_corrente')] = (data_hoje.year, data_hoje.month)
        session[s('dia_corrente')] = data_inicio
        session[s('dia_referencia')] = data_hoje.day
        session[s('data_inicio_intervalo')] = data_inicio
        session[s('data_fim_intervalo')] = data_fim
        session[s('tipo_data')] = tipo_data
        
        return data_inicio, data_fim, tipo_data

    # ===== INICIALIZA OS MODOS NA SESSÃO =====
    if s('modo') not in session:
        session[s('modo')] = 'dia'
    if s('mes_corrente') not in session:
        session[s('mes_corrente')] = (data_hoje.year, data_hoje.month)
    if s('dia_corrente') not in session:
        session[s('dia_corrente')] = data_hoje.strftime('%Y-%m-%d')
    if s('dia_referencia') not in session:
        session[s('dia_referencia')] = data_hoje.day
    if s('data_inicio_intervalo') not in session:
        session[s('data_inicio_intervalo')] = None
    if s('data_fim_intervalo') not in session:
        session[s('data_fim_intervalo')] = None

    # ===== POST =====
    if request.method == 'POST':
        tipo_filtro = request.form.get('tipo_filtro')
        
        if request.form.get('tipo_data'):
            tipo_data = request.form.get('tipo_data')
            session[s('tipo_data')] = tipo_data

        # ===== FILTRO HOJE =====
        if tipo_filtro == 'hoje':
            data_inicio = data_hoje
            data_fim = data_hoje
            session[s('modo')] = 'dia'
            session[s('mes_corrente')] = (data_hoje.year, data_hoje.month)
            session[s('dia_corrente')] = data_hoje.strftime('%Y-%m-%d')
            session[s('dia_referencia')] = data_hoje.day
            session[s('data_inicio_intervalo')] = None
            session[s('data_fim_intervalo')] = None
        
        # ===== NAVEGAÇÃO DE DIAS =====
        elif tipo_filtro == 'ontem':
            if session[s('modo')] == 'intervalo':
                inicio = datetime.strptime(session[s('data_inicio_intervalo')], '%Y-%m-%d').date()
                fim = datetime.strptime(session[s('data_fim_intervalo')], '%Y-%m-%d').date()
                novo_inicio = inicio - timedelta(days=1)
                novo_fim = fim - timedelta(days=1)
                session[s('data_inicio_intervalo')] = novo_inicio.strftime('%Y-%m-%d')
                session[s('data_fim_intervalo')] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            elif session[s('modo')] == 'mes_completo':
                ano, mes = session[s('mes_corrente')]
                primeiro_dia = date(ano, mes, 1)
                ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
                novo_inicio = primeiro_dia - timedelta(days=1)
                novo_fim = ultimo_dia - timedelta(days=1)
                session[s('modo')] = 'intervalo'
                session[s('data_inicio_intervalo')] = novo_inicio.strftime('%Y-%m-%d')
                session[s('data_fim_intervalo')] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            else:
                dia_atual = datetime.strptime(session[s('dia_corrente')], '%Y-%m-%d').date()
                dia_novo = dia_atual - timedelta(days=1)
                session[s('modo')] = 'dia'
                session[s('dia_corrente')] = dia_novo.strftime('%Y-%m-%d')
                session[s('dia_referencia')] = dia_novo.day
                session[s('mes_corrente')] = (dia_novo.year, dia_novo.month)
                data_inicio = dia_novo
                data_fim = dia_novo
        
        elif tipo_filtro == 'amanha':
            if session[s('modo')] == 'intervalo':
                inicio = datetime.strptime(session[s('data_inicio_intervalo')], '%Y-%m-%d').date()
                fim = datetime.strptime(session[s('data_fim_intervalo')], '%Y-%m-%d').date()
                novo_inicio = inicio + timedelta(days=1)
                novo_fim = fim + timedelta(days=1)
                session[s('data_inicio_intervalo')] = novo_inicio.strftime('%Y-%m-%d')
                session[s('data_fim_intervalo')] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            elif session[s('modo')] == 'mes_completo':
                ano, mes = session[s('mes_corrente')]
                primeiro_dia = date(ano, mes, 1)
                ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
                novo_inicio = primeiro_dia + timedelta(days=1)
                novo_fim = ultimo_dia + timedelta(days=1)
                session[s('modo')] = 'intervalo'
                session[s('data_inicio_intervalo')] = novo_inicio.strftime('%Y-%m-%d')
                session[s('data_fim_intervalo')] = novo_fim.strftime('%Y-%m-%d')
                data_inicio = novo_inicio
                data_fim = novo_fim
            else:
                dia_atual = datetime.strptime(session[s('dia_corrente')], '%Y-%m-%d').date()
                dia_novo = dia_atual + timedelta(days=1)
                session[s('modo')] = 'dia'
                session[s('dia_corrente')] = dia_novo.strftime('%Y-%m-%d')
                session[s('dia_referencia')] = dia_novo.day
                session[s('mes_corrente')] = (dia_novo.year, dia_novo.month)
                data_inicio = dia_novo
                data_fim = dia_novo

        # ===== INÍCIO/FIM DO MÊS =====
        elif tipo_filtro == 'mes':
            ano, mes = session[s('mes_corrente')]
            data_inicio = date(ano, mes, 1)
            data_fim = date(ano, mes, monthrange(ano, mes)[1])
            session[s('modo')] = 'mes_completo'
            session[s('data_inicio_intervalo')] = None
            session[s('data_fim_intervalo')] = None

        # ===== NAVEGAÇÃO ENTRE MESES =====
        elif tipo_filtro == 'mes_passado':
            ano, mes = session[s('mes_corrente')]
            if mes == 1:
                ano -= 1
                mes = 12
            else:
                mes -= 1
            session[s('mes_corrente')] = (ano, mes)
            
            if session[s('modo')] == 'mes_completo':
                data_inicio = date(ano, mes, 1)
                data_fim = date(ano, mes, monthrange(ano, mes)[1])
            elif session[s('modo')] == 'intervalo':
                dia_ref = session[s('dia_referencia')]
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session[s('modo')] = 'dia'
                session[s('dia_corrente')] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref
            else:
                dia_ref = session[s('dia_referencia')]
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session[s('dia_corrente')] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref

        elif tipo_filtro == 'mes_proximo':
            ano, mes = session[s('mes_corrente')]
            if mes == 12:
                ano += 1
                mes = 1
            else:
                mes += 1
            session[s('mes_corrente')] = (ano, mes)
            
            if session[s('modo')] == 'mes_completo':
                data_inicio = date(ano, mes, 1)
                data_fim = date(ano, mes, monthrange(ano, mes)[1])
            elif session[s('modo')] == 'intervalo':
                dia_ref = session[s('dia_referencia')]
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session[s('modo')] = 'dia'
                session[s('dia_corrente')] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref
            else:
                dia_ref = session[s('dia_referencia')]
                ultimo_dia = monthrange(ano, mes)[1]
                if dia_ref > ultimo_dia:
                    dia_ref = ultimo_dia
                data_ref = date(ano, mes, dia_ref)
                session[s('dia_corrente')] = data_ref.strftime('%Y-%m-%d')
                data_inicio = data_ref
                data_fim = data_ref

        # ===== FILTRO PERSONALIZADO (consultar) =====
        elif tipo_filtro == 'consultar' or not tipo_filtro:
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')
            if data_inicio and data_fim:
                data_obj_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_obj_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                session[s('modo')] = 'intervalo'
                session[s('data_inicio_intervalo')] = data_inicio
                session[s('data_fim_intervalo')] = data_fim
                session[s('dia_referencia')] = data_obj_inicio.day
                session[s('mes_corrente')] = (data_obj_inicio.year, data_obj_inicio.month)
            elif data_inicio:
                data_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                session[s('modo')] = 'dia'
                session[s('dia_corrente')] = data_inicio
                session[s('dia_referencia')] = data_obj.day
                session[s('mes_corrente')] = (data_obj.year, data_obj.month)
                data_fim = data_inicio

    # ===== RECUPERA VALORES DA SESSÃO =====
    if not data_inicio and session.get(s('data_inicio_intervalo')):
        data_inicio = session[s('data_inicio_intervalo')]
    if not data_fim and session.get(s('data_fim_intervalo')):
        data_fim = session[s('data_fim_intervalo')]
    
    if not data_inicio and session.get(s('modo')) == 'dia' and session.get(s('dia_corrente')):
        data_inicio = session[s('dia_corrente')]
        data_fim = session[s('dia_corrente')]
    elif not data_inicio and session.get(s('modo')) == 'mes_completo' and session.get(s('mes_corrente')):
        ano, mes = session[s('mes_corrente')]
        data_inicio = date(ano, mes, 1).strftime('%Y-%m-%d')
        data_fim = date(ano, mes, monthrange(ano, mes)[1]).strftime('%Y-%m-%d')

    return data_inicio, data_fim, tipo_data