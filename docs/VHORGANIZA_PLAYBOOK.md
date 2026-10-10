# VHORGANIZA — PLAYBOOK 2099
## Padrão de desenvolvimento do sistema (Flask + HTMX + JS modular + Auditoria)

**Versão:** 3.0 (pós-Orçamento 2099)
**Data:** Outubro/2026
**Módulos de referência:** Finanças + Tarefas (100%) + Orçamentos (95%)

---

## 1. VISÃO GERAL

### 1.1 Stack
- **Backend:** Flask + PostgreSQL
- **Frontend:** HTMX + JS modular vanilla (sem framework)
- **Templates:** Jinja2
- **Build:** `python scripts/combine_static_<modulo>.py` (concatena JS/CSS em `<modulo>.min.js` e `<modulo>.min.css`)
- **Deploy:** Git → VPS (Contabo/Alemanha) → `systemctl restart gestao_financeira`
- **Latência prod:** ~200ms (Brasil ↔ Alemanha)

### 1.2 Princípios

1. **HTMX puro** — front só abre/fecha modal, backend devolve HTML + HX-Trigger
2. **1 arquivo = 1 responsabilidade** (1 JS por ação)
3. **Auditoria SEMPRE na view, transacional** (mesma `conexao`)
4. **FK da auditoria = `id` interno** (não sequência visual)
5. **JSON de alterações** = `[{campo, antes, depois}]` quando `campo_alterado='multiplos'`
6. **CSS compartilhado** em `components/` (não duplicar por módulo)
7. **Sem `onclick` inline** — sempre `data-*` + listener JS
8. **Sem `setTimeout` fixo** pra sincronizar com HTMX — usar `htmx:afterSwap`
9. **Respostas sempre `200`** (HTMX ignora `HX-Trigger` em 4xx/5xx)
10. **Colunas explícitas no SELECT** do `listar_*_formatado` + `dict(zip(colunas, row))`
11. **View magra** — toda regra de negócio vai pro `services.py` (não fica na view)
12. **Validação backend SEMPRE** — front ajuda, mas backend é a fonte da verdade
13. **Sequência visual por usuário** — cada user tem seu `#1, #2, #3`, não `id` global
14. **Cache de valores calculados** — `valor_total`, totais, etc salvos no banco
15. **Número formatado único** — `ORC-2026-0001` (não só `#1`)
16. **Soft delete SEMPRE** — `UPDATE ativo = 0`, nunca `DELETE FROM`
17. **Pós-insert = `htmx.ajax`** — recarrega só a tabela, nunca `window.location.reload()`
18. **Validação campo-a-campo no front** — borda vermelha + mensagem por campo

---

## 2. ESTRUTURA DE PASTAS

```
rotas/pasta_<modulo>/
├── __init__.py                 # Blueprint principal + register_blueprint dos CRUDs
├── <modulo>.py                 # Rotas principais (listagem, detalhes, limpar_filtros)
├── queries.py                  # SQL puro
├── filters.py                  # Filtros (session, query string)
├── formatters.py               # Serialização/dicionários
├── services/
│   └── services_<modulo>.py    # Service principal
└── crud/
    ├── pasta_insert/
    │   ├── __init__.py         # bp_insert + add_url_rule
    │   ├── insert_<x>.py       # View MAGRA (só orquestra) — AUDITORIA AQUI
    │   ├── services.py         # INSERT + regras (sequência, numero, valor_total)
    │   └── validacoes.py       # Validações backend + helpers
    ├── pasta_edit/
    │   ├── __init__.py
    │   ├── edit_<x>.py         # View + _montar_diff
    │   ├── services.py         # UPDATE + retorna dados_antes/dados_depois
    │   └── validacoes.py
    ├── pasta_delete/
    │   ├── __init__.py
    │   ├── delete_<x>.py       # View — AUDITORIA aqui
    │   └── services.py
    ├── pasta_<acao>/           # quitar/concluir, estornar/reabrir, reativar, etc
    │   ├── __init__.py
    │   ├── <acao>_<x>.py
    │   └── services.py

templates/pasta_<modulo>/
├── tela_<modulo>.html.jinja
├── _tabela_<modulo>.html.jinja         # Estrutura da tabela (thead + include do tbody)
├── modais/
│   ├── modal_nova_<x>.html.jinja
│   ├── modal_editar_<x>.html.jinja
│   └── excluir_<x>.html                # Modal confirmação
└── partials/
    ├── _tbody_<modulo>.html.jinja      # Loop + <tbody id="tbody-<modulo>">
    ├── _linha_<modulo>.html.jinja      # 1 linha da tabela
    └── form_<x>.html.jinja             # Form compartilhado novo/edit

templates/pasta_auditoria/pasta_<modulo>/
└── modal_auditoria.html.jinja          # Modal accordion

static/js/modules/pasta_<modulo>/
├── <modulo>.js                         # Orquestrador (só init + recarregarTabela)
├── core/
│   ├── formatadores.js
│   └── <X>Form.js                      # Classe compartilhada (create/edit)
├── components/
│   ├── totalizadores.js
│   ├── botoes_filtros.js
│   └── ordenacao.js
├── modals/
│   ├── <x>-nova.js
│   └── <x>-editar.js
└── acoes_e_modais/                     # 1 arquivo por ação
    ├── pasta_excluir/excluir_<x>.js
    ├── pasta_concluir/concluir_<x>.js
    ├── pasta_reabrir/reabrir_<x>.js
    ├── pasta_reativar/reativar_<x>.js
    ├── pasta_detalhes/detalhes_<x>.js
    └── pasta_auditoria/auditoria_<modulo>.js

static/css/
├── components/
│   ├── buttons.css                     # ✅ compartilhado
│   ├── filters.css
│   ├── footer.css
│   ├── tables.css
│   ├── modal.css                       # .fin-modal-* (full-screen)
│   ├── modal_confirmacao.css           # .modal-confirmacao-* (pequeno, cor variável)
│   ├── modal_detalhes.css              # .modal-detalhes-* (visualização)
│   ├── modal_auditoria.css             # accordion de auditoria
│   ├── form.css                        # form-grid, form-input, etc
│   └── notificacoes.css
└── core/
    ├── reset.css
    ├── responsive.css
    └── base_pos_acesso.css             # sidebar + variáveis CSS

rotas/auditoria_geral/
├── __init__.py                         # bp_auditoria (global, com prefixo /auditoria)
├── pasta_<modulo>/
│   ├── __init__.py                     # (vazio)
│   ├── logica_auditoria.py             # View: traduz sequencia→id, renderiza modal
│   ├── services_auditoria.py           # Service (registrar + listar)
│   └── tabela.py                       # Cria tabela de auditoria
```

