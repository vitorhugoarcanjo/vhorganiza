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
            excluido_em DATETIME,
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
    cursor.execute("PRAGMA table_info(transacoes)")
    colunas_existentes = [col[1] for col in cursor.fetchall()]
    
    # Lista de colunas que REALMENTE precisam ser adicionadas
    colunas_para_adicionar = []
    
    # Colunas NOVAS (para parcelas) - essas não existem na sua tabela atual
    if 'transacao_pai_id' not in colunas_existentes:
        colunas_para_adicionar.append("transacao_pai_id INTEGER DEFAULT NULL")
    
    if 'sequencia_parcela' not in colunas_existentes:
        colunas_para_adicionar.append("sequencia_parcela INTEGER DEFAULT NULL")
    
    if 'intervalo_dias' not in colunas_existentes:
        colunas_para_adicionar.append("intervalo_dias INTEGER DEFAULT 30")
    
    # Verifica se 'ativo' existe (já deve existir, mas seguro)
    if 'ativo' not in colunas_existentes:
        colunas_para_adicionar.append("ativo INTEGER DEFAULT 1")
    
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