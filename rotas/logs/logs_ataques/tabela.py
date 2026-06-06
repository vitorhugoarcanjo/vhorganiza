def tabela_ataque(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'logs_ataques')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE logs_ataques (
            id SERIAL PRIMARY KEY,
            ip VARCHAR(45),
            rota VARCHAR(255),
            metodo VARCHAR(10),
            user_agent TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            padrao_detectado VARCHAR(100)
        )
    """)
        print("✅ tabela logs_ataques criada com sucesso")
        return
    
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")