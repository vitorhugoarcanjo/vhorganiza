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
        """ PROCESSA FILTROS DE DATA """
        data_inicio, data_fim, tipo_data = filtro_datas(date.today(), prefixo=cls.PREFIXO)
        return data_inicio, data_fim, tipo_data

    # ==========================================================
    # SALVAR FILTROS DO POST NA SESSION
    # ==========================================================
    @classmethod
    def salvar_filtros_post(cls, request, session):
        """ SALVAR FILTROS DO POST NA SESSION """
        session[f'{cls.PREFIXO}_status']  = request.form.get('status', '')
        session[f'{cls.PREFIXO}_cliente'] = request.form.get('cliente', '')
        session[f'{cls.PREFIXO}_busca']   = request.form.get('busca', '')

    # ==========================================================
    # RECUPERAR FILTROS DA SESSION
    # ==========================================================
    @classmethod
    def recuperar_filtros(cls, session):
        """ RECUPERA FILTROS DA SESSION """
        return {
            'status':  session.get(f'{cls.PREFIXO}_status', ''),
            'cliente': session.get(f'{cls.PREFIXO}_cliente', ''),
            'busca':   session.get(f'{cls.PREFIXO}_busca', ''),
            'tipo_data': session.get(f'{cls.PREFIXO}_tipo_data', 'emissao'),
        }

    # ==========================================================
    # LIMPAR FILTROS
    # ==========================================================
    @classmethod
    def limpar_filtros(cls, session):
        """ LIMPA TODOS OS FILTROS """
        chaves = [
            'status', 'cliente', 'busca',
            'tipo_data',
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
        """ APLICA TODOS OS FILTROS QUERY """

        # FILTRO DATA
        if filtros.get('data_inicio') and filtros.get('data_fim'):
            data_ini = str(filtros['data_inicio'])[:10]
            data_fim = str(filtros['data_fim'])[:10]

            query += " AND DATE(o.created_at) BETWEEN %s AND %s"
            params.extend([data_ini, data_fim])

        # FILTRO STATUS
        if filtros.get('status'):
            query += " AND o.status = %s"
            params.append(filtros['status'])

        # FILTRO CLIENTE
        if filtros.get('cliente'):
            query += " AND o.cliente ILIKE %s"
            params.append(f"%{filtros['cliente']}%")

        # FILTRO BUSCA (título OU cliente)
        if filtros.get('busca'):
            query += " AND (o.titulo ILIKE %s OR o.cliente ILIKE %s)"
            params.append(f"%{filtros['busca']}%")
            params.append(f"%{filtros['busca']}%")

        return query, params