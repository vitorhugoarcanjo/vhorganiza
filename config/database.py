import os
import sqlite3
caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')


from rotas.pasta_login.tabelas.cadastre_se import tabela_cadastre_se # TABELA DE CADASTRO DE USUÁRIO

from rotas.pasta_financas.tabelas.tabelas_gerais import tabela_transacoes # TABELA TRANSAÇÕES E CATEGORIAS
from rotas.pasta_categorias.categorias_financas.tabela.tabela_categoria_financas import tabela_categorias_financas # TABELA CATEGORIA FINANCAS

from rotas.pasta_tarefas.tabelas.tabela_tarefas import criar_tabela_tarefas # TABELA TAREFAS
from rotas.pasta_categorias.categorias_tarefas.tabela.tabela_categoria_tarefas import tabela_categorias_tarefas # TABELA CATEGORIA_TAREFAS

# TABELAS DOS LOGS
from rotas.logs.logs_services.tabela_services import tabela_services
from rotas.logs.logs_acessos.tabela_acessos import tabela_logs_acessos
from rotas.logs.logs_erros.tabela_erros import tabela_logs_erros
from rotas.logs.logs_mensais_relatorio.tabela_logs_relatorio import tabela_logs_resumo_mensal

def criar_todas_tabelas():
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    tabela_cadastre_se(cursor)

    # FINANÇAS
    tabela_categorias_financas(cursor)
    tabela_transacoes(cursor)

    # TAREFAS
    criar_tabela_tarefas(cursor)
    tabela_categorias_tarefas(cursor)

    # LOGS
    tabela_services(cursor)
    tabela_logs_acessos(cursor)
    tabela_logs_erros(cursor)
    tabela_logs_resumo_mensal(cursor)


    print('Tabela criadas com sucesso!')
    conexao.commit()
    conexao.close()
