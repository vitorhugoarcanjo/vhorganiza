def criar_tabela_tarefas(cursor):
    cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='tarefas')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
        CREATE TABLE tarefas (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        categoria_id INTEGER,
        tarefa_sequencia INTEGER,
                       
        descricao TEXT NOT NULL,
        titulo VARCHAR(200),
        status TEXT DEFAULT 'pendente',
        prioridade TEXT DEFAULT 'media' CHECK (prioridade IN ('baixa', 'media', 'alta')),
                    
        data_inicio DATE,
        data_final DATE,
                       
        ativo INTEGER DEFAULT 1,
        excluido_em TIMESTAMP,
        excluido_por INTEGER,
                    
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_finalizacao DATE,
        motivo_conclusao TEXT,
                    
        FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
        FOREIGN KEY(categoria_id) REFERENCES categorias_tarefas(id) ON DELETE SET NULL
        )
    """)
        print("✅ Tabela tarefas criada com sucesso!")
        return

    # ==========================================================
    # VERIFICA E ADICIONA COLUNAS QUE FALTAM
    # ==========================================================
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'tarefas'
        ORDER BY ordinal_position
    """)
    colunas_existentes = [row[0] for row in cursor.fetchall()]
    
    colunas_para_adicionar = []
    
    if 'motivo_conclusao' not in colunas_existentes:
        colunas_para_adicionar.append("motivo_conclusao TEXT")
    
    if 'data_finalizacao' not in colunas_existentes:
        colunas_para_adicionar.append("data_finalizacao DATE")
    
    # Adiciona mais colunas se necessário
    
    for coluna_sql in colunas_para_adicionar:
        try:
            nome_coluna = coluna_sql.split()[0]
            cursor.execute(f"ALTER TABLE tarefas ADD COLUMN {coluna_sql}")
            print(f"✅ Coluna '{nome_coluna}' adicionada em tarefas!")
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna {coluna_sql}: {e}")
    
    if colunas_para_adicionar:
        print(f"✅ {len(colunas_para_adicionar)} nova(s) coluna(s) adicionada(s)!")
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")
