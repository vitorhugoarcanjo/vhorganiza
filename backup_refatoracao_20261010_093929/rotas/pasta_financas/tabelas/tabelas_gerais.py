def tabela_transacoes(cursor, tipo_banco='postgresql'):
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transacoes')")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE transacoes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            sequencia_transacoes INTEGER,
            
            -- dados básicos da transação
            tipo TEXT,
            descricao TEXT,
            categoria_id INTEGER,
            
            -- Datas importantes
            data_emissao DATE,
            data_vencimento DATE,
            data_quitamento DATE,
            data_alteracao DATE,
                    
            -- Valores
            valor_total REAL,
            valor_parcela REAL,
                    
            -- Controle de parcelas
            numero_parcela INTEGER,
            total_parcelas INTEGER,
            
            -- 🔥 NOVAS COLUNAS PARA VÍNCULO DE PARCELAS
            transacao_pai_id INTEGER,
            sequencia_parcela INTEGER,
            intervalo_dias INTEGER DEFAULT 30,
            
            -- Status e controle
            status TEXT DEFAULT 'aberto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            excluido_por INTEGER,
            excluido_em TIMESTAMP,
            ativo INTEGER DEFAULT 1,
            
            FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias_financas(id) ON DELETE SET NULL
        )
    """)
        print("✅ tabela transacoes criada com sucesso")
        return

    # ==========================================================
    # VERIFICA E ADICIONA SOMENTE AS COLUNAS QUE FALTAM
    # ==========================================================
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'transacoes'
        ORDER BY ordinal_position
""")
    colunas_existentes = [row[0] for row in cursor.fetchall()]
    
    # Lista de colunas que REALMENTE precisam ser adicionadas
    colunas_para_adicionar = []
    
    # Colunas NOVAS (para parcelas) - essas não existem na sua tabela atual
    if 'transacao_pai_id' not in colunas_existentes:
        colunas_para_adicionar.append("transacao_pai_id INTEGER DEFAULT NULL")
    
    
    # Adiciona cada coluna faltante
    for coluna_sql in colunas_para_adicionar:
        try:
            nome_coluna = coluna_sql.split()[0]
            cursor.execute(f"ALTER TABLE transacoes ADD COLUMN {coluna_sql}")
            print(f"✅ Coluna '{nome_coluna}' adicionada em transacoes!")
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna {coluna_sql}: {e}")
    
    if colunas_para_adicionar:
        print(f"✅ {len(colunas_para_adicionar)} nova(s) coluna(s) adicionada(s)!")
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")