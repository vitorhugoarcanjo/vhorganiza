# rotas/pasta_dashboard/filters.py
# ==========================================================
# FILTROS DO DASHBOARD (padrão 2099 — igual Finanças)
# ==========================================================

from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas


class DashboardFilters:
    """ GERENCIA TODOS OS FILTROS DO MÓDULO DASHBOARD """
    PREFIXO = 'dashboard'

    @classmethod
    def processar_filtros_data(cls):
        """ PROCESSA FILTROS DE DATA """
        data_inicio, data_fim, tipo_data = filtro_datas(date.today(), prefixo=cls.PREFIXO)

        # CORRIGE TIPO_DATA (padrão Finanças)
        if tipo_data == 'inicio':
            tipo_data = 'emissao'

        return data_inicio, data_fim, tipo_data

    @classmethod
    def limpar_filtros(cls, session):
        """ LIMPA TODOS OS FILTROS """
        chaves = [
            'tipo_data', 'mostrar_inativas',
            'data_inicio_intervalo', 'data_fim_intervalo',
            'modo', 'mes_corrente', 'dia_corrente', 'dia_referencia'
        ]

        for chave in chaves:
            session.pop(f'{cls.PREFIXO}_{chave}', None)