---

## 3. BANCO DE DADOS — PADRÕES

### 3.1 Colunas obrigatórias em TODA tabela principal

```sql
-- IDENTIFICAÇÃO
id SERIAL PRIMARY KEY,
usuario_id INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
sequencia_<modulo> INTEGER,          -- # visual POR USUÁRIO (não id global)
numero VARCHAR(30),                  -- número formatado (ORC-2026-0001, TAR-2026-0001)

-- DADOS
<campos específicos do módulo>

-- VALORES CACHEADOS (se aplicável)
valor_total NUMERIC(12,2) DEFAULT 0,

-- DATAS DE NEGÓCIO
data_emissao DATE DEFAULT CURRENT_DATE,
data_validade DATE,                  -- opcional (ex: +30 dias)
data_entrega DATE,                   -- opcional (preenchido quando souber)

-- DATAS DE STATUS (automáticas — preenchidas quando muda status)
<status>_em TIMESTAMP,               -- enviado_em, aprovado_em, rejeitado_em, etc
pdf_gerado_em TIMESTAMP,

-- CONTROLE
<motivo>_rejeicao TEXT,              -- quando rejeitado/concluído
observacoes TEXT,                    -- campo livre (futuro)
ativo INTEGER DEFAULT 1,             -- soft delete
excluido_em TIMESTAMP,
excluido_por INTEGER,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### 3.2 Índices obrigatórios

- **Único:** `(usuario_id, sequencia_<modulo>)` — garante sequência única por usuário
- **Busca:** `(usuario_id, ativo)` — filtro de listagem
- **Data:** `(data_emissao DESC)` — ordenação
- **Status:** `(status)` — filtro
- **Número:** `(numero)` — busca por número

### 3.3 Backfill automático

**Toda migração de coluna nova DEVE ter backfill** (popular dados existentes):

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

### 3.4 Tabela de auditoria (padrão único)

```sql
CREATE TABLE <modulo>_auditoria (
    id SERIAL PRIMARY KEY,
    <x>_id INTEGER,                        -- FK pro ID INTERNO (não sequência)
    acao VARCHAR(50),                      -- criada, editada, inativada, reativada, etc
    campo_alterado VARCHAR(100),           -- 'multiplos' ou 1 campo ('ativo', 'status')
    valor_antigo TEXT,
    valor_novo TEXT,                       -- JSON quando campo_alterado='multiplos'
    usuario_id INTEGER,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45),
    FOREIGN KEY (<x>_id) REFERENCES <tabela>(id),    -- 🔥 id interno, NÃO sequência
    FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
);
```

---

## 4. BACKEND — PADRÕES

### 4.1 Blueprint principal (`__init__.py`)

```python
from flask import Blueprint

bp_<modulo> = Blueprint('<modulo>', __name__)

from .<modulo> import ini_<modulo>, detalhes_<x>, limpar_filtros
from .crud.pasta_insert   import bp_insert
from .crud.pasta_edit     import bp_edit
from .crud.pasta_delete   import bp_delete
# ...

bp_<modulo>.add_url_rule('/', view_func=ini_<modulo>, methods=['GET', 'POST'])
bp_<modulo>.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

bp_<modulo>.register_blueprint(bp_insert, url_prefix='')   # ← ou com prefixo
bp_<modulo>.register_blueprint(bp_edit,   url_prefix='')
# ...
```

**⚠️ IMPORTANTE:** o `url_prefix` varia por módulo. **Finanças** usa `/nova_transacao/`, **Orçamentos** usa `/` (registra direto em `/criar`).

### 4.2 View magra — só orquestra

**❌ ERRADO (faz tudo na view):**
```python
@login_required
def criar_orcamento():
    dados = request.get_json()
    # ... valida
    # ... calcula sequência
    # ... gera numero
    # ... INSERT
    # ... auditoria
    return jsonify(...)
