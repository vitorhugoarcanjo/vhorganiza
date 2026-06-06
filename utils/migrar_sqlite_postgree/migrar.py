# migrar_dados_seguro.py
import sqlite3
import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# TABELAS NA ORDEM CORRETA (respeitando FKs)
TABELAS_ORDEM = [
    'cadastre_se',
    'categorias_financas',
    'categorias_tarefas',
    'transacoes',
    'tarefas',
    'logs_acesso',
    'logs_ataques',
    'logs_erros',
    'logs_resumo_mensal',
    'logs_acao',
    'tarefas_auditoria',
    'financas_auditoria',
]

# CAMPOS QUE SÃO DO TIPO DATE no PostgreSQL
CAMPOS_DATA = [
    'data_inicio', 'data_final', 'data_finalizacao',
    'data_emissao', 'data_vencimento', 'data_quitamento', 'data_alteracao',
    'data_criacao', 'data_hora', 'codigo_expiracao', 'codigo_recuperacao_expiracao',
    'excluido_em', 'created_at', 'updated_at'
]

# CAMPOS QUE SÃO TIMESTAMP
CAMPOS_TIMESTAMP = [
    'data_hora', 'created_at', 'updated_at', 'excluido_em',
    'codigo_expiracao', 'codigo_recuperacao_expiracao'
]

def tratar_valor(valor, coluna):
    """Converte valores do SQLite para tipos compatíveis com PostgreSQL"""
    
    # Se for None, mantém None
    if valor is None:
        return None
    
    # Se for string vazia em campo de data/timestamp
    if isinstance(valor, str) and valor == '':
        if coluna in CAMPOS_DATA or coluna in CAMPOS_TIMESTAMP:
            return None
        return valor
    
    # Se for string com 'None' literal
    if isinstance(valor, str) and valor.lower() == 'none':
        return None
    
    return valor

print("🚀 INICIANDO MIGRAÇÃO DOS DADOS...")
print("=" * 50)

# ==========================================================
# CONEXÕES
# ==========================================================

# Conexão SQLite (origem)
sqlite_conn = sqlite3.connect('instance/banco_de_dados.db')
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Conexão PostgreSQL (destino)
url = urlparse(os.getenv('DATABASE_URL'))
pg_conn = psycopg2.connect(
    host=url.hostname,
    database=url.path[1:],
    user=url.username,
    password=url.password,
    port=url.port or 5432
)
pg_cursor = pg_conn.cursor()

# ==========================================================
# DESABILITAR VERIFICAÇÃO DE FOREIGN KEYS
# ==========================================================
print("\n🔓 Desabilitando verificação de chaves estrangeiras...")
pg_cursor.execute("SET session_replication_role = 'replica';")
print("   ✅ Verificação desabilitada")

# ==========================================================
# MIGRAÇÃO
# ==========================================================

for nome_tabela in TABELAS_ORDEM:
    print(f"\n📥 Migrando {nome_tabela}...")
    
    # Verifica se tabela existe no SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
    if not sqlite_cursor.fetchone():
        print(f"   ⚠️ Tabela não encontrada no SQLite, pulando...")
        continue
    
    # Pega dados do SQLite
    sqlite_cursor.execute(f"SELECT * FROM {nome_tabela}")
    dados = sqlite_cursor.fetchall()
    
    if not dados:
        print(f"   ℹ️ Tabela vazia, nada a migrar")
        continue
    
    # Pega nomes das colunas
    colunas = [desc[0] for desc in sqlite_cursor.description]
    
    # Limpa dados existentes no PostgreSQL
    try:
        pg_cursor.execute(f'TRUNCATE TABLE "{nome_tabela}" RESTART IDENTITY CASCADE')
        print(f"   🗑️  Dados antigos removidos")
    except Exception as e:
        print(f"   ⚠️ Erro ao limpar tabela: {e}")
        continue
    
    # Prepara INSERT
    placeholders = ", ".join(["%s"] * len(colunas))
    colunas_str = ", ".join([f'"{col}"' for col in colunas])
    
    # Insere os dados com tratamento de valores
    inseridos = 0
    erros = 0
    
    for idx, row in enumerate(dados, 1):
        try:
            # Trata cada valor conforme o tipo da coluna
            valores = []
            for col in colunas:
                valor_original = row[col]
                valor_tratado = tratar_valor(valor_original, col)
                valores.append(valor_tratado)
            
            pg_cursor.execute(f'INSERT INTO "{nome_tabela}" ({colunas_str}) VALUES ({placeholders})', valores)
            inseridos += 1
            
        except Exception as e:
            erros += 1
            if erros <= 5:  # Mostra só os primeiros 5 erros
                print(f"   ⚠️ Erro na linha {idx}: {e}")
                print(f"      Colunas: {colunas[:5]}...")
                print(f"      Valores: {valores[:5]}...")
    
    pg_conn.commit()
    print(f"   ✅ {inseridos}/{len(dados)} linhas migradas com sucesso!")
    if erros > 0:
        print(f"   ⚠️ {erros} linhas com erro (ignoradas)")

