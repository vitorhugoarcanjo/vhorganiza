# 05 — Auditoria

## 5.1 Tabela

```sql
CREATE TABLE <modulo>_auditoria (
    id SERIAL PRIMARY KEY,
    <x>_id INTEGER,                        -- FK pro ID INTERNO
    acao VARCHAR(50),                      -- criada, editada, inativada, reativada
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

## 5.2 Service `registrar()`

```python
@staticmethod
def registrar(<x>_id, acao, campo_alterado=None,
              valor_antigo=None, valor_novo=None, conexao=None):
    """
    Se `conexao` fornecida → usa a MESMA (transacional) — não faz commit.
    """
    propria_conexao = False
    try:
        if conexao is None:
            conexao, cursor = AuditoriaService.get_db_connection()
            propria_conexao = True
        else:
            cursor = conexao.cursor()

        if valor_antigo and len(str(valor_antigo)) > 2000:
            valor_antigo = str(valor_antigo)[:2000] + "..."
        if valor_novo and len(str(valor_novo)) > 2000:
            valor_novo = str(valor_novo)[:2000] + "..."

        cursor.execute("""
            INSERT INTO <modulo>_auditoria
            (<x>_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            <x>_id, acao, campo_alterado, valor_antigo, valor_novo,
            session.get('user_id'), request.remote_addr
        ))

        if propria_conexao:
            conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")
        if propria_conexao:
            conexao.rollback()
        return False
```

## 5.3 Listagem formatada

```python
colunas = [
    'id', '<x>_id', 'acao', 'campo_alterado',
    'valor_antigo', 'valor_novo', 'usuario_id', 'data_hora', 'ip',
    'usuario_nome', 'data_hora_br'
]

cursor.execute("""
    SELECT
        ta.id, ta.<x>_id, ta.acao, ta.campo_alterado,
        ta.valor_antigo, ta.valor_novo, ta.usuario_id, ta.data_hora, ta.ip,
        u.nome as usuario_nome,
        TO_CHAR(ta.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br
    FROM <modulo>_auditoria ta
    LEFT JOIN cadastre_se u ON ta.usuario_id = u.id
    WHERE ta.<x>_id = %s
    ORDER BY ta.data_hora DESC
    LIMIT %s
""", (<x>_id, limite))

auditoria = []
for row in cursor.fetchall():
    item = dict(zip(colunas, row))    # 🔥 NUNCA dict(row)
    item['data_hora'] = item.get('data_hora_br') or str(item.get('data_hora') or '')
    item['alteracoes'] = []

    if item.get('campo_alterado') == 'multiplos' and item.get('valor_novo'):
        try:
            item['alteracoes'] = json.loads(item['valor_novo'])
        except Exception:
            item['alteracoes'] = []

    auditoria.append(item)
```

## 5.4 View (traduz sequência → id)

```python
@login_required
def historico_<x>(<x>_seq):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT id, sequencia_<modulo>, <campos_header>
        FROM <tabela>
        WHERE sequencia_<modulo> = %s AND usuario_id = %s
    """, (<x>_seq, user_id))
    row = cursor.fetchone()
    if not row:
        return '', 404

    id_interno = row[0]
    <x> = (row[1], row[2], ...)

    historico = AuditoriaService.listar_por_<x>_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja',
        historico=historico,
        <x>=<x>,
        <x>_seq=<x>_seq,
    )
```

## 5.5 JSON de alterações

**Padrão:** `[{campo, antes, depois}]`

**Quando usar:**
- **`multiplos`** — 2+ campos (criar, editar, concluir, reabrir)
- **1 campo** — 1 campo só (inativar, reativar, quitar)

**Formato editada:**
```json
[
    {"campo": "Status", "antes": "pendente", "depois": "concluido"},
    {"campo": "Data Finalização", "antes": "(vazio)", "depois": "04/10/2026 15:46:23"}
]
```

**Formato criada (sem `antes`):**
```json
[
    {"campo": "Título", "depois": "Teste"},
    {"campo": "Categoria", "depois": "Trabalho"}
]
```

**Formato especial (Orçamento — estrutura JSONB):**
```json
[
    {"campo": "Número", "depois": "ORC-2026-0004"},
    {"campo": "Título", "depois": "Orçamento X"},
    {"campo": "📋 Blocos do Orçamento", "depois": "6 bloco(s)"},
    {"campo": "• Bloco 1 (cabecalho)", "depois": "ORÇAMENTO"},
    {"campo": "• Bloco 2 (secao)", "depois": "1. OBJETIVO"}
]
```