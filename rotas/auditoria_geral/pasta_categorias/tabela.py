# rotas/auditoria_geral/pasta_categorias/tabela.py
# ==========================================================
# TABELA DE AUDITORIA DE CATEGORIAS
# ==========================================================


def tabela_auditoria_categorias(cursor):
    """Cria a tabela categorias_auditoria se não existir"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'categorias_auditoria'
        )
    """)
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
            CREATE TABLE categorias_auditoria (
                id SERIAL PRIMARY KEY,
                categoria_id INTEGER,
                acao VARCHAR(50),
                campo_alterado VARCHAR(100),
                valor_antigo TEXT,
                valor_novo TEXT,
                usuario_id INTEGER,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip VARCHAR(45),
                FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
            )
        """)
        print("✅ Tabela categorias_auditoria criada com sucesso.")
    else:
        print("ℹ️ Tabela categorias_auditoria já existe.")