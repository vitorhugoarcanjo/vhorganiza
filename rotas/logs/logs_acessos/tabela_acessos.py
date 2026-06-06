def tabela_logs_acessos(cursor):
    """Tabela de logs de acesso"""
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'logs_acesso')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
            CREATE TABLE logs_acesso (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                ip VARCHAR(45),
                user_agent TEXT,
                rota VARCHAR(255),
                metodo VARCHAR(10),
                status_code INTEGER,
                tempo_resposta INTEGER,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE SET NULL
            )
        """)
        print("✅ tabela logs_acesso criada com sucesso")
        return
    
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")