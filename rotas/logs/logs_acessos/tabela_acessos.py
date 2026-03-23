def tabela_logs_acessos(cursor):
    """Tabela de logs de acesso"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ip VARCHAR(45),
            user_agent TEXT,
            rota VARCHAR(255),
            metodo VARCHAR(10),
            status_code INTEGER,
            tempo_resposta INTEGER,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
    """)