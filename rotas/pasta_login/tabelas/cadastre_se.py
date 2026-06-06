def tabela_cadastre_se(cursor):
    cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='cadastre_se')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE cadastre_se(
        id SERIAL PRIMARY KEY,
        is_master INTEGER DEFAULT 0,
                       
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT NOT NULL,
        senha TEXT NOT NULL,
                       
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ativo INTEGER DEFAULT 1,
                       
        email_verificado INTEGER DEFAULT 0,
        codigo_verificacao VARCHAR(6),
        codigo_expiracao TIMESTAMP,
        tentativas_verificacao INTEGER DEFAULT 0,
        
        codigo_recuperacao_expiracao TIMESTAMP,
        codigo_recuperacao VARCHAR(6),
        tentativas_recuperacao INTEGER DEFAULT 0
        
        )
    """)
        print("✅ Tabela cadastre_se criada com sucesso!")
        return
    # ==========================================================
    # VERIFICA E ADICIONA COLUNAS QUE FALTAM
    # ==========================================================
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'cadastre_se'
        ORDER BY ordinal_position
    """)
    colunas_existentes = [row[0] for row in cursor.fetchall()]
    
    colunas_para_adicionar = []
    
    if 'is_master' not in colunas_existentes:
        colunas_para_adicionar.append("is_master INTEGER DEFAULT 0")
    
    for coluna_sql in colunas_para_adicionar:
        try:
            nome_coluna = coluna_sql.split()[0]
            cursor.execute(f"ALTER TABLE cadastre_se ADD COLUMN {coluna_sql}")
            print(f"✅ Coluna '{nome_coluna}' adicionada em cadastre_se!")
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna {coluna_sql}: {e}")
    
    if colunas_para_adicionar:
        print(f"✅ {len(colunas_para_adicionar)} nova(s) coluna(s) adicionada(s)!")
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")