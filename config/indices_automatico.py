def criar_indices(cursor):
    """Cria índices para otimizar consultas"""
    
    print("📊 Criando índices...")
    
    # Lista de índices (nome, tabela, colunas)
    indices = [
        # TAREFAS
        ("idx_tarefas_user_id", "tarefas", "user_id"),
        ("idx_tarefas_status", "tarefas", "status"),
        ("idx_tarefas_prioridade", "tarefas", "prioridade"),
        ("idx_tarefas_data_inicio", "tarefas", "data_inicio"),
        ("idx_tarefas_data_final", "tarefas", "data_final"),
        ("idx_tarefas_user_status", "tarefas", "user_id, status"),
        
        # TRANSAÇÕES
        ("idx_transacoes_user_id", "transacoes", "user_id"),
        ("idx_transacoes_tipo", "transacoes", "tipo"),
        ("idx_transacoes_status", "transacoes", "status"),
        ("idx_transacoes_data_emissao", "transacoes", "data_emissao"),
        ("idx_transacoes_data_vencimento", "transacoes", "data_vencimento"),
        ("idx_transacoes_user_tipo", "transacoes", "user_id, tipo"),
        ("idx_transacoes_user_status", "transacoes", "user_id, status"),
        ("idx_transacoes_user_data_emissao", "transacoes", "user_id, data_emissao"),
        
        # CATEGORIAS
        ("idx_categorias_tarefas_user_id", "categorias_tarefas", "user_id"),
        ("idx_categorias_financas_user_id", "categorias_financas", "user_id"),
        
        # LOGS
        ("idx_logs_acesso_user_id", "logs_acesso", "user_id"),
        ("idx_logs_acesso_data_hora", "logs_acesso", "data_hora"),
        ("idx_logs_acesso_rota", "logs_acesso", "rota"),
        ("idx_logs_erros_user_id", "logs_erros", "user_id"),
        ("idx_logs_erros_data_hora", "logs_erros", "data_hora"),
        ("idx_logs_ataques_ip", "logs_ataques", "ip"),
        ("idx_logs_ataques_data_hora", "logs_ataques", "data_hora"),
        
        # AUDITORIA
        ("idx_auditoria_tarefa_id", "tarefas_auditoria", "tarefa_id"),
        ("idx_auditoria_usuario_id", "tarefas_auditoria", "usuario_id"),
        ("idx_auditoria_data_hora", "tarefas_auditoria", "data_hora"),
        ("idx_auditoria_acao", "tarefas_auditoria", "acao"),
    ]
    
    for nome, tabela, colunas in indices:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {nome} ON {tabela}({colunas})")
            print(f"  ✅ Índice {nome} criado/verificado")
        except Exception as e:
            print(f"  ⚠️ Erro ao criar índice {nome}: {e}")
    
    print("✅ Índices criados/verificados com sucesso!")