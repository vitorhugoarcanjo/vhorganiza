# rotas/pasta_tarefas/filters.py
# ==========================================================
# FILTROS DO MÓDULO DE TAREFAS
# ==========================================================
from flask import session
from datetime import date
from utils.filtros_reutilizaveis.data import filtro_datas


class TarefasFilters:
    """GERENCIA TODOS OS FILTROS DO MÓDULO TAREFAS"""
    PREFIXO = 'tarefas'

    # ------------------------------------------------------
    # RECUPERAR (só LÊ — nunca sobrescreve)
    # ------------------------------------------------------
    @classmethod
    def recuperar_filtros(cls, session):
        """RECUPERA FILTROS DA SESSION (só leitura)"""
        return {
            'status':            session.get(f'{cls.PREFIXO}_status', ''),
            'prioridade':        session.get(f'{cls.PREFIXO}_prioridade', ''),
            'descricao':         session.get(f'{cls.PREFIXO}_descricao', ''),
            'categorias':        session.get(f'{cls.PREFIXO}_categorias', []),
            'mostrar_inativas':  session.get(f'{cls.PREFIXO}_mostrar_inativas', '0'),
            'tipo_data':         session.get(f'{cls.PREFIXO}_tipo_data', 'inicio'),
        }

    # ------------------------------------------------------
    # SALVAR (só chamado pela view principal no POST)
    # ------------------------------------------------------
    @classmethod
    def salvar_filtros_post(cls, request, session):
        """SALVAR FILTROS DO POST NA SESSION"""
        session[f'{cls.PREFIXO}_status'] = request.form.get('status', '')
        session[f'{cls.PREFIXO}_prioridade'] = request.form.get('prioridade', '')
        session[f'{cls.PREFIXO}_descricao'] = request.form.get('descricao', '')
        session[f'{cls.PREFIXO}_categorias'] = request.form.getlist('categorias')

        mostrar_inativas = request.form.get('mostrar_inativas')
        if mostrar_inativas in ('0', '1', '2'):
            session[f'{cls.PREFIXO}_mostrar_inativas'] = mostrar_inativas
        else:
            session[f'{cls.PREFIXO}_mostrar_inativas'] = '0'

    # ------------------------------------------------------
    # CATEGORIAS (retorna lista pro <select> de filtros)
    # ------------------------------------------------------
    @classmethod
    def filtro_categorias(cls, usuario_id, cursor):
        """Retorna (categorias_filtro, categorias_usuario)"""
        cursor.execute("""
            SELECT id, nome, cor FROM categorias
            WHERE usuario_id = %s AND modulo = 'tarefas'
            ORDER BY nome
        """, (usuario_id,))
        categorias_usuario = cursor.fetchall()

        categorias_selecionadas = session.get(f'{cls.PREFIXO}_categorias', [])

        if not categorias_selecionadas:
            return [], categorias_usuario

        return categorias_selecionadas, categorias_usuario

    # ------------------------------------------------------
    # FILTROS DE DATA
    # ------------------------------------------------------
    @classmethod
    def processar_filtros_data(cls):
        """Chama o utilitário compartilhado passando 'tarefas' como prefixo"""
        data_hoje = date.today()
        return filtro_datas(data_hoje, prefixo=cls.PREFIXO)

    # ------------------------------------------------------
    # APLICAÇÃO DOS FILTROS NA QUERY
    # ------------------------------------------------------
    @classmethod
    def aplicar_filtros_query(cls, query, params, filtros):
        """Monta os AND/OR na query base"""

        # DATA
        if filtros.get('data_inicio') and filtros.get('data_fim'):
            tipo_data = filtros.get('tipo_data', 'inicio')
            if tipo_data == 'inicio':
                query += " AND t.data_inicio BETWEEN %s AND %s"
            elif tipo_data == 'final':
                query += " AND t.data_final BETWEEN %s AND %s"
            else:  # finalizacao
                query += " AND t.data_finalizacao BETWEEN %s AND %s"
            params.extend([filtros['data_inicio'], filtros['data_fim']])

        # CATEGORIAS
        categorias = filtros.get('categorias') or []
        if categorias:
            conds = []
            for cat in categorias:
                if cat == 'null':
                    conds.append("t.categoria_id IS NULL")
                else:
                    conds.append("t.categoria_id = %s")
                    params.append(cat)
            if conds:
                query += " AND (" + " OR ".join(conds) + ")"

        # STATUS
        status = filtros.get('status') or ''
        if status == 'vazio':
            query += " AND (t.status IS NULL OR t.status = '')"
        elif status == 'pendente_em_andamento':
            query += " AND (t.status = 'pendente' OR t.status = 'em andamento')"
        elif status:
            query += " AND t.status = %s"
            params.append(status)

        # PRIORIDADE
        prioridade = filtros.get('prioridade') or ''
        if prioridade == 'vazio':
            query += " AND (t.prioridade IS NULL OR t.prioridade = '')"
        elif prioridade:
            query += " AND t.prioridade = %s"
            params.append(prioridade)

        # DESCRIÇÃO
        descricao = filtros.get('descricao') or ''
        if descricao:
            query += " AND t.descricao ILIKE %s"
            params.append(f"%{descricao}%")

        # ATIVO / INATIVO
        mostrar_inativas = filtros.get('mostrar_inativas', '0')
        if mostrar_inativas == '1':
            query += " AND t.ativo = 0"
        elif mostrar_inativas == '2':
            pass  # todas
        else:
            query += " AND t.ativo = 1"

        return query, params

    # ------------------------------------------------------
    # LIMPAR
    # ------------------------------------------------------
    @classmethod
    def limpar_filtros(cls, session):
        """Limpa toda a sessão de filtros do módulo Tarefas"""
        chaves = [
            'status', 'prioridade', 'descricao', 'categorias',
            'mostrar_inativas', 'tipo_data',
            'data_inicio_intervalo', 'data_fim_intervalo',
            'modo', 'mes_corrente', 'dia_corrente', 'dia_referencia'
        ]
        for chave in chaves:
            session.pop(f'{cls.PREFIXO}_{chave}', None)