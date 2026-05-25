def tabela_categorias_financas(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias_financas'")

    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias_financas (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,  -- ID DO USUARIO
        nome TEXT, -- NOME DA CATEGORIA
        cor TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- DATA DE CRIAÇÃO
        FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE
        )
    """)
        print("✅ tabela categorias_financas criada com sucesso.")

    else:
        print("ℹ️ tabela categorias_financas já está criada.")