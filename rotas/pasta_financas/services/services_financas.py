# rotas\pasta_financas\services\services_financas.py
from rotas.pasta_financas.queries import FinancasQueries
from rotas.pasta_financas.filters import FinancasFilters

class FinancasServices:
    """ Serviços de negócios do módulo finanças """
    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    def buscar_categorias(self, usuario_id):
        """ Busca categorias do usuário """
        self.cursor.execute(FinancasQueries.get_categorias_usuario(), (usuario_id,))
        return self.cursor.fetchall()
    
    def buscar_transacoes(self, usuario_id, filtros):
        """ BUSCA transações com FILTROS """
        query = FinancasQueries.get_transacoes_base()
        params = [usuario_id]

        # Aplica o filtro
        query, params = FinancasFilters.aplicar_filtros_query(query, params, filtros)

        # aplica a ordenação pela sequencia
        query += " ORDER BY t.data_emissao DESC, t.sequencia_transacoes DESC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def buscar_detalhes_transacao(self, transacao_id, usuario_id):
        """ BUSCA DETALHES DE UMA TRANSAÇÃO """
        self.cursor.execute(
            FinancasQueries.get_transacao_detalhes(),
            (transacao_id, usuario_id)
        )
        return self.cursor.fetchone()
