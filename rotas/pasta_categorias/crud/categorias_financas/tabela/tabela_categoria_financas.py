def tabela_categorias_financas(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='categorias_financas')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE categorias_financas (
        id SERIAL PRIMARY KEY,
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