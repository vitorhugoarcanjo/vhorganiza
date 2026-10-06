# rotas/pasta_orcamentos/filters.py
# ==========================================================
# FILTROS DO MÓDULO DE ORÇAMENTOS (idêntico ao Finanças)
# ==========================================================

from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas


class OrcamentosFilters:
    """ GERENCIA TODOS OS FILTROS DO MÓDULO ORÇAMENTOS """
    PREFIXO = 'orcamentos'

    # ==========================================================
    # DATA
    # ==========================================================
    @classmethod
    def processar_filtros_data(cls):
        data_inicio, data_fim, tipo_data = filtro_datas(date.today(), prefixo=cls.PREFIXO)

        # 🔥 CORRIGE TIPO_DATA (padrão Finanças)
        if tipo_data == 'inicio':
            tipo_data = 'emissao'

        return data_inicio, data_fim, tipo_data

    # ==========================================================
    # MOSTRAR INATIVAS
    # ==========================================================
    @classmethod
    def processar_mostrar_inativas(cls):
        from flask import request, session

        mostrar = request.args.get('mostrar_inativas')
        if mostrar is None and request.method == 'POST':
            mostrar = request.form.get('mostrar_inativas')
        if mostrar is None:
            mostrar = session.get(f'{cls.PREFIXO}_mostrar_inativas', '0')

        session[f'{cls.PREFIXO}_mostrar_inativas'] = mostrar
        return mostrar

    # ==========================================================
    # SALVAR FILTROS POST
    # ==========================================================
    @classmethod
    def salvar_filtros_post(cls, request, session):
        session[f'{cls.PREFIXO}_status']  = request.form.get('status', '')
        session[f'{cls.PREFIXO}_cliente'] = request.form.get('cliente', '')
        session[f'{cls.PREFIXO}_busca']   = request.form.get('busca', '')

        mostrar_inativas = request.form.get('mostrar_inativas')
        if mostrar_inativas in ('0', '1', '2'):
            session[f'{cls.PREFIXO}_mostrar_inativas'] = mostrar_inativas

    # ==========================================================
    # RECUPERAR FILTROS
    # ==========================================================
    @classmethod
    def recuperar_filtros(cls, session):
        return {
            'status':            session.get(f'{cls.PREFIXO}_status', ''),
            'cliente':           session.get(f'{cls.PREFIXO}_cliente', ''),
            'busca':             session.get(f'{cls.PREFIXO}_busca', ''),
            'tipo_data':         session.get(f'{cls.PREFIXO}_tipo_data', 'emissao'),
            'mostrar_inativas':  session.get(f'{cls.PREFIXO}_mostrar_inativas', '0'),
        }

    # ==========================================================
    # LIMPAR FILTROS
    # ==========================================================
    @classmethod
    def limpar_filtros(cls, session):
        chaves = [
            'status', 'cliente', 'busca',
            'tipo_data', 'mostrar_inativas',
            'data_inicio_intervalo', 'data_fim_intervalo',
            'modo', 'mes_corrente', 'dia_corrente', 'dia_referencia'
        ]
        for chave in chaves:
            session.pop(f'{cls.PREFIXO}_{chave}', None)

    # ==========================================================
    # APLICAR FILTROS NA QUERY
    # ==========================================================
    @classmethod
    def aplicar_filtros_query(cls, query, params, filtros):

        # DATA — 🔥 usa data_emissao (não created_at)
        if filtros.get('data_inicio') and filtros.get('data_fim'):
            data_ini = str(filtros['data_inicio'])[:10]
            data_fim = str(filtros['data_fim'])[:10]
            query += " AND DATE(o.data_emissao) BETWEEN %s AND %s"
            params.extend([data_ini, data_fim])

        # STATUS
        if filtros.get('status'):
            query += " AND o.status = %s"
            params.append(filtros['status'])

        # CLIENTE
        if filtros.get('cliente'):
            query += " AND o.cliente ILIKE %s"
            params.append(f"%{filtros['cliente']}%")

        # BUSCA
        if filtros.get('busca'):
            query += " AND (o.titulo ILIKE %s OR o.cliente ILIKE %s)"
            params.append(f"%{filtros['busca']}%")
            params.append(f"%{filtros['busca']}%")

        # ATIVO / INATIVO / TODAS
        mostrar_inativas = filtros.get('mostrar_inativas', '0')
        if mostrar_inativas == '1':
            query += " AND o.ativo = 0"
        elif mostrar_inativas == '2':
            pass
        else:
            query += " AND o.ativo = 1"

        return query, params