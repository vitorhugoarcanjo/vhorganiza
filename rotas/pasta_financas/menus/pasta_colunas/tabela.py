# def tabela_colunas_usuarios(cursor):
#     # Verifica se a tabela existe (usando o nome correto)
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_preferences'")

#     if not cursor.fetchone():
#         cursor.execute("""
#             CREATE TABLE user_preferences (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 tabela TEXT NOT NULL,
#                 configuracao TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
#                 UNIQUE(user_id, tabela)
#             )
#         """)
#         print("✅ Tabela user_preferences criada com sucesso")
#         return

#     # ==========================================================
#     # VERIFICA E ADICIONA SOMENTE AS COLUNAS QUE FALTAM
#     # ==========================================================
#     cursor.execute("PRAGMA table_info(user_preferences)")
#     colunas_existentes = [col[1] for col in cursor.fetchall()]
    
#     colunas_para_adicionar = []
    
#     # Verifica cada coluna individualmente
#     if 'configuracao' not in colunas_existentes:
#         colunas_para_adicionar.append("configuracao TEXT DEFAULT '[]'")
    
#     if 'updated_at' not in colunas_existentes:
#         colunas_para_adicionar.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
#     # Adiciona cada coluna faltante
#     for coluna_sql in colunas_para_adicionar:
#         try:
#             nome_coluna = coluna_sql.split()[0]
#             cursor.execute(f"ALTER TABLE user_preferences ADD COLUMN {coluna_sql}")
#             print(f"✅ Coluna '{nome_coluna}' adicionada em user_preferences!")
#         except Exception as e:
#             print(f"⚠️ Erro ao adicionar coluna {coluna_sql}: {e}")
    
#     if colunas_para_adicionar:
#         print(f"✅ {len(colunas_para_adicionar)} nova(s) coluna(s) adicionada(s)!")
#     else:
#         print("ℹ️ Todas as colunas já existem. Nada foi alterado.")