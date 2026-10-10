# rotas/pasta_tarefas/filters.py
# ==========================================================
# FILTROS DO MÓDULO DE TAREFAS
# ==========================================================

from datetime import date
from flask import session, request
from utils.filtros_reutilizaveis.data import filtro_datas


class TarefasFilters:

    # ------------------------------------------------------
    # FILTROS DE SESSÃO
    # ------------------------------------------------------
    @staticmethod
    def filtro_categorias(usuario_id, cursor):
        """Retorna (categorias_filtro, categorias_usuario)"""
        cursor.execute("""
            SELECT id, nome, cor FROM categorias WHERE usuario_id = %s AND modulo = 'tarefas' ORDER BY nome
        """, (usuario_id,))
        categorias_usuario = cursor.fetchall()

        categorias_selecionadas = request.form.getlist('categorias')

        if not categorias_selecionadas:
            return [], categorias_usuario

        return categorias_selecionadas, categorias_usuario

    @staticmethod
    def filtro_status():
        status = request.form.get('status', '')
        if request.method == 'POST':
            session['status_filtro'] = status
            return status
        return session.get('status_filtro', '')

    @staticmethod
    def filtro_prioridade():
        prioridade = request.form.get('prioridade', '')
        if request.method == 'POST':
            session['prioridade_filtro'] = prioridade
            return prioridade
        return session.get('prioridade_filtro', '')

    @staticmethod
    def filtro_descricao():
        descricao = request.form.get('descricao', '')
        if descricao:
            session['descricao_filtro'] = descricao
            return descricao
        return session.get('descricao_filtro', '')

    @staticmethod
    def processar_filtros_data():
        """Chama o utilitário compartilhado passando 'tarefas' como prefixo"""
        data_hoje = date.today()
        return filtro_datas(data_hoje, prefixo='tarefas')

    @staticmethod
    def processar_mostrar_inativas():
        """Retorna '0', '1' ou '2' (ativos / inativos / todas)"""
        mostrar = request.args.get('mostrar_inativas')
        if mostrar is None and request.method == 'POST':
            mostrar = request.form.get('mostrar_inativas')
        if mostrar is None:
            mostrar = session.get('mostrar_inativas', '0')
        session['mostrar_inativas'] = mostrar
        return mostrar

    # ------------------------------------------------------
    # APLICAÇÃO DOS FILTROS NA QUERY
    # ------------------------------------------------------
    @staticmethod
    def aplicar_filtros_query(query, params, filtros):
        """Monta os AND/OR na query base"""

        # DATA (🔥 SEM DATE() — usa BETWEEN direto, aproveita índice)
        if filtros.get('data_inicio') and filtros.get('data_fim'):
            tipo_data = filtros.get('tipo_data', 'inicio')
            if tipo_data == 'inicio':
                query += " AND t.data_inicio BETWEEN %s AND %s"
            elif tipo_data == 'final':
                query += " AND t.data_final BETWEEN %s AND %s"
            else:  # finalizacao
                query += " AND t.data_finalizacao BETWEEN %s AND %s"
            params.extend([filtros['data_inicio'], filtros['data_fim']])

        # CATEGORIAS (🔥 categoria_id é INTEGER — só IS NULL)
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

        # DESCRIÇÃO (🔥 ILIKE — case-insensitive)
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

    @staticmethod
    def limpar_filtros():
        """Limpa toda a sessão de filtros do módulo Tarefas"""
        prefixo = 'tarefas'
        session.pop('status_filtro', None)
        session.pop('prioridade_filtro', None)
        session.pop('descricao_filtro', None)
        session.pop('mostrar_inativas', None)
        session.pop(f'{prefixo}_data_inicio_intervalo', None)
        session.pop(f'{prefixo}_data_fim_intervalo', None)
        session.pop(f'{prefixo}_modo', None)
        session.pop(f'{prefixo}_mes_corrente', None)
        session.pop(f'{prefixo}_dia_corrente', None)
        session.pop(f'{prefixo}_dia_referencia', None)
        session.pop(f'{prefixo}_tipo_data', None)