"""import os
import shutil
from datetime import datetime

def migrar_transacoes_com_backup(cursor, caminho_banco):
    
    # =====================================================
    # 1. BACKUP DO BANCO INTEIRO (.db)
    # =====================================================
    pasta_backup = os.path.join(os.path.dirname(caminho_banco), "backup")
    os.makedirs(pasta_backup, exist_ok=True)

    data = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(pasta_backup, f"banco_backup_{data}.db")

    shutil.copy2(caminho_banco, backup_path)

    print(f"✅ BACKUP DO BANCO CRIADO: {backup_path}")

    # =====================================================
    # 2. RENOMEIA TABELA ANTIGA
    # =====================================================
    cursor.execute("""
        ALTER TABLE transacoes RENAME TO transacoes_backup
    """)
    print("✅ Tabela antiga renomeada")

    # =====================================================
    # 3. CRIA NOVA TABELA COM FK
    # =====================================================
    cursor.execute("""
        CREATE TABLE transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,

            sequencia_transacoes INTEGER,

            tipo TEXT,
            descricao TEXT,

            categoria_id INTEGER,

            data_emissao DATE,
            data_vencimento DATE,
            data_quitamento DATE,
            data_alteracao DATE,

            valor_total REAL,
            valor_parcela REAL,

            numero_parcela INTEGER,
            total_parcelas INTEGER,

            status TEXT DEFAULT 'aberto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES cadastre_se(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias_financas(id) ON DELETE SET NULL
        )
    """)
    print("✅ Nova tabela criada com FK")

    # =====================================================
    # 4. MIGRA DADOS
    # =====================================================
    cursor.execute("""
        INSERT INTO transacoes (
            id,
            user_id,
            sequencia_transacoes,
            tipo,
            descricao,
            categoria_id,
            data_emissao,
            data_vencimento,
            data_quitamento,
            data_alteracao,
            valor_total,
            valor_parcela,
            numero_parcela,
            total_parcelas,
            status,
            created_at
        )
        SELECT 
            id,
            user_id,
            sequencia_transacoes,
            tipo,
            descricao,
            NULL,
            data_emissao,
            data_vencimento,
            data_quitamento,
            data_alteracao,
            valor_total,
            valor_parcela,
            numero_parcela,
            total_parcelas,
            status,
            created_at
        FROM transacoes_backup
    """)
    print("✅ Dados migrados com sucesso")

    print("🎯 MIGRAÇÃO FINALIZADA COM BACKUP SEGURO")
    """