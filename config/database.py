from utils.database.conexao_global import get_conexao_direct

# CRIAR INDICES
from .indices_automatico import criar_indices

# TABELA DE CADASTRO DE USUÁRIO
from rotas.pasta_login.tabelas.cadastre_se import tabela_cadastre_se 

# TABELA TRANSAÇÕES
from rotas.pasta_financas.tabelas.tabelas_gerais import tabela_transacoes 

# TABELA TAREFAS
from rotas.pasta_tarefas.tabelas.tabela_tarefas import criar_tabela_tarefas 

# TABELA CATEGORIAS
from rotas.pasta_categorias.tabela.tabela_categorias import tabela_categorias

# TABELAS DOS LOGS
from rotas.logs.logs_services.tabela_services import tabela_services
from rotas.logs.logs_acessos.tabela_acessos import tabela_logs_acessos
from rotas.logs.logs_erros.tabela_erros import tabela_logs_erros
from rotas.logs.logs_mensais_relatorio.tabela_logs_relatorio import tabela_logs_resumo_mensal
from rotas.logs.logs_ataques.tabela import tabela_ataque

# TABELAS AUDITORIA
from rotas.auditoria_geral.pasta_tarefas.tabela import tabela_auditoria_tarefas
from rotas.auditoria_geral.pasta_financas.tabela import tabela_auditoria_financas
from rotas.auditoria_geral.pasta_orcamentos.tabela import tabela_auditoria_orcamentos


# TABELA ORCAMENTO
from rotas.pasta_orcamentos.tabelas.criar_tabela_orcamentos import tabela_orcamento

def criar_todas_tabelas():
    conexao = get_conexao_direct()
    cursor = conexao.cursor()

    tabela_cadastre_se(cursor)

    # FINANÇAS
    tabela_transacoes(cursor)

    # TAREFAS
    criar_tabela_tarefas(cursor)

    # CATEGORIAS
    tabela_categorias(cursor)

    # LOGS
    tabela_services(cursor)
    tabela_logs_acessos(cursor)
    tabela_logs_erros(cursor)
    tabela_logs_resumo_mensal(cursor)
    tabela_ataque(cursor)

    # AUDITORIA
    tabela_auditoria_tarefas(cursor)
    tabela_auditoria_financas(cursor)
    tabela_auditoria_orcamentos(cursor)

    # ORCAMENTOS
    tabela_orcamento(cursor)

    # CRIA ÍNDICES
    criar_indices(cursor)

    print('Tabela criadas com sucesso!')
    conexao.commit()
    conexao.close()
