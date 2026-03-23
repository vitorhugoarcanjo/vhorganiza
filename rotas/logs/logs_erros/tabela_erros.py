def tabela_logs_erros(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_erros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mensagem TEXT NOT NULL,
    arquivo VARCHAR(255),
    linha INTEGER,
    user_id INTEGER,
    rota VARCHAR(255),
    metodo VARCHAR(10),
    stack_trace TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE SET NULL                  
    )
""")