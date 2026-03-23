def tabela_services(cursor):
    cursor.execute("""    
    CREATE TABLE IF NOT EXISTS logs_acao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        acao VARCHAR(100),
        tabela_afetada VARCHAR(50),
        registro_id INTEGER,
        dados_antes TEXT,
        dados_depois TEXT,
        ip VARCHAR(45),
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL
    );
""")