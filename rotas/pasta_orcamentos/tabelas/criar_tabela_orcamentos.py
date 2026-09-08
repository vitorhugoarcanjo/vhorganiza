def tabela_orcamento(cursor, tipo_banco='postgresql'):
    # VERIFICA SE A TABELA EXISTE
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orcamentos')")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        # CRIA A TABELA COMPLETA
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orcamentos (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
                titulo VARCHAR(200) NOT NULL,
                cliente VARCHAR(200),
                status VARCHAR(20) DEFAULT 'rascunho',
                estrutura JSONB DEFAULT '[]'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela 'orcamentos' criada com sucesso!")
        return  # ← SAI DA FUNÇÃO! NÃO TENTA ADICIONAR COLUNAS

    # ==========================================================
    # SÓ CHEGA AQUI SE A TABELA JÁ EXISTE
    # ==========================================================
    print("ℹ️ Tabela 'orcamentos' já existe. Verificando colunas...")
    
    # VERIFICA COLUNAS EXISTENTES
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'orcamentos'
        ORDER BY ordinal_position
    """)
    colunas_existentes = [row[0] for row in cursor.fetchall()]
    
    # LISTA DE COLUNAS QUE DEVEM EXISTIR
    colunas_necessarias = {
        'cliente': 'VARCHAR(200)',
        'status': "VARCHAR(20) DEFAULT 'rascunho'",
        'estrutura': "JSONB DEFAULT '[]'::jsonb"
    }
    
    # ADICIONA SOMENTE AS QUE FALTAM
    colunas_adicionadas = 0
    for nome_coluna, definicao in colunas_necessarias.items():
        if nome_coluna not in colunas_existentes:
            try:
                cursor.execute(f"ALTER TABLE orcamentos ADD COLUMN {nome_coluna} {definicao}")
                print(f"✅ Coluna '{nome_coluna}' adicionada!")
                colunas_adicionadas += 1
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna '{nome_coluna}': {e}")
    
    if colunas_adicionadas > 0:
        print(f"✅ {colunas_adicionadas} coluna(s) adicionada(s)!")
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")