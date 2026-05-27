def tabela_auditoria_financas(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financas_auditoria'")
    
    if not cursor.fetchone():    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financas_auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transacao_id INTEGER,
                acao VARCHAR(50),  -- 'criada', 'editada', 'excluida', 'quitada', 'recebida'
                campo_alterado VARCHAR(100),
                valor_antigo TEXT,
                valor_novo TEXT,
                usuario_id INTEGER,
                data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip VARCHAR(45),
                FOREIGN KEY (transacao_id) REFERENCES transacoes(id),
                FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
            )
        """)
        print("✅ Tabela financas_auditoria criada com sucesso!")
    else:
        print("ℹ️ Tabela financas_auditoria já existe")