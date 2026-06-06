def tabela_categorias_tarefas(cursor):
    cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='categorias_tarefas')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE categorias_tarefas (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,              
        nome TEXT NOT NULL,              
        cor TEXT DEFAULT '#CCCCCC',
        FOREIGN KEY(user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
        UNIQUE(user_id, nome)                             
        )
    """)
        print("✅ Tabela categorias_tarefas criada com sucesso!")

    else:
        print("ℹ️ Tabela categorias_tarefas já existe.")
