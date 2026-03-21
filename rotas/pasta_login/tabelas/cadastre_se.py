def tabela_cadastre_se(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cadastre_se'")

    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastre_se(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                       
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT NOT NULL,
        senha TEXT NOT NULL,
                       
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ativo BOOLEAN DEFAULT 1,
                       
        email_verificado INTEGER DEFAULT 0,
        codigo_verificacao VARCHAR(6),
        codigo_expiracao DATETIME,
        tentativas_verificacao INTEGER DEFAULT 0
                    
        )
    """)
        print("✅ Tabela cadastre_se criada com sucesso!")

    else:
        # MODELO DE NOVAS COLUNAS
        cursor.execute("PRAGMA table_info(cadastre_se)")
        if not any(col[1] == 'codigo_recuperacao_expiracao' for col in cursor.fetchall()):
            cursor.execute("ALTER TABLE cadastre_se ADD COLUMN codigo_recuperacao_expiracao DATETIME")
            print("✅ Coluna codigo_recuperacao_expiracao Adicionado em cadastre_se")


        cursor.execute("PRAGMA table_info(cadastre_se)")
        if not any(col[1] == 'codigo_recuperacao' for col in cursor.fetchall()):
            cursor.execute("ALTER TABLE cadastre_se ADD COLUMN codigo_recuperacao VARCHAR(6)")
            print("✅ Coluna codigo_recuperacao Adicionado em cadastre_se")


        cursor.execute("PRAGMA table_info(cadastre_se)")
        if not any(col[1] == 'tentativas_recuperacao' for col in cursor.fetchall()):
            cursor.execute("ALTER TABLE cadastre_se ADD COLUMN tentativas_recuperacao INTEGER DEFAULT 0")
            print("✅ Coluna tentativas_recuperacao Adicionado em cadastre_se")


        print("Tabela tarefas já existe.")
