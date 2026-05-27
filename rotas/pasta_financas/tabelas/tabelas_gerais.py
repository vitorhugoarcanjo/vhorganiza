def tabela_transacoes(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes'")

    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sequencia_transacoes INTEGER,
            
            -- dados básicos da transação
            tipo TEXT,
            descricao TEXT,
            categoria_id INTEGER,
            
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
                    
            FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias_financas(id) ON DELETE SET NULL
                       
                             
        )
    """)
        print("✅ tabela tabela_transacoes criada com sucesso")

    else:
        # Verifica e adiciona colunas faltantes
        cursor.execute("PRAGMA table_info(transacoes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'ativo' not in colunas:
            cursor.execute("ALTER TABLE transacoes ADD COLUMN ativo INTEGER DEFAULT 1")
            print("✅ Coluna ativo adicionada em transacoes!")
            
        if 'excluido_em' not in colunas:
            cursor.execute("ALTER TABLE transacoes ADD COLUMN excluido_em DATETIME")
            print("✅ Coluna excluido_em adicionada em transacoes!")
            
        if 'excluido_por' not in colunas:
            cursor.execute("ALTER TABLE transacoes ADD COLUMN excluido_por INTEGER")
            print("✅ Coluna excluido_por adicionada em transacoes!")
            
        print("ℹ️ tabela transacoes já existe. Verificação concluída.")
