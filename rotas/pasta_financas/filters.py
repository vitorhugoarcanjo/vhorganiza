from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas

class FinancasFilters:
    """ GERENCIA TODOS OS FILTROS DO MÓDULO FINANÇAS """
    PREFIXO = 'financas'

    @classmethod
    def processar_filtros_data(cls):
        """ PROCESSA FILTROS DE DATA """
        data_inicio, data_fim, tipo_data = filtro_datas(date.today(), prefixo=cls.PREFIXO)

        # CORRIGE TIPO_DATA
        if tipo_data == 'inicio':
            tipo_data = 'emissao'

        return data_inicio, data_fim, tipo_data

    @classmethod
    def salvar_filtros_post(cls, request, session):
        """ SALVAR FILTROS DO POST NA SESSION """
        session[f'{cls.PREFIXO}_descricao'] = request.form.get('descricao', '')
        session[f'{cls.PREFIXO}_tipo'] = request.form.get('tipo', '')
        session[f'{cls.PREFIXO}_status'] = request.form.get('status', '')
        session[f'{cls.PREFIXO}_categorias'] = request.form.getlist('categorias')

        mostrar_inativas = request.form.get('mostrar_inativas')
        if mostrar_inativas in ('0', '1', '2'):
            session[f'{cls.PREFIXO}_mostrar_inativas'] = mostrar_inativas

        else:
            session[f'{cls.PREFIXO}_mostrar_inativas'] = '0'


    @classmethod
    def recuperar_filtros(cls, session):
        """ RECUPERA FILTROS DA SESSION """
        return {
            'descricao': session.get(f'{cls.PREFIXO}_descricao', ''),
            'tipo': session.get(f'{cls.PREFIXO}_tipo', ''),
            'status': session.get(f'{cls.PREFIXO}_status', ''),
            'categorias': session.get(f'{cls.PREFIXO}_categorias', []),
            'mostrar_inativas': session.get(f'{cls.PREFIXO}_mostrar_inativas', '0'),
            'tipo_data': session.get(f'{cls.PREFIXO}_tipo_data', 'emissao')
        }

    @classmethod
    def limpar_filtros(cls, session):
        """ LIMPA TODOS OS FILTROS """
        chaves = [
            'descricao', 'tipo', 'status', 'categorias',
            'tipo_data', 'mostrar_inativas',
            'data_inicio_intervalo', 'data_fim_intervalo',
            'modo', 'mes_corrente', 'dia_corrente', 'dia_referencia'
        ]
        
        for chave in chaves:
            session.pop(f'{cls.PREFIXO}_{chave}', None)

    @classmethod
    def aplicar_filtros_query(cls, query, params, filtros):
        """ APLICA TODOS OS FILTROS QUERY """
        # FILTRO DATA
        if filtros.get('data_inicio') and filtros.get('data_fim'):
            if filtros.get('tipo_data') == 'emissao':
                query += " AND DATE(t.data_emissao) BETWEEN %s AND %s"

            else:
                query += " AND DATE(t.data_vencimento) BETWEEN %s AND %s"
            
            params.extend([filtros['data_inicio'], filtros['data_fim']])

        # FILTROS ATIVO/INATIVO
        if filtros.get('mostrar_inativas') == '1':
            query += " AND t.ativo = 0"

        elif filtros.get('mostrar_inativas') == '0':
            query += " AND t.ativo = 1"

        # FILTRO CATEGORIAS
        if filtros.get('categorias'):
            conditions = []
            for cat in filtros['categorias']:
                if cat == 'null':
                    conditions.append("(t.categoria_id IS NULL OR t.categoria_id = '')")

                else:
                    conditions.append("t.categoria_id = %s")
                    params.append(cat)
            if conditions:
                query += " AND (" + " OR ".join(conditions) + ")"

        # FILTRO DESCRIÇÃO
        if filtros.get('descricao'):
            query += " AND t.descricao ILIKE %s"
            params.append(f"%{filtros['descricao']}")


        # FILTRO TIPO
        if filtros.get('tipo'):
            query += " AND t.tipo = %s"
            params.append(filtros['tipo'])

        # FILTRO STATUS
        if filtros.get('status'):
            query += " AND t.status = %s"
            params.append(filtros['status'])

        
        return query, params