def tabela_services(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'logs_acao')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""    
        CREATE TABLE logs_acao (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            acao VARCHAR(100),
            tabela_afetada VARCHAR(50),
            registro_id INTEGER,
            dados_antes TEXT,
            dados_depois TEXT,
            ip VARCHAR(45),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE SET NULL
        )
    """)
        print("✅ tabela logs_acao criada com sucesso")
        return
    
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")
