# 03 — Banco de Dados

## 3.1 Colunas obrigatórias em TODA tabela principal

```sql
-- IDENTIFICAÇÃO
id SERIAL PRIMARY KEY,
usuario_id INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
sequencia_<modulo> INTEGER,          -- # visual POR USUÁRIO
numero VARCHAR(30),                  -- ORC-2026-0001, TAR-2026-0001

-- DADOS
<campos específicos do módulo>

-- VALORES CACHEADOS
valor_total NUMERIC(12,2) DEFAULT 0,

-- DATAS DE NEGÓCIO
data_emissao DATE DEFAULT CURRENT_DATE,
data_validade DATE,
data_entrega DATE,

-- DATAS DE STATUS
<status>_em TIMESTAMP,               -- enviado_em, aprovado_em, rejeitado_em
pdf_gerado_em TIMESTAMP,

-- CONTROLE
<motivo>_rejeicao TEXT,
observacoes TEXT,
ativo INTEGER DEFAULT 1,
excluido_em TIMESTAMP,
excluido_por INTEGER,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## 3.2 Índices obrigatórios

- **Único:** `(usuario_id, sequencia_<modulo>)` — garante sequência única
- **Busca:** `(usuario_id, ativo)` — filtro de listagem
- **Data:** `(data_emissao DESC)` — ordenação
- **Status:** `(status)` — filtro
- **Número:** `(numero)` — busca

## 3.3 Backfill automático

**Toda migração de coluna nova DEVE ter backfill:**

```sql
-- 1. Adicionar coluna
ALTER TABLE <tabela> ADD COLUMN IF NOT EXISTS <coluna> <tipo>;

-- 2. Popular sequência por usuário
UPDATE <tabela>
SET sequencia_<modulo> = sub.rn
FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY usuario_id ORDER BY id) AS rn
    FROM <tabela>
) sub
WHERE <tabela>.id = sub.id AND <tabela>.sequencia_<modulo> IS NULL;

-- 3. Formatar numero
UPDATE <tabela>
SET numero = '<PREFIXO>-' || TO_CHAR(created_at, 'YYYY') || '-' ||
             LPAD(sequencia_<modulo>::text, 4, '0')
WHERE numero IS NULL;

-- 4. Backfill de valor_total (exemplo Orçamento)
UPDATE orcamentos
SET valor_total = (
    SELECT COALESCE(SUM(
        NULLIF(REPLACE(REPLACE(REPLACE(item->>'valor', 'R$', ''), '.', ''), ',', '.'), '')::numeric
    ), 0)
    FROM jsonb_array_elements(estrutura) item
    WHERE item->>'tipo' = 'valor'
)
WHERE valor_total = 0 OR valor_total IS NULL;
```

## 3.4 Tabela de auditoria (padrão único)

```sql
CREATE TABLE <modulo>_auditoria (
    id SERIAL PRIMARY KEY,
    <x>_id INTEGER,                        -- FK pro ID INTERNO
    acao VARCHAR(50),                      -- criada, editada, inativada, etc
    campo_alterado VARCHAR(100),           -- 'multiplos' ou 1 campo
    valor_antigo TEXT,
    valor_novo TEXT,                       -- JSON quando 'multiplos'
    usuario_id INTEGER,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45),
    FOREIGN KEY (<x>_id) REFERENCES <tabela>(id),
    FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
);
```

## 3.5 Convenções de nomes

| Elemento | Padrão |
|----------|--------|
| Tabela principal | `<plural>` (ex: `orcamentos`, `transacoes`, `tarefas`) |
| Tabela auditoria | `<plural>_auditoria` (ex: `orcamentos_auditoria`) |
| ID interno | `id` (SERIAL) |
| ID do usuário | `usuario_id` (Finanças usa `user_id` — legado) |
| Sequência visual | `sequencia_<singular>` (ex: `sequencia_orcamentos`) |
| Número formatado | `numero` |
| Soft delete | `ativo` (1/0) |
| Exclusão | `excluido_em`, `excluido_por` |