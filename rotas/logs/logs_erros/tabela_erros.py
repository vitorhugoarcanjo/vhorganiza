def tabela_logs_erros(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'logs_erros')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE logs_erros (
        id SERIAL PRIMARY KEY,
        mensagem TEXT NOT NULL,
        arquivo VARCHAR(255),
        linha INTEGER,
        user_id INTEGER,
        rota VARCHAR(255),
        metodo VARCHAR(10),
        stack_trace TEXT,
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE SET NULL                  
        )
    """)
        print("✅ tabela logs_erros criada com sucesso")
        return
    
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")
