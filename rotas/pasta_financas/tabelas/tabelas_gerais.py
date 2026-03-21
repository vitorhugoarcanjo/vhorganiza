def tabela_transacoes(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes'")

    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            
            -- dados básicos da transação
            tipo TEXT,
            descricao TEXT,
            categoria TEXT,
            
            -- Datas importantes
            data_emissao DATE, -- Quando foi criada
            data_vencimento DATE,  -- Quando vence
            data_quitamento DATE,  -- Quando foi paga
            data_alteracao DATE,   -- Quando foi alterada
                    
            -- Valores
            valor_total REAL,      -- Valor total da compra
            valor_parcela REAL,    -- Valor desta parcela específica
                    
            -- Controle de parcelas(novo)
            numero_parcela INTEGER,  -- Ex: 1ª parcela
            total_parcelas INTEGER,  -- Ex: 10 parcelas no total
                    
            -- Status e controle
            status TEXT DEFAULT 'aberto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
            FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE       
        )
    """)
        print("✅ tabela tabela_transacoes criada com sucesso")

    # MODELO - ESTRUTURA
    cursor.execute("PRAGMA table_info(transacoes)")
    if not any(col[1] == 'sequencia_transacoes' for col in cursor.fetchall()):
        cursor.execute("ALTER TABLE transacoes ADD COLUMN sequencia_transacoes INTEGER")
        print("✅ Coluna sequencia_transacoes adicionada em transacoes!")


    else:
        print("ℹ️ tabela tabela_transacoes já está criada.")
