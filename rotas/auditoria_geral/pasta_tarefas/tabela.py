def tabela_auditoria_tarefas(cursor):

    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tarefas_auditoria')
""")
    tabela_existe = cursor.fetchone()[0]

    if not tabela_existe:    
        cursor.execute("""
        CREATE TABLE tarefas_auditoria (
        id SERIAL PRIMARY KEY,
        tarefa_id INTEGER,
        acao VARCHAR(50),  -- 'criada', 'editada', 'concluida', 'excluida', 'restaurada'
        campo_alterado VARCHAR(100),
        valor_antigo TEXT,
        valor_novo TEXT,
        usuario_id INTEGER,
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip VARCHAR(45),
        FOREIGN KEY (tarefa_id) REFERENCES tarefas(id),
        FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
        )
    """)
        print("✅ tabela tarefas_auditoria criada com sucesso!")
        return

    else:
        print("ℹ️ Todas as colunas já existem. Nada foi alterado.")