def tabela_logs_resumo_mensal(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='logs_resumo_mensal')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE logs_resumo_mensal (
            id SERIAL PRIMARY KEY,
            ano INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            total_acessos INTEGER DEFAULT 0,
            usuarios_unicos INTEGER DEFAULT 0,
            total_erros INTEGER DEFAULT 0,
            rotas_mais_acessadas TEXT,  -- JSON
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ano, mes)
        )
    """)
        print("✅ tabela logs_resumo_mensal criada com sucesso")
        return
    
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")
