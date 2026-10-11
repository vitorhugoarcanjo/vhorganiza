# rotas/pasta_categorias/filters.py
# ==========================================================
# FILTROS DO MÓDULO DE CATEGORIAS
# ==========================================================

from flask import session, request


class CategoriasFilters:

    @staticmethod
    def filtro_descricao():
        """Busca por nome (ILIKE)"""
        descricao = request.form.get('descricao', '')
        if descricao:
            session['categorias_descricao'] = descricao
            return descricao
        return session.get('categorias_descricao', '')

    @staticmethod
    def filtro_modulo():
        """Módulo selecionado: 'tarefas', 'financas' ou '' (todos)"""
        modulo = request.form.get('modulo', '')
        if modulo:
            session['categorias_modulo'] = modulo
            return modulo
        return session.get('categorias_modulo', '')

    @staticmethod
    def processar_mostrar_inativas():
        """Retorna '0', '1' ou '2' (ativos / inativos / todas)"""
        mostrar = request.args.get('mostrar_inativas')
        if mostrar is None and request.method == 'POST':
            mostrar = request.form.get('mostrar_inativas')
        if mostrar is None:
            mostrar = session.get('categorias_mostrar_inativas', '0')
        session['categorias_mostrar_inativas'] = mostrar
        return mostrar

    @staticmethod
    def aplicar_filtros_query(query, params, filtros):
        """Monta os AND/OR na query base"""

        # MÓDULO
        modulo = filtros.get('modulo') or ''
        if modulo in ('tarefas', 'financas'):
            query += " AND c.modulo = %s"
            params.append(modulo)

        # DESCRIÇÃO (ILIKE — case-insensitive)
        descricao = filtros.get('descricao') or ''
        if descricao:
            query += " AND c.nome ILIKE %s"
            params.append(f"%{descricao}%")

        # ATIVO / INATIVO
        mostrar_inativas = filtros.get('mostrar_inativas', '0')
        if mostrar_inativas == '1':
            query += " AND c.ativo = 0"
        elif mostrar_inativas == '2':
            pass  # todas
        else:
            query += " AND c.ativo = 1"

        return query, params

    @staticmethod
    def limpar_filtros():
        """Limpa toda a sessão de filtros do módulo Categorias"""
        session.pop('categorias_descricao', None)
        session.pop('categorias_modulo', None)
        session.pop('categorias_mostrar_inativas', None)