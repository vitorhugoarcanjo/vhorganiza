# rotas/pasta_categorias/crud/tabela/tabela_categorias.py
# ==========================================================
# CATEGORIAS UNIFICADAS - CRIAÇÃO DA TABELA
# ==========================================================

def tabela_categorias(cursor, tipo_banco='postgresql'):
    """
    Cria a tabela unificada 'categorias' (tarefas + finanças).
    Se já existe, verifica e adiciona colunas que faltam.
    Os índices são criados em config/indices_automatico.py.
    """
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'categorias'
        )
    """)
    tabela_existe = cursor.fetchone()[0]

    # ==========================================================
    # 1. CRIA A TABELA (se não existe)
    # ==========================================================
    if not tabela_existe:
        cursor.execute("""
            CREATE TABLE categorias (
                id                    SERIAL PRIMARY KEY,
                usuario_id            INTEGER,

                -- 🔥 MÓDULO (tarefas | financas)
                modulo                TEXT NOT NULL,

                -- IDENTIFICAÇÃO VISUAL
                sequencia_categorias  INTEGER,
                numero                VARCHAR(30),

                -- DADOS
                nome                  TEXT NOT NULL,
                cor                   TEXT DEFAULT '#CCCCCC',

                -- CONTROLE
                ativo                 INTEGER DEFAULT 1,
                excluido_em           TIMESTAMP,
                excluido_por          INTEGER,
                created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- FKs
                FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,

                -- CHECK do módulo
                CONSTRAINT chk_categorias_modulo
                    CHECK (modulo IN ('tarefas', 'financas'))
            )
        """)
        print("✅ Tabela 'categorias' criada com sucesso.")
        return

    # ==========================================================
    # 2. JÁ EXISTE — VERIFICA E ADICIONA COLUNAS QUE FALTAM
    # ==========================================================
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'categorias'
        ORDER BY ordinal_position
    """)
    colunas_existentes = [row[0] for row in cursor.fetchall()]

    # Colunas que devem existir (e o SQL de criação de cada uma)
    colunas_esperadas = {
        'modulo':               "modulo TEXT",
        'sequencia_categorias': "sequencia_categorias INTEGER",
        'numero':               "numero VARCHAR(30)",
        'ativo':                "ativo INTEGER DEFAULT 1",
        'excluido_em':          "excluido_em TIMESTAMP",
        'excluido_por':         "excluido_por INTEGER",
        'updated_at':           "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }

    colunas_para_adicionar = []
    for nome_coluna, sql_coluna in colunas_esperadas.items():
        if nome_coluna not in colunas_existentes:
            colunas_para_adicionar.append(sql_coluna)

    # Adiciona cada uma
    for coluna_sql in colunas_para_adicionar:
        try:
            nome_coluna = coluna_sql.split()[0]
            cursor.execute(f"ALTER TABLE categorias ADD COLUMN {coluna_sql}")
            print(f"✅ Coluna '{nome_coluna}' adicionada em categorias!")
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna {coluna_sql}: {e}")

    if colunas_para_adicionar:
        print(f"✅ {len(colunas_para_adicionar)} nova(s) coluna(s) adicionada(s) em categorias!")
    else:
        print("ℹ️ Tabela 'categorias' já está completa. Nada foi alterado.")