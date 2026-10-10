# config/indices_automatico.py
# ==========================================================
# ÍNDICES AUTOMÁTICOS (padronizado usuario_id)
# ==========================================================

def criar_indices(cursor):
    """Cria índices para otimizar consultas"""

    print("📊 Criando índices...")

    indices = [
        # TAREFAS
        ("idx_tarefas_usuario_id", "tarefas", "usuario_id"),
        ("idx_tarefas_status", "tarefas", "status"),
        ("idx_tarefas_prioridade", "tarefas", "prioridade"),
        ("idx_tarefas_data_inicio", "tarefas", "data_inicio"),
        ("idx_tarefas_data_final", "tarefas", "data_final"),
        ("idx_tarefas_usuario_status", "tarefas", "usuario_id, status"),

        # TRANSAÇÕES
        ("idx_transacoes_usuario_id", "transacoes", "usuario_id"),
        ("idx_transacoes_tipo", "transacoes", "tipo"),
        ("idx_transacoes_status", "transacoes", "status"),
        ("idx_transacoes_data_emissao", "transacoes", "data_emissao"),
        ("idx_transacoes_data_vencimento", "transacoes", "data_vencimento"),
        ("idx_transacoes_usuario_tipo", "transacoes", "usuario_id, tipo"),
        ("idx_transacoes_usuario_status", "transacoes", "usuario_id, status"),
        ("idx_transacoes_usuario_data_emissao", "transacoes", "usuario_id, data_emissao"),
        ("idx_transacoes_pai", "transacoes", "transacao_pai_id"),
        ("idx_transacoes_usuario_pai", "transacoes", "usuario_id, transacao_pai_id"),
        ("idx_transacoes_usuario_ativo", "transacoes", "usuario_id, ativo"),
        ("idx_transacoes_usuario_ativo_emissao", "transacoes", "usuario_id, ativo, data_emissao DESC"),
        ("idx_transacoes_usuario_sequencia", "transacoes", "usuario_id, sequencia_transacoes"),
        ("idx_transacoes_sequencia_usuario", "transacoes", "sequencia_transacoes, usuario_id"),
        ("idx_transacoes_categoria_id", "transacoes", "categoria_id"),

        # CATEGORIAS
        ("idx_categorias_tarefas_usuario_id", "categorias_tarefas", "usuario_id"),
        ("idx_categorias_financas_usuario_id", "categorias_financas", "usuario_id"),

        # LOGS
        ("idx_logs_acesso_usuario_id", "logs_acesso", "usuario_id"),
        ("idx_logs_acesso_data_hora", "logs_acesso", "data_hora"),
        ("idx_logs_acesso_rota", "logs_acesso", "rota"),
        ("idx_logs_erros_usuario_id", "logs_erros", "usuario_id"),
        ("idx_logs_erros_data_hora", "logs_erros", "data_hora"),
        ("idx_logs_ataques_ip", "logs_ataques", "ip"),
        ("idx_logs_ataques_data_hora", "logs_ataques", "data_hora"),

        # AUDITORIA
        ("idx_auditoria_tarefa_id", "tarefas_auditoria", "tarefa_id"),
        ("idx_auditoria_usuario_id", "tarefas_auditoria", "usuario_id"),
        ("idx_auditoria_data_hora", "tarefas_auditoria", "data_hora"),
        ("idx_auditoria_acao", "tarefas_auditoria", "acao"),

        # ORÇAMENTOS
        ("idx_orcamentos_usuario_id", "orcamentos", "usuario_id"),
        ("idx_orcamentos_status", "orcamentos", "status"),
        ("idx_orcamentos_cliente", "orcamentos", "cliente"),
        ("idx_orcamentos_created_at", "orcamentos", "created_at"),
        ("idx_orcamentos_usuario_status", "orcamentos", "usuario_id, status"),
        ("idx_orcamentos_usuario_created", "orcamentos", "usuario_id, created_at DESC"),
        ("idx_orcamentos_cliente_status", "orcamentos", "cliente, status"),
        ("idx_orcamentos_usuario_ativo", "orcamentos", "usuario_id, ativo"),
        ("idx_orcamentos_sequencia", "orcamentos", "sequencia_orcamentos"),
        ("idx_orcamentos_numero", "orcamentos", "numero"),
        ("idx_orcamentos_data_emissao", "orcamentos", "data_emissao DESC"),
        ("idx_orcamentos_data_validade", "orcamentos", "data_validade"),
        ("idx_orcamentos_usuario_data_emissao", "orcamentos", "usuario_id, data_emissao DESC"),
    ]

    for nome, tabela, colunas in indices:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {nome} ON {tabela}({colunas})")
            print(f"  ✅ Índice {nome} criado/verificado")
        except Exception as e:
            print(f"  ⚠️ Erro ao criar índice {nome}: {e}")

    print("✅ Índices criados/verificados com sucesso!")