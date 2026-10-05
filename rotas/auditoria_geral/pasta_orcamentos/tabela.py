# rotas/auditoria_geral/pasta_orcamentos/tabela.py
# ==========================================================
# TABELA DE AUDITORIA DE ORÇAMENTOS
# ==========================================================

def tabela_auditoria_orcamentos(cursor):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'orcamentos_auditoria'
        )
    """)
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:
        cursor.execute("""
            CREATE TABLE orcamentos_auditoria (
                id SERIAL PRIMARY KEY,
                orcamento_id INTEGER,
                acao VARCHAR(50),               -- 'criada', 'editada', 'excluida'
                campo_alterado VARCHAR(100),
                valor_antigo TEXT,
                valor_novo TEXT,
                usuario_id INTEGER,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip VARCHAR(45),
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id),
                FOREIGN KEY (usuario_id)   REFERENCES cadastre_se(id)
            )
        """)
        print("✅ Tabela 'orcamentos_auditoria' criada com sucesso!")
        return

    print("ℹ️ Tabela 'orcamentos_auditoria' já existe.")