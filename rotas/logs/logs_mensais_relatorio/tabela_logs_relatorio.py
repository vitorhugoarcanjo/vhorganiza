def tabela_logs_resumo_mensal(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_resumo_mensal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        total_acessos INTEGER DEFAULT 0,
        usuarios_unicos INTEGER DEFAULT 0,
        total_erros INTEGER DEFAULT 0,
        rotas_mais_acessadas TEXT,  -- JSON
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ano, mes)
    );
""")