```

**✅ CORRETO (view só orquestra):**
```python
from .services import InserirOrcamentoService
from .validacoes import validar_dados_insercao, limpar_texto, calcular_valor_total

@login_required
def criar_orcamento():
    user_id = session['user_id']
    conexao = None
    try:
        payload = request.get_json() or {}

        # 1. Sanitiza
        estrutura = payload.get('estrutura') or []
        dados = {
            'titulo':        limpar_texto(payload.get('titulo'), max_len=200),
            'cliente':       limpar_texto(payload.get('cliente'), max_len=200),
            'status':        (payload.get('status') or 'rascunho').strip().lower(),
            'estrutura':     estrutura,
            'valor_total':   calcular_valor_total(estrutura),
            'data_emissao':  payload.get('data_emissao') or None,
            'data_validade': payload.get('data_validade') or None,
            'data_entrega':  payload.get('data_entrega') or None,
        }

        # 2. Valida (backend)
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros, 'message': 'Dados inválidos.'}), 400

        # 3. Insere
        conexao, cursor = ini_conexao()
        sucesso, resultado = InserirOrcamentoService.criar_orcamento(cursor, user_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'message': resultado}), 400

        # 4. Auditoria
        alteracoes = InserirOrcamentoService.montar_alteracoes_auditoria(dados, resultado)
        AuditoriaOrcamentosService.registrar(
            orcamento_id=resultado['id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()
        return jsonify({
            'success': True,
            'message': f'Orçamento "{dados["titulo"]}" criado!',
            'id': resultado['id'],
            'sequencia': resultado['sequencia'],
            'numero': resultado['numero'],
        }), 201

    except Exception as e:
        if conexao:
            conexao.rollback()
        logger.exception(f"Erro ao criar user_id={user_id}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
```

### 4.3 Services — regras de negócio

**`services.py` (do insert) tem:**
- `get_proxima_sequencia(cursor, user_id)` → `MAX + 1`
- `gerar_numero(sequencia, ano)` → `ORC-2026-0004`
- `criar_<x>(cursor, user_id, dados)` → INSERT
- `montar_alteracoes_auditoria(dados, resultado)` → lista de dicts

**Regra:** service **não faz commit**. Quem faz é a view (transacional).

### 4.4 Validações backend — SEMPRE

**`validacoes.py` (do insert):**
- `limpar_texto(valor, max_len)` → sanitiza
- `parse_valor_br(valor_str)` → `"R$ 150,00"` → `150.0`
- `calcular_valor_total(estrutura)` → soma dos blocos tipo `valor`
- `validar_dados_insercao(dados)` → lista de erros `[{campo, mensagem}]`

**Regra:** front valida 1x, backend valida SEMPRE (front é burlável).

### 4.5 View HTMX — devolve HTML + HX-Trigger

**Para DELETE/INATIVAR/CONCLUIR/etc:**

```python
@login_required
def excluir_orcamento(sequencia):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        # 1. Busca id_interno + título ANTES
        cursor.execute("""
            SELECT id, titulo FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, user_id))
        resultado = cursor.fetchone()
        if not resultado:
            conexao.close()
            return '', 404

        id_interno, titulo = resultado[0], resultado[1]

        # 2. Inativa (soft delete)
        cursor.execute(
            OrcamentosQueries.inativar_orcamento(),
            (user_id, sequencia, user_id)
        )

        # 3. Auditoria transacional
        AuditoriaOrcamentosService.registrar(
            orcamento_id=id_interno,
            acao='inativada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        # 4. Retorna HTML + HX-Trigger
        html = _render_tbody(user_id, cursor)
        conexao.close()
        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'orcamentoInativado': {'message': f'Orçamento "{titulo}" inativado!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro: {e}")
        conexao.close()
        return '', 500
```

### 4.6 Helpers duplicados em TODOS os CRUDs

Toda view que devolve HTML tem:

```python
def _buscar_<x>_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = <Modulo>Filters.processar_filtros_data()
    filtros = <Modulo>Filters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
    })
    service = <Modulo>Services(conexao=None, cursor=cursor)
    <x>_raw = service.buscar_<x>(user_id, filtros)
    return <Modulo>Formatters.formatar_<x>(<x>_raw)


def _render_tbody(user_id, cursor):
    <x> = _buscar_<x>_com_filtros(cursor, user_id)
    return render_template(
        'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja',
        <x>=<x>,
        mostrar_inativas=session.get('<modulo>_mostrar_inativas', '0'),
    )
```

### 4.7 Filtros

- Data: `data_emissao` (não `created_at`)
- Tipo data: `'emissao'` (nunca `'inicio'`)
- Mostrar inativas: `'0'` (ativas), `'1'` (inativas), `'2'` (todas)

### 4.8 Sequência visual por usuário

```python
@staticmethod
def get_proxima_sequencia(cursor, user_id):
    """Retorna a próxima sequência visual pro usuário."""
    cursor.execute("""
        SELECT COALESCE(MAX(sequencia_<modulo>), 0) + 1
        FROM <tabela>
        WHERE usuario_id = %s
    """, (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 1
```

### 4.9 Número formatado

```python
@staticmethod
def gerar_numero(sequencia, ano=None):
    """Gera 'ORC-{ano}-{seq 4 dígitos}'."""
    if ano is None:
        ano = date.today().year
    return f'ORC-{ano}-{str(sequencia).zfill(4)}'
```

**Prefixos por módulo:**
- Orçamento: `ORC-2026-0001`
- Tarefa: `TAR-2026-0001`
- Transação: `TRN-2026-0001` (opcional)

---

## 5. AUDITORIA — PADRÃO 2099

### 5.1 Service `registrar()`

```python
@staticmethod
def registrar(<x>_id, acao, campo_alterado=None,
              valor_antigo=None, valor_novo=None, conexao=None):
    """
    Registra uma ação.
    Se `conexao` fornecida → usa a MESMA (transacional) — não faz commit.
    """
    propria_conexao = False
    try:
        if conexao is None:
            conexao, cursor = AuditoriaService.get_db_connection()
            propria_conexao = True
        else:
            cursor = conexao.cursor()

        # Trunca valores grandes
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

### 5.2 Listagem formatada

**Colunas explícitas + `dict(zip(colunas, row))`:**

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

### 5.3 View (traduz sequência → id)

```python
@login_required
def historico_<x>(<x>_seq):
    """Recebe a SEQUÊNCIA (URL: /auditoria/<x>/<seq>)."""
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

### 5.4 JSON de alterações

**Padrão:** lista de dicts `[{campo, antes, depois}]`.

**Quando usar:**
- **`multiplos`** — quando altera 2+ campos (criar, editar, concluir, reabrir, estornar)
- **1 campo** (`ativo`, `status`) — quando altera só 1 (inativar, reativar, quitar)

**Formato do `valor_novo` (editada):**
```json
[
    {"campo": "Status", "antes": "pendente", "depois": "concluido"},
    {"campo": "Data Finalização", "antes": "(vazio)", "depois": "04/10/2026 15:46:23"}
]
```

**Formato do `valor_novo` (criada — sem `antes`):**
```json
[
    {"campo": "Título", "depois": "Teste"},
    {"campo": "Categoria", "depois": "Trabalho"}
]
```

**Formato especial (Orçamento — estrutura):**

Para campos com estrutura complexa (JSONB), montar **um item por bloco**:

```json
[
    {"campo": "Número", "depois": "ORC-2026-0004"},
    {"campo": "Título", "depois": "Orçamento X"},
    {"campo": "Valor Total", "depois": "R$ 5.400,00"},
    {"campo": "Emissão", "depois": "2026-10-05"},
    {"campo": "Validade", "depois": "2026-11-04"},
    {"campo": "📋 Blocos do Orçamento", "depois": "6 bloco(s)"},
    {"campo": "• Bloco 1 (cabecalho)", "depois": "ORÇAMENTO"},
    {"campo": "• Bloco 2 (secao)", "depois": "1. OBJETIVO"},
    {"campo": "• Bloco 3 (lista)", "depois": "2. ENTREGÁVEIS (3 item(ns))"}
]
```

---

## 6. FRONTEND — PADRÕES

### 6.1 Classe `<X>Form` (core, compartilhada)

- **`mode: 'create'`** ou **`mode: 'edit'`**
- **`setData(data)`** — popula no edit
- **`getData()`** — serializa pro POST
- **`submit(url)`** — **SEMPRE JSON** + validações client-side
- **`reset()`** — limpa no create

### 6.2 Submits — semântica

- **insert/edit** → `fetch` + **JSON** (front valida + manda pra API)
- **delete/concluir/reabrir/reativar** → **HTMX puro** (backend devolve `<tbody>` + HX-Trigger)

### 6.3 Pós-insert = `htmx.ajax` (padrão 2099)

**NUNCA usar `window.location.reload()`.**

```javascript
if (data.success) {
    window.Notificacao.sucesso(data.message);
    fecharModal();

    // 🔥 Padrão 2099 — recarrega SÓ a tabela
    if (window.htmx) {
        window.htmx.ajax('GET', '/<modulo>/', {
            target: '#tabela-container',
            swap: 'outerHTML'
        });
    } else {
        window.location.reload();  // fallback
    }
}
```

### 6.4 Validação campo-a-campo no front

**Backend devolve `data.errors` com `[{campo, mensagem}]`.**

**Front pinta a borda + mensagem:**

```javascript
var MAPA_IDS = {
    'titulo':        'novoTitulo',
    'cliente':       'novoCliente',
    'status':        'novoStatus',
    'data_emissao':  'novoDataEmissao',
    'data_validade': 'novoDataValidade',
    'data_entrega':  'novoDataEntrega',
};

function mostrarErrosForm(errors) {
    // Limpa erros antigos
    document.querySelectorAll('.campo-erro').forEach(el => el.classList.remove('campo-erro'));
    document.querySelectorAll('.msg-erro-campo').forEach(el => el.remove());

    errors.forEach(er => {
        var inputId = MAPA_IDS[er.campo];
        if (!inputId) return;
        var input = document.getElementById(inputId);
        if (!input) return;

        input.classList.add('campo-erro');

        var msg = document.createElement('span');
        msg.className = 'msg-erro-campo';
        msg.textContent = er.mensagem;
        input.parentNode.appendChild(msg);
    });
}
```

**CSS:**

```css
.campo-erro {
    border: 2px solid #ef4444 !important;
    background: rgba(239, 68, 68, 0.05) !important;
}
.msg-erro-campo {
    display: block;
    color: #ef4444;
    font-size: 0.7rem;
    margin-top: 2px;
    font-weight: 500;
}
```

### 6.5 Padrão de ação HTMX (1 arquivo por ação)

```javascript
(function() {
    'use strict';

    let modalAberto = false;

    window.abrirModal<Acao><X> = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modal<Acao><X>');
        const titulo = document.getElementById('modal<Acao>Titulo');
        const texto = document.getElementById('modal<Acao>Texto');

        // 🔥 Clona botão pra limpar listeners HTMX antigos
        let btnConfirmar = document.getElementById('btnConfirmar<Acao><X>');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelar<Acao><X>');
        if (!modal || !btnConfirmar || !btnCancelar) return;

        modalAberto = true;
        if (titulo) titulo.textContent = config.titulo;
        if (texto) texto.textContent = config.texto;
        modal.classList.add('active');

        // 🔥 hx-post DINÂMICO
        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-<modulo>');
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        if (window.htmx) window.htmx.process(btnConfirmar);

        const fecharModal = () => {
            modal.classList.remove('active');
            modalAberto = false;
        };

        btnCancelar.onclick = fecharModal;
        modal.onclick = function(e) {
            if (e.target === modal) fecharModal();
        };

        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            const status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) fecharModal();
            btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
        });
    };

    // Delegação: clique no botão da linha
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-<acao>');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        window.abrirModal<Acao><X>({
            titulo: '<Ação> <X>',
            texto: 'Deseja <acao> a <x> "' + btn.dataset.titulo + '"?',
            url: '/<modulo>/<acao>_<x>/' + btn.dataset.sequencia
        });
    });

    // HX-Trigger → toast
    document.body.addEventListener('<x><Acao>da', function(evt) {
        modalAberto = false;
        const modal = document.getElementById('modal<Acao><X>');
        if (modal) modal.classList.remove('active');

        const msg = evt.detail && evt.detail.message ? evt.detail.message : '<X> <acao>da!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de <acao> <modulo> carregado!');
})();
```

### 6.6 Orquestrador `<modulo>.js`

**Só orquestra. Nada de lógica de ação.**

```javascript
(function() {
    'use strict';

    function recarregarTabela<Modulo>() {
        var tabelaContainer = document.getElementById('tabela-container');
        if (!tabelaContainer) return;
        var urlRefresh = tabelaContainer.dataset.urlRefresh || '/<modulo>';
        htmx.ajax('GET', urlRefresh, {
            target: '#tabela-container',
            swap: 'outerHTML'
        });
    }

    function init() {
        document.body.addEventListener('atualizarTabela<Modulo>', function() {
            recarregarTabela<Modulo>();
        });
    }

    window.recarregarTabela<Modulo> = recarregarTabela<Modulo>;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ <MODULO> - MAIN carregado!');
})();
```

### 6.7 Auditoria modal (accordion)

```javascript
(function() {
    'use strict';

    if (!window.fecharModalAuditoria) {
        window.fecharModalAuditoria = function() {
            const container = document.getElementById('modal-auditoria-container');
            if (container) container.innerHTML = '';
            document.body.style.overflow = '';
        };
    }

    if (!window.toggleAuditEntry) {
        window.toggleAuditEntry = function(headerEl) {
            const entry = headerEl.closest('.audit-entry');
            if (!entry) return;
            entry.classList.toggle('open');
        };
    }

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'modal-auditoria-container') {
            const modal = document.getElementById('modalAuditoria');
            if (modal) {
                modal.onclick = function(e) {
                    if (e.target === modal) window.fecharModalAuditoria();
                };
                const primeiro = modal.querySelector('.audit-entry');
                if (primeiro) primeiro.classList.add('open');
            }
            document.body.style.overflow = 'hidden';
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modalAuditoria');
            if (modal) window.fecharModalAuditoria();
        }
    });

    console.log('✅ Sistema de auditoria <Modulo> carregado!');
})();
```

---

## 7. TEMPLATES — PADRÕES

### 7.1 Estrutura da tabela (3 camadas de partial)

**`_tabela_<modulo>.html.jinja`:**
```jinja
<div id="tabela-container" data-url-refresh="{{ url_for('<modulo>.ini_<modulo>') }}">
    <div class="painel-tabela-conteudo scroll-fino">
        <div class="table-responsive">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th style="width: 65px;">Nº REG.</th>
                        <!-- outras colunas -->
                        <th style="width: 145px; text-align: center;">AÇÕES</th>
                    </tr>
                </thead>
                {% include 'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja' %}
            </table>
        </div>
    </div>
</div>
```

**`partials/_tbody_<modulo>.html.jinja`:**
```jinja
<tbody id="tbody-<modulo>">
    {% if <x> %}
        {% for <x> in <x>s %}
            {% include 'pasta_<modulo>/partials/_linha_<modulo>.html.jinja' %}
        {% endfor %}
    {% else %}
        <tr>
            <td colspan="9" class="text-center py-4 text-white-50">Nenhum registro encontrado.</td>
        </tr>
    {% endif %}
</tbody>
```

**`partials/_linha_<modulo>.html.jinja` — 1 linha com botões:**
```jinja
<tr data-sequencia="{{ <x>.sequencia }}" id="linha-<x>-{{ <x>.sequencia }}">
    <!-- colunas -->
    <td class="td-acoes text-center">
        <!-- DETALHES -->
        <button type="button" class="btn-acao view" title="Ver detalhes"
                onclick="verDetalhes<X>({{ <x>.sequencia }})">
            <i class="bi bi-eye"></i>
        </button>

        <!-- AUDITORIA -->
        <button type="button"
                class="btn-acao audit"
                hx-get="{{ url_for('auditoria.historico_<x>', <x>_seq=<x>.sequencia) }}"
                hx-target="#modal-auditoria-container"
                hx-swap="innerHTML"
                title="Ver histórico">
            <i class="bi bi-clock-history"></i>
        </button>

        {% if <x>.ativo == 1 %}
            <!-- EDITAR -->
            <button type="button" class="btn-acao edit"
                    onclick="abrirModalEditar({{ <x>.sequencia }})"
                    title="Editar">
                <i class="bi bi-pencil"></i>
            </button>

            <!-- EXCLUIR (inativar) -->
            <button type="button" class="btn-acao delete btn-excluir"
                    data-sequencia="{{ <x>.sequencia }}"
                    data-titulo="{{ <x>.titulo }}" title="Inativar">
                <i class="bi bi-trash"></i>
            </button>
        {% else %}
            <!-- REATIVAR -->
            <button type="button" class="btn-acao reativar btn-reativar"
                    data-sequencia="{{ <x>.sequencia }}"
                    data-titulo="{{ <x>.titulo }}" title="Reativar">
                <i class="bi bi-arrow-repeat"></i>
            </button>
        {% endif %}
    </td>
</tr>
```

### 7.2 Modal de auditoria (accordion)

**`pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja`:**
```jinja
<div class="fin-modal-overlay active" id="modalAuditoria">
    <div class="fin-modal-box">
        <div class="fin-modal-header">
            <h3>Auditoria — <X> #{{ <x>_seq }}</h3>
            <button class="fin-btn-close-modal" onclick="fecharModalAuditoria()">✕</button>
        </div>

        <div class="fin-modal-body">
            <div class="audit-wrapper">
                {% for item in historico %}
                <div class="audit-entry">
                    <div class="audit-entry-header" onclick="toggleAuditEntry(this)">
                        <div class="audit-entry-header-left">
                            <i class="bi bi-chevron-right audit-chevron"></i>
                            <span class="audit-badge audit-badge-{{ item.acao }}">
                                {% if item.acao == 'criada' %}✨ Criada
                                {% elif item.acao == 'editada' %}✏️ Editada
                                {% elif item.acao == 'inativada' %}🗑️ Inativada
                                {% elif item.acao == 'reativada' %}🔄 Reativada
                                {% else %}{{ item.acao }}
                                {% endif %}
                            </span>
                            <span class="audit-data-hora">{{ item.data_hora }}</span>
                        </div>
                        <span class="audit-usuario">
                            <i class="bi bi-person-circle"></i> {{ item.usuario_nome or 'Sistema' }}
                        </span>
                    </div>

                    <div class="audit-entry-body">
                        {% if item.alteracoes %}
                            <div class="audit-fields">
                                {% for alt in item.alteracoes %}
                                <div class="audit-field">
                                    <div class="audit-field-label">{{ alt.campo }}</div>
                                    <div class="audit-field-value">
                                        {% if alt.antes is defined and alt.antes is not none %}
                                            <span class="audit-old">{{ alt.antes }}</span>
                                            <i class="bi bi-arrow-right audit-arrow"></i>
                                        {% endif %}
                                        <span class="audit-new">{{ alt.depois or '(vazio)' }}</span>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        {% elif item.campo_alterado %}
                            <div class="audit-fields">
                                <div class="audit-field">
                                    <div class="audit-field-label">{{ item.campo_alterado }}</div>
                                    <div class="audit-field-value">
                                        {% if item.valor_antigo %}
                                            <span class="audit-old">{{ item.valor_antigo }}</span>
                                            <i class="bi bi-arrow-right audit-arrow"></i>
                                        {% endif %}
                                        <span class="audit-new">{{ item.valor_novo or '(vazio)' }}</span>
                                    </div>
                                </div>
                            </div>
                        {% else %}
                            <p class="audit-empty">Nenhuma alteração detalhada.</p>
                        {% endif %}
                        <div class="audit-footer">
                            <i class="bi bi-globe"></i> IP: {{ item.ip or '-' }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer-fixo-padrao">
            <button class="btn-footer-cancelar" onclick="fecharModalAuditoria()">
                <i class="bi bi-x-circle"></i> FECHAR
            </button>
            <h2>AUDITORIA</h2>
            <div class="contador-footer">
                <i class="bi bi-list-ul"></i> {{ historico|length }} registros
            </div>
        </div>
    </div>
</div>
```

### 7.3 Modal novo — exemplo Orçamento

**Campos mínimos:**
- **Título** (obrigatório)
- **Cliente** (obrigatório)
- **Data Emissão** (default: hoje)
- **Data Validade** (default: +30 dias)
- **Data Entrega** (opcional)
- **Status** (select)
- **Estrutura/Blocos** (JS renderiza)

**⚠️ NÃO usar `required` no HTML** — validação fica 100% backend.
**⚠️ NÃO usar `onchange="atualizarPreview()"`** — se a função não existe, quebra.

---

## 8. CSS COMPARTILHADO

### 8.1 `components/modal_auditoria.css`

```css
.audit-entry { background: var(--bg-card); border: 1px solid var(--border-sutil); border-radius: 8px; }
.audit-entry.open { border-color: rgba(37, 99, 235, 0.5); }

.audit-entry-header { display: flex; justify-content: space-between; padding: 12px 16px; cursor: pointer; }

.audit-chevron { transition: transform 0.2s ease; }
.audit-entry.open .audit-chevron { transform: rotate(90deg); }

.audit-badge-criada { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.audit-badge-editada { background: rgba(37, 99, 235, 0.15); color: #2563eb; }
.audit-badge-inativada { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.audit-badge-reativada { background: rgba(37, 99, 235, 0.15); color: #2563eb; }

.audit-entry-body { max-height: 0; overflow: hidden; transition: max-height 0.25s ease; }
.audit-entry.open .audit-entry-body { max-height: 2000px; border-top: 1px solid var(--border-sutil); }

.audit-field { padding: 8px 12px; background: var(--bg-principal); border-radius: 6px; }
.audit-old { color: #f87171; text-decoration: line-through; background: rgba(248, 113, 113, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-new { color: #4ade80; font-weight: 600; background: rgba(74, 222, 128, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-arrow { color: var(--texto-discreto); margin: 0 8px; }

/* Validação campo-a-campo */
.campo-erro {
    border: 2px solid #ef4444 !important;
    background: rgba(239, 68, 68, 0.05) !important;
}
.msg-erro-campo {
    display: block;
    color: #ef4444;
    font-size: 0.7rem;
    margin-top: 2px;
    font-weight: 500;
}
```

---

## 9. ARQUIVOS DE BUILD — `combina.py`

```python
JS_FILES = [
    'static/js/modules/pasta_<modulo>/core/<X>Form.js',
    'static/js/modules/pasta_<modulo>/components/totalizadores.js',
    'static/js/modules/pasta_<modulo>/components/botoes_filtros.js',
    'static/js/modules/pasta_<modulo>/components/ordenacao.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-nova.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-editar.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_excluir/excluir_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_<acao>/<acao>_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_auditoria/auditoria_<modulo>.js',
    'static/js/modules/pasta_<modulo>/<modulo>.js',
]

CSS_FILES = [
    'static/css/core/reset.css',
    'static/css/core/responsive.css',
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',
    'static/css/components/modal.css',
    'static/css/components/modal_confirmacao.css',
    'static/css/components/modal_detalhes.css',
    'static/css/components/modal_auditoria.css',
    'static/css/components/form.css',
    # específicos do módulo
]
```

⚠️ **NUNCA misturar CSS no `JS_FILES` nem JS no `CSS_FILES`**

⚠️ **IMPORTANTE:** rodar o build **DEPOIS** de substituir o JS, senão o bundle fica com a versão antiga.

---

## 10. ARMADILHAS CONHECIDAS

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `dict(row)` no `listar_formatado` | `object is not iterable` | Colunas explícitas + `dict(zip(colunas, row))` |
| Auditoria com `sequencia` (não `id`) | Modal abre vazio | View traduz `sequencia → id` |
| `campo_alterado='todos'` | JSON não é parseado | Usar `'multiplos'` |
| `converter_valor_br` sempre remove `.` | `1009.9` → `10099` | Check `if ',' in valor` |
| `setTimeout(50)` pra sync HTMX | Quebra em prod (200ms latência) | `htmx:afterSwap` |
| CSS no `JS_FILES` | `Uncaught SyntaxError` | Separar JS e CSS |
| `HX-Trigger` em resposta 4xx | HTMX ignora header | Sempre `200` |
| `session['user_id']` ausente | `KeyError` | `session.get('user_id')` |
| Categoria mostra ID | `19` em vez de `Trabalho` | Buscar `nome` no service |
| Data ISO crua | `2026-10-04` | Helper `_fmt_data_br` |
| `modal.onclick` sempre | Clicar dentro fecha | `event.stopPropagation()` no box |
| View faz INSERT direto | Código duplicado | Mover pro `services.py` |
| `required` no HTML | Validação burlável | Backend valida sempre |
| `onchange` pra função inexistente | `is not defined` no console | Remover ou criar a função |
| `window.location.reload()` pós-insert | Perde scroll/filtros | `htmx.ajax` só a tabela |
| Bundle desatualizado | JS novo não roda | Rodar build DEPOIS de editar |
| Coluna nova sem backfill | Antigos ficam NULL | SQL de backfill obrigatório |
| `data_emissao` no filtro errado | Orçamento de hoje não aparece | Filtrar por `data_emissao`, não `created_at` |

---

## 11. CHECKLIST — CRIAR MÓDULO NOVO

### Backend
- [ ] `rotas/pasta_<modulo>/__init__.py` (blueprint pai)
- [ ] `<modulo>.py` (view + `_buscar_<x>_com_filtros` + `_render_tbody`)
- [ ] `queries.py`, `filters.py`, `formatters.py`, `services/`
- [ ] `crud/pasta_insert/` (view magra + services.py + validacoes.py)
- [ ] `crud/pasta_edit/` (JSON + diff + auditoria)
- [ ] `crud/pasta_delete/` (HTML + HX-Trigger + auditoria)
- [ ] `crud/pasta_<acao>/` (reativar, concluir, etc)
- [ ] **Todas** as views: `logger.exception()`, `conexao.rollback()`, `conexao.close()`
- [ ] **Todas** as auditorias: `conexao=conexao`, `id_interno`, JSON `[{campo, antes, depois}]`
- [ ] **Toda** migração: SQL de backfill

### Auditoria
- [ ] `rotas/auditoria_geral/pasta_<modulo>/tabela.py`
- [ ] `services_auditoria.py` (com `conexao=None` + colunas explícitas + zip)
- [ ] `logica_auditoria.py` (traduz sequência → id)
- [ ] Registrar no `bp_auditoria`

### Frontend
- [ ] `core/<X>Form.js` (setData, getData, submit JSON, reset)
- [ ] `components/totalizadores.js`, `botoes_filtros.js`, `ordenacao.js`
- [ ] `modals/<x>-nova.js`, `<x>-editar.js` (com `htmx.ajax` pós-sucesso)
- [ ] `acoes_e_modais/pasta_<acao>/<acao>_<x>.js`
- [ ] `<modulo>.js` (só init + recarregarTabela)
- [ ] Validação campo-a-campo (`mostrarErrosForm`)
- [ ] **Zero** `setTimeout` fixo
- [ ] **Zero** `window.location.reload()` pós-insert

### Templates
- [ ] `tela_<modulo>.html.jinja`
- [ ] `_tabela_<modulo>.html.jinja`
- [ ] `partials/_tbody_<modulo>.html.jinja` + `_linha_<modulo>.html.jinja`
- [ ] `modais/modal_nova_<x>.html.jinja` + `modal_editar_<x>.html.jinja`
- [ ] `modais/excluir_<x>.html` + `reativar_<x>.html`
- [ ] `pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja`
- [ ] Containers na tela

### CSS
- [ ] Reaproveitar `components/`
- [ ] Específicos em `modules/pasta_<modulo>/`

### Build
- [ ] Ajustar `combine_static_<modulo>.py`
- [ ] Rodar build
- [ ] **Zero** `⚠️ não encontrado`

### Antes de subir
- [ ] Criar funciona (com sequência + numero)
- [ ] Editar (diff correto)
- [ ] Excluir/reativar
- [ ] Auditoria abre em modal
- [ ] Toast verde em todas ações
- [ ] Filtros preservam
- [ ] Console sem erro
- [ ] **Pós-insert recarrega só a tabela (não F5)**
- [ ] **Validação campo-a-campo funciona (borda vermelha)**
- [ ] **Testar em prod** (latência 200ms)

---

## 12. COMANDOS

```bash
# Build local
python scripts/combine_static_financas.py
python scripts/combine_static_tarefas.py
python scripts/combine_static_orcamentos.py

# Rodar Flask
python app.py

# Commit
git add .
git commit -m "feat: <modulo> padrao 2099"
git push origin <branch>

# Deploy
ssh usuario@vhorganiza.com.br
cd /var/www/vhorganiza
git fetch origin
git reset --hard origin/main
git clean -fd
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
sudo systemctl restart gestao_financeira

# Debug prod
journalctl -u gestao_financeira -n 50
```

---

## 13. REFERÊNCIAS

- HTMX: https://htmx.org/docs/
- HTMX events: https://htmx.org/events/
- OOB swaps: https://htmx.org/attributes/hx-swap-oob/
- Flask blueprints: https://flask.palletsprojects.com/en/latest/blueprints/

---

## FIM DO PLAYBOOK 2099 v3.0

> **Este documento é a fonte da verdade do padrão VHORGANIZA.**
> Ao criar novo módulo: siga seção 11 (checklist).
> Ao encontrar bug: adicione em seção 10 (armadilhas).
> Ao mudar padrão: atualize as seções correspondentes.