# ==========================================================
# REATIVAR VERIFICAÇÃO DE FOREIGN KEYS
# ==========================================================
print("\n🔒 Reativando verificação de chaves estrangeiras...")
pg_cursor.execute("SET session_replication_role = 'origin';")
print("   ✅ Verificação reativada")

# ==========================================================
# VERIFICAR CONSISTÊNCIA
# ==========================================================
print("\n🔍 Verificando consistência dos dados...")

# Verifica se todas as FKs estão válidas
try:
    pg_cursor.execute("""
        SELECT 'tarefas' as tabela, COUNT(*) as invalidos
        FROM tarefas t
        LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id
        WHERE t.categoria_id IS NOT NULL AND c.id IS NULL
        UNION ALL
        SELECT 'transacoes', COUNT(*)
        FROM transacoes t
        LEFT JOIN categorias_financas c ON t.categoria_id = c.id
        WHERE t.categoria_id IS NOT NULL AND c.id IS NULL
    """)
    resultados = pg_cursor.fetchall()
    for tabela, invalidos in resultados:
        if invalidos > 0:
            print(f"   ⚠️ {tabela}: {invalidos} registros com categoria inválida")
        else:
            print(f"   ✅ {tabela}: todas as FKs válidas")
except Exception as e:
    print(f"   ⚠️ Não foi possível verificar: {e}")

# ==========================================================
# AJUSTAR SEQUENCES PARA O PRÓXIMO ID DISPONÍVEL
# ==========================================================
print("\n📊 Ajustando sequences para o próximo ID disponível...")

# Lista de tabelas com SERIAL (id auto-incremento)
tabelas_com_serial = [
    'cadastre_se', 'categorias_financas', 'categorias_tarefas', 
    'transacoes', 'tarefas', 'logs_acesso', 'logs_ataques', 
    'logs_erros', 'logs_resumo_mensal', 'logs_acao', 
    'tarefas_auditoria', 'financas_auditoria'
]

for tabela in tabelas_com_serial:
    try:
        # Verifica se a tabela tem registros
        pg_cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = pg_cursor.fetchone()[0]
        
        if count > 0:
            # Ajusta a sequence para o maior ID + 1
            pg_cursor.execute(f"SELECT setval('{tabela}_id_seq', (SELECT MAX(id) FROM {tabela}))")
            print(f"   ✅ {tabela}_id_seq ajustada para MAX(id) = {pg_cursor.fetchone()[0]}")
        else:
            print(f"   ℹ️ {tabela} está vazia, sequence mantida em 1")
    except Exception as e:
        print(f"   ⚠️ {tabela}: {e}")

pg_conn.commit()

# Contagem final por tabela
print("\n📊 CONTAGEM FINAL POR TABELA:")
try:
    for tabela in TABELAS_ORDEM:
        pg_cursor.execute(f'SELECT COUNT(*) FROM "{tabela}"')
        count = pg_cursor.fetchone()[0]
        print(f"   📌 {tabela}: {count} registros")
except Exception as e:
    print(f"   ⚠️ Erro ao contar: {e}")

print("\n" + "=" * 50)
print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")

# Fecha conexões
sqlite_cursor.close()
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()