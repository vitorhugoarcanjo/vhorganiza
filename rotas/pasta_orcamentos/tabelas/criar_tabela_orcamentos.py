# rotas/pasta_orcamentos/tabelas/criar_tabela_orcamentos.py
# ==========================================================
# TABELA DE ORÇAMENTOS — Padrão 2099
# ==========================================================

def tabela_orcamento(cursor, tipo_banco='postgresql'):
    # ==========================================================
    # VERIFICA SE A TABELA EXISTE
    # ==========================================================
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orcamentos')")
    tabela_existe = cursor.fetchone()[0]

    # ==========================================================
    # CRIA A TABELA COMPLETA (primeira vez)
    # ==========================================================
    if not tabela_existe:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orcamentos (
                -- IDENTIFICAÇÃO
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
                sequencia_orcamentos INTEGER,
                numero VARCHAR(30),

                -- DADOS DO ORÇAMENTO
                titulo VARCHAR(200) NOT NULL,
                cliente VARCHAR(200),
                descricao TEXT,
                status VARCHAR(20) DEFAULT 'rascunho',
                estrutura JSONB DEFAULT '[]'::jsonb,
                valor_total NUMERIC(12,2) DEFAULT 0,

                -- DATAS DE NEGÓCIO
                data_emissao DATE DEFAULT CURRENT_DATE,
                data_validade DATE,
                data_entrega DATE,

                -- DATAS DE STATUS (automáticas)
                enviado_em TIMESTAMP,
                aprovado_em TIMESTAMP,
                rejeitado_em TIMESTAMP,
                pdf_gerado_em TIMESTAMP,

                -- CONTROLE
                motivo_rejeicao TEXT,
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                excluido_em TIMESTAMP,
                excluido_por INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("✅ Tabela 'orcamentos' criada com sucesso!")
        return

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

    # ==========================================================
    # COLUNAS QUE DEVEM EXISTIR (ordem de adição)
    # ==========================================================
    colunas_necessarias = {
        # CONTROLE
        'ativo':                 'INTEGER DEFAULT 1',
        'excluido_em':           'TIMESTAMP',
        'excluido_por':          'INTEGER',

        # SEQUÊNCIA VISUAL
        'sequencia_orcamentos':  'INTEGER',

        # NÚMERO FORMATADO
        'numero':                'VARCHAR(30)',

        # DADOS EXTRAS
        'descricao':             'TEXT',
        'valor_total':           'NUMERIC(12,2) DEFAULT 0',

        # DATAS DE NEGÓCIO
        'data_emissao':          'DATE DEFAULT CURRENT_DATE',
        'data_validade':         'DATE',
        'data_entrega':          'DATE',

        # DATAS DE STATUS
        'enviado_em':            'TIMESTAMP',
        'aprovado_em':           'TIMESTAMP',
        'rejeitado_em':          'TIMESTAMP',
        'pdf_gerado_em':         'TIMESTAMP',

        # CONTROLE EXTRA
        'motivo_rejeicao':       'TEXT',
        'observacoes':           'TEXT',
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

    # ==========================================================
    # BACKFILL — POPULAR DADOS NAS COLUNAS NOVAS
    # ==========================================================

    # 1. sequencia_orcamentos (por usuário, ordem de id)
    if 'sequencia_orcamentos' not in colunas_existentes:
        cursor.execute("""
            UPDATE orcamentos o
            SET sequencia_orcamentos = sub.rn
            FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY usuario_id ORDER BY id) AS rn
                FROM orcamentos
            ) sub
            WHERE o.id = sub.id AND o.sequencia_orcamentos IS NULL
        """)
        print("✅ Sequências populadas pros registros existentes!")

    # 2. data_emissao (usar created_at como base)
    if 'data_emissao' not in colunas_existentes:
        cursor.execute("""
            UPDATE orcamentos
            SET data_emissao = DATE(created_at)
            WHERE data_emissao IS NULL AND created_at IS NOT NULL
        """)
        print("✅ data_emissao populada (a partir do created_at)!")

    # 3. numero (formatar ORC-YYYY-NNNN)
    if 'numero' not in colunas_existentes:
        cursor.execute("""
            UPDATE orcamentos
            SET numero = 'ORC-' || TO_CHAR(created_at, 'YYYY') || '-' ||
                         LPAD(sequencia_orcamentos::text, 4, '0')
            WHERE numero IS NULL AND sequencia_orcamentos IS NOT NULL
        """)
        print("✅ numero formatado (ORC-YYYY-NNNN)!")

    # ==========================================================
    # RESULTADO
    # ==========================================================
    if colunas_adicionadas > 0:
        print(f"✅ {colunas_adicionadas} coluna(s) adicionada(s)!")
    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")