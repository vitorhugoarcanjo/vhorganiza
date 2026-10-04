# VHORGANIZA — PLAYBOOK 2099
## Padrão de desenvolvimento do sistema (Flask + HTMX + JS modular + Auditoria)

**Versão:** 2.0 (pós-refactor de auditoria)
**Data:** Outubro/2026
**Módulos de referência:** Finanças + Tarefas (ambos 100% no padrão)

---

## 1. VISÃO GERAL

### 1.1 Stack
- **Backend:** Flask + PostgreSQL
- **Frontend:** HTMX (navegação/tabela) + JS modular vanilla (formulários/modais)
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
    │   ├── insert_<x>.py       # View (GET modal + POST salvar) — AUDITORIA AQUI
    │   ├── services.py         # INSERT
    │   └── validacoes.py       # Validações + helpers
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
│   └── excluir_<x>.html                 # Modal confirmação
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

## 3. BACKEND — PADRÕES

### 3.1 Blueprint principal (`__init__.py`)

```python
from flask import Blueprint

bp_<modulo> = Blueprint('<modulo>', __name__)

# Imports das views
from .<modulo> import ini_<modulo>, detalhes_<x>, limpar_filtros

# Imports dos blueprints filhos
from .crud.pasta_insert   import bp_insert
from .crud.pasta_edit     import bp_edit
from .crud.pasta_delete   import bp_delete
from .crud.pasta_concluir import bp_concluir
from .crud.pasta_reabrir  import bp_reabrir
from .crud.pasta_reativar import bp_reativar

# Rotas principais
bp_<modulo>.add_url_rule('/', view_func=ini_<modulo>, methods=['GET', 'POST'])
bp_<modulo>.add_url_rule('/detalhes/<int:x_seq>', view_func=detalhes_<x>)
bp_<modulo>.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# Registro dos CRUDs (com prefixo)
bp_<modulo>.register_blueprint(bp_insert,   url_prefix='/nova_<x>')
bp_<modulo>.register_blueprint(bp_edit,     url_prefix='/edit_<x>')
bp_<modulo>.register_blueprint(bp_delete,   url_prefix='/excluir_<x>')
bp_<modulo>.register_blueprint(bp_concluir, url_prefix='/concluir_<x>')
bp_<modulo>.register_blueprint(bp_reabrir,  url_prefix='/reabrir_<x>')
bp_<modulo>.register_blueprint(bp_reativar, url_prefix='/reativar_<x>')
```

**Registro no `config/imports_rotas.py`:**
```python
from rotas.pasta_<modulo> import bp_<modulo>
app.register_blueprint(bp_<modulo>, url_prefix="/<modulo>")
```

### 3.2 Blueprint de CRUD

```python
# crud/pasta_<acao>/__init__.py
from flask import Blueprint

bp_<acao> = Blueprint('<acao>_<modulo>', __name__)

from .<acao>_<x> import <acao>_view  # ou editar_modal, dados_json, etc

bp_<acao>.add_url_rule('/<int:sequencia>', view_func=<acao>_view, methods=['POST'])
```

### 3.3 View principal — helpers

**`tarefas.py` / `financas.py` — sempre ter 2 helpers:**

```python
def _buscar_<x>_com_filtros(cursor, user_id):
    """Busca itens com filtros da sessão. Reaproveitado por TODOS os CRUDs."""
    data_inicio, data_fim, tipo_data = <Modulo>Filters.processar_filtros_data()
    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
        # ... outros filtros
    }
    service = <Modulo>Services(conexao=None, cursor=cursor)
    <x>_raw = service.buscar_<x>(user_id, filtros)
    return <Modulo>Formatters.formatar_<x>(<x>_raw)


def _render_tbody(user_id, cursor):
    """Renderiza só o <tbody>. Reaproveitado pelos CRUDs que devolvem HTML."""
    <x> = _buscar_<x>_com_filtros(cursor, user_id)
    return render_template(
        'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja',
        <x>=<x>,
        mostrar_inativas=session.get('mostrar_inativas', '0'),
    )
```

**Regra:** **todos os CRUDs** que devolvem HTML **copiam** esse helper (padrão do Finanças).

### 3.4 Padrão de view HTMX (devolve `<tbody>` + HX-Trigger)

```python
# crud/pasta_<acao>/<acao>_<x>.py
import logging
import json
from flask import session, make_response, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_<modulo>.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from rotas.pasta_<modulo>.services.services_<modulo> import <Modulo>Services
from rotas.pasta_<modulo>.filters import <Modulo>Filters
from rotas.pasta_<modulo>.formatters import <Modulo>Formatters

from .services import <Acao><X>Service

logger = logging.getLogger(__name__)


def _buscar_<x>_com_filtros(cursor, user_id):
    # ... (igual ao principal)
    pass


def _render_tbody(user_id, cursor):
    # ... (igual ao principal)
    pass


@login_required
def <acao>_view(sequencia):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        resultado = <Acao><X>Service.<acao>_<x>(cursor, sequencia, user_id)
        if not resultado.get('success'):
            conexao.close()
            return '', 404

        # 🔥 AUDITORIA com ID INTERNO
        AuditoriaService.registrar(
            <x>_id=resultado['id_interno'],           # ID interno (não sequência)
            acao='<acao>ada',                          # padrão: criada, editada, inativada...
            campo_alterado='ativo',                    # ou 'multiplos'
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,                           # 🔥 transacional
        )

        conexao.commit()

        html = _render_tbody(user_id, cursor)
        conexao.close()

        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            '<x><Acao>da': {'message': f'{Titulo} "{resultado["titulo"]}" <acao>da!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao <acao> {<x>} sequencia={sequencia} user_id={user_id}")
        conexao.close()
        return '', 500
```

### 3.5 Padrão do INSERT (com auditoria)

```python
@login_required
def salvar_nova_<x>():
    user_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        payload = request.json or {}
        dados = { ... }   # extrai do JSON

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        # 🔥 Busca o NOME da categoria ANTES (se tiver categoria)
        categoria_nome = <X>Service.buscar_nome_categoria(cursor, dados['categoria_id'])

        sucesso, resultado = <X>Service.criar_<x>(cursor, user_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400

        # 🔥 Auditoria — 1 registro com TODOS os campos
        alteracoes = [
            {'campo': 'Título',       'depois': dados['titulo']},
            {'campo': 'Descrição',    'depois': dados['descricao'] or '(vazio)'},
            {'campo': 'Status',       'depois': dados['status'].title()},
            {'campo': 'Prioridade',   'depois': dados['prioridade'].title()},
            {'campo': 'Data Início',  'depois': _fmt_data_br(dados['data_inicio']) or '(vazio)'},
            {'campo': 'Data Final',   'depois': _fmt_data_br(dados['data_final']) or '(vazio)'},
            {'campo': 'Categoria',    'depois': categoria_nome},
        ]

        AuditoriaService.registrar(
            <x>_id=resultado['<x>_id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'{Titulo} "{dados["titulo"]}" cadastrada com sucesso!',
            '<x>_sequencia': resultado['<x>_sequencia'],
            '<x>_id': resultado['<x>_id'],
        }), 201

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar nova {<x>} user_id={user_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor ao salvar.',
            'details': str(e)
        }), 500
    finally:
        conexao.close()
```

### 3.6 Padrão do EDIT (com diff)

**No service:**
```python
@staticmethod
def atualizar_<x>(cursor, sequencia, user_id, dados):
    <x>_atual = <X>Service.buscar_<x>_por_sequencia(cursor, sequencia, user_id)
    if not <x>_atual:
        return {'success': False, 'error': 'Não encontrada'}

    # Busca ID interno
    cursor.execute("SELECT id FROM <tabela> WHERE <seq_col> = %s AND user_id = %s",
                   (sequencia, user_id))
    id_interno = cursor.fetchone()[0]

    # 🔥 Busca o NOME da categoria ANTES
    categoria_antes_nome = <X>Service.buscar_nome_categoria(cursor, <x>_atual[7])

    # 🔥 Busca o NOME da categoria DEPOIS
    categoria_depois_nome = <X>Service.buscar_nome_categoria(cursor, dados.get('categoria_id'))

    # 🔥 dados_antes e dados_depois pra auditoria
    dados_antes = {
        'titulo':         <x>_atual[1],
        'descricao':      <x>_atual[2],
        'status':         <x>_atual[3],
        'data_inicio':    str(<x>_atual[4]) if <x>_atual[4] else '',
        'data_final':     str(<x>_atual[5]) if <x>_atual[5] else '',
        'categoria_nome': categoria_antes_nome,
        'prioridade':     <x>_atual[8],
    }
    dados_depois = {
        'titulo':         dados['titulo'],
        'descricao':      dados['descricao'],
        'status':         dados['status'],
        'data_inicio':    dados.get('data_inicio') or '',
        'data_final':     dados.get('data_final') or '',
        'categoria_nome': categoria_depois_nome,
        'prioridade':     dados['prioridade'],
    }

    cursor.execute("""
        UPDATE <tabela>
        SET ..., updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
    """, (..., id_interno, user_id))

    return {
        'success': True,
        'id_interno': id_interno,
        'dados_antes': dados_antes,
        'dados_depois': dados_depois,
    }
```

**Na view:**
```python
def _montar_diff(antes, depois):
    """Compara antes/depois e retorna lista de alterações."""
    mapa_campos = {
        'titulo':         'Título',
        'descricao':      'Descrição',
        'status':         'Status',
        'prioridade':     'Prioridade',
        'data_inicio':    'Data Início',
        'data_final':     'Data Final',
        'categoria_nome': 'Categoria',
    }

    alteracoes = []
    for campo, label in mapa_campos.items():
        v_antes = antes.get(campo)
        v_depois = depois.get(campo)

        # Formata datas BR
        if campo in ('data_inicio', 'data_final'):
            v_antes = _fmt_data_br(v_antes)
            v_depois = _fmt_data_br(v_depois)

        v_antes_s = str(v_antes or '').strip()
        v_depois_s = str(v_depois or '').strip()

        if v_antes_s != v_depois_s:
            alteracoes.append({
                'campo': label,
                'antes': v_antes_s or '(vazio)',
                'depois': v_depois_s or '(vazio)',
            })

    return alteracoes


@login_required
def salvar_edicao(sequencia):
    # ...
    resultado = <X>Service.atualizar_<x>(cursor, sequencia, user_id, dados)
    # ...

    # 🔥 Auditoria com DIFF
    alteracoes = _montar_diff(
        resultado.get('dados_antes', {}),
        resultado.get('dados_depois', {})
    )

    if alteracoes:
        AuditoriaService.registrar(
            <x>_id=resultado['id_interno'],
            acao='editada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

    conexao.commit()
```

---

## 4. AUDITORIA — PADRÃO 2099

### 4.1 Estrutura da tabela

```sql
CREATE TABLE <modulo>_auditoria (
    id SERIAL PRIMARY KEY,
    <x>_id INTEGER,                        -- FK pro ID INTERNO
    acao VARCHAR(50),                      -- criada, editada, inativada, reativada...
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

### 4.2 Service de auditoria

```python
@staticmethod
def registrar(<x>_id, acao, campo_alterado=None, valor_antigo=None,
              valor_novo=None, conexao=None):
    """
    Registra uma ação na auditoria.
    Se `conexao` fornecida, usa a MESMA (transacional) — não faz commit.
    """
    propria_conexao = False
    try:
        if conexao is None:
            conexao, cursor = AuditoriaService.get_db_connection()
            propria_conexao = True
        else:
            cursor = conexao.cursor()      # 🔥 cursor novo na MESMA conexão

        # ... INSERT ...

        if propria_conexao:
            conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")
        if propria_conexao:
            conexao.rollback()
        return False
```

### 4.3 Listagem formatada (colunas explícitas + zip)

```python
@staticmethod
def listar_por_<x>_formatado(<x>_id, limite=50):
    """Lista auditoria com formatação."""
    try:
        conexao, cursor = AuditoriaService.get_db_connection()

        # 🔥 COLUNAS EXPLÍCITAS (evita bug de dict(row))
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
            # 🔥 dict(zip()) — NUNCA dict(row)
            item = dict(zip(colunas, row))
            item['data_hora'] = item.get('data_hora_br') or str(item.get('data_hora') or '')
            item['alteracoes'] = []

            # Padrão 2099: só 'multiplos' tem lista
            if item.get('campo_alterado') == 'multiplos' and item.get('valor_novo'):
                try:
                    item['alteracoes'] = json.loads(item['valor_novo'])
                except Exception:
                    item['alteracoes'] = []

            auditoria.append(item)

        return auditoria
    except Exception as e:
        print(f"Erro ao listar auditoria formatada: {e}")
        return []
```

### 4.4 View (traduz sequência → id)

```python
@login_required
def historico_<x>(<x>_seq):
    """
    Recebe a SEQUÊNCIA (URL: /auditoria/<x>/<seq>).
    Traduz pra ID interno e busca auditoria.
    """
    user_id = session['user_id']
    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT id, <seq_col>, <campos_header>
        FROM <tabela>
        WHERE <seq_col> = %s AND user_id = %s
    """, (<x>_seq, user_id))
    row = cursor.fetchone()

    if not row:
        return '', 404

    id_interno = row[0]
    <x> = (row[1], row[2], ...)   # tupla no formato do template

    historico = AuditoriaService.listar_por_<x>_formatado(id_interno)

    return render_template(
        'pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja',
        historico=historico,
        <x>=<x>,
        <x>_seq=<x>_seq,
    )
```

### 4.5 JSON de alterações (`campo_alterado='multiplos'`)

**Padrão:** lista de dicts `[{campo, antes, depois}]`.

**Quando usar:**
- **`multiplos`** — quando altera 2+ campos (criar, editar, concluir, reabrir, estornar)
- **1 campo** (`ativo`, `status`) — quando altera só 1 (inativar, reativar, quitar)

**Formato do `valor_novo`:**
```json
[
    {"campo": "Status", "antes": "pendente", "depois": "concluido"},
    {"campo": "Data Finalização", "antes": "(vazio)", "depois": "04/10/2026 15:46:23"},
    {"campo": "Motivo Conclusão", "antes": "(vazio)", "depois": "Finalizei"}
]
```

**Quando é `criada` (sem `antes`):**
```json
[
    {"campo": "Título", "depois": "Teste"},
    {"campo": "Descrição", "depois": "Descrição teste"},
    {"campo": "Categoria", "depois": "Trabalho"}
]
```

---

## 5. FRONTEND — PADRÕES

### 5.1 Classe `<X>Form` (core, compartilhada)

- **`mode: 'create'`** ou **`mode: 'edit'`**
- **`setData(data)`** — popula no edit
- **`getData()`** — serializa pro POST
- **`submit(url)`** — **SEMPRE JSON** + validações client-side
- **`reset()`** — limpa no create

### 5.2 Submits — semântica

**insert/edit** → `fetch` + **JSON** (front valida + manda pra API)

**delete/concluir/reabrir/reativar** → **HTMX puro** (botão confirmar recebe `hx-post` dinâmico, backend devolve `<tbody>` + HX-Trigger)

### 5.3 Padrão de ação HTMX (1 arquivo por ação)

```javascript
// acoes_e_modais/pasta_<acao>/<acao>_<x>.js
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

        // Fecha se sucesso
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

### 5.4 Orquestrador `<modulo>.js`

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

### 5.5 Auditoria modal (accordion)

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
                // Abre o 1º registro por padrão
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

## 6. TEMPLATES — PADRÕES

### 6.1 Estrutura da tabela (3 camadas de partial)

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
<tr data-id="{{ <x>.sequencia }}" id="linha-<x>-{{ <x>.sequencia }}">
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
            {% if <x>.status != 'concluido' %}
                <!-- CONCLUIR -->
                <button type="button" class="btn-acao check btn-concluir"
                        data-sequencia="{{ <x>.sequencia }}"
                        data-titulo="{{ <x>.titulo }}" title="Concluir">
                    <i class="bi bi-check-lg"></i>
                </button>

                <!-- EDITAR -->
                <button type="button" class="btn-acao edit"
                        hx-get="{{ url_for('<modulo>.edit_<x>.editar_modal', sequencia=<x>.sequencia) }}"
                        hx-target="#modal-editar-container"
                        hx-swap="innerHTML" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>

                <!-- EXCLUIR -->
                <button type="button" class="btn-acao delete btn-excluir"
                        data-sequencia="{{ <x>.sequencia }}"
                        data-titulo="{{ <x>.titulo }}" title="Inativar">
                    <i class="bi bi-trash"></i>
                </button>
            {% else %}
                <!-- REABRIR -->
                <button type="button" class="btn-acao undo btn-reabrir"
                        data-sequencia="{{ <x>.sequencia }}"
                        data-titulo="{{ <x>.titulo }}" title="Reabrir">
                    <i class="bi bi-arrow-return-left"></i>
                </button>
            {% endif %}
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

### 6.2 Modal de auditoria (accordion)

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
                                {% elif item.acao == 'concluida' %}✅ Concluída
                                {% elif item.acao == 'reaberta' %}↩️ Reaberta
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

---

## 7. CSS COMPARTILHADO

### 7.1 `components/modal_auditoria.css` (accordion)

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
.audit-badge-concluida { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.audit-badge-reaberta { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.audit-entry-body { max-height: 0; overflow: hidden; transition: max-height 0.25s ease; }
.audit-entry.open .audit-entry-body { max-height: 2000px; border-top: 1px solid var(--border-sutil); }

.audit-field { padding: 8px 12px; background: var(--bg-principal); border-radius: 6px; }
.audit-old { color: #f87171; text-decoration: line-through; background: rgba(248, 113, 113, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-new { color: #4ade80; font-weight: 600; background: rgba(74, 222, 128, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-arrow { color: var(--texto-discreto); margin: 0 8px; }
```

---

## 8. ARQUIVOS DE BUILD — `combina.py`

**Template por módulo (`scripts/combine_static_<modulo>.py`):**

```python
JS_FILES = [
    'static/js/modules/pasta_<modulo>/core/<X>Form.js',
    'static/js/modules/pasta_<modulo>/components/totalizadores.js',
    'static/js/modules/pasta_<modulo>/components/botoes_filtros.js',
    'static/js/modules/pasta_<modulo>/components/ordenacao.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-nova.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-editar.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_excluir/excluir_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_concluir/concluir_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_detalhes/detalhes_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_reabrir/reabrir_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_reativar/reativar_<x>.js',
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
    # específicos do módulo (se houver)
]
```

⚠️ **NUNCA misturar CSS no `JS_FILES` nem JS no `CSS_FILES`** — o concat vai quebrar tudo.

---

## 9. ARMADILHAS CONHECIDAS

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `dict(row)` no `listar_formatado` | `object is not iterable` | Colunas explícitas + `dict(zip(colunas, row))` |
| Auditoria com `sequencia` (não `id`) | Modal abre vazio | View traduz `sequencia → id`, auditoria usa `id` |
| `campo_alterado='todos'` | JSON não é parseado | Usar `'multiplos'` |
| `converter_valor_br` sempre remove `.` | `1009.9` → `10099` | Check `if ',' in valor` |
| `setTimeout(50)` pra sync HTMX | Quebra em prod (200ms latência) | `htmx:afterSwap` |
| CSS no `JS_FILES` | `Uncaught SyntaxError` | Separar JS e CSS |
| `HX-Trigger` em resposta 4xx | HTMX ignora header | Sempre `200` |
| `session['user_id']` ausente | `KeyError` | `session.get('user_id')` |
| Categoria mostra ID | `19` em vez de `Trabalho` | Buscar `nome` no service antes |
| Data `2026-10-04` | Data ISO crua | Helper `_fmt_data_br` / `_fmt_data_hora_br` |
| `modal.onclick` sempre | Clicar dentro fecha | `event.stopPropagation()` no box |
| Atualizar `_atualizar_filhas` sem `id` | UPDATE errado em parcelada | `WHERE id = %s` (não `sequencia`) |

---

## 10. CHECKLIST — CRIAR MÓDULO NOVO

### Backend
- [ ] Criar `rotas/pasta_<modulo>/__init__.py` (blueprint pai)
- [ ] Criar `<modulo>.py` (view + `_buscar_<x>_com_filtros` + `_render_tbody`)
- [ ] Criar `queries.py`, `filters.py`, `formatters.py`, `services/`
- [ ] Criar `crud/pasta_insert/` (JSON + auditoria)
- [ ] Criar `crud/pasta_edit/` (JSON + diff + auditoria)
- [ ] Criar `crud/pasta_delete/` (HTML + HX-Trigger + auditoria)
- [ ] Criar `crud/pasta_<acao1>/`, `pasta_<acao2>/` (ex: concluir, reabrir)
- [ ] **Todos** os CRUDs: `_buscar_<x>_com_filtros` + `_render_tbody` duplicados (padrão)
- [ ] **Todas** as views: `logger.exception()`, `conexao.rollback()`, `conexao.close()`
- [ ] **Todas** as auditorias: `conexao=conexao`, `tarefa_id=id_interno`, JSON `[{campo, antes, depois}]`

### Auditoria
- [ ] Criar `rotas/auditoria_geral/pasta_<modulo>/tabela.py`
- [ ] Criar `rotas/auditoria_geral/pasta_<modulo>/services_auditoria.py` (com `conexao=None` + colunas explícitas + zip)
- [ ] Criar `rotas/auditoria_geral/pasta_<modulo>/logica_auditoria.py` (traduz sequência → id)
- [ ] Registrar no `bp_auditoria` (em `rotas/auditoria_geral/__init__.py`)

### Frontend
- [ ] Criar `core/<X>Form.js` (setData, getData, submit JSON, reset)
- [ ] Criar `components/totalizadores.js`, `botoes_filtros.js`, `ordenacao.js`
- [ ] Criar `modals/<x>-nova.js`, `<x>-editar.js`
- [ ] Criar `acoes_e_modais/pasta_excluir/`, `pasta_concluir/`, `pasta_reativar/`, `pasta_detalhes/`, `pasta_auditoria/`
- [ ] Criar `<modulo>.js` (só init + recarregarTabela)
- [ ] **Nenhum** `setTimeout` fixo pra sync HTMX
- [ ] **Nenhum** `onclick` inline (só `data-*`)

### Templates
- [ ] `tela_<modulo>.html.jinja`
- [ ] `_tabela_<modulo>.html.jinja`
- [ ] `partials/_tbody_<modulo>.html.jinja`
- [ ] `partials/_linha_<modulo>.html.jinja`
- [ ] `partials/form_<x>.html.jinja`
- [ ] `modais/modal_nova_<x>.html.jinja`, `modal_editar_<x>.html.jinja`
- [ ] `modais/excluir_<x>.html`, `concluir_<x>.html`, `reabrir_<x>.html`, `reativar_<x>.html`
- [ ] `pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja`
- [ ] Containers na tela: `<div id="modal-nova-container">`, `#modal-editar-container`, `#modal-auditoria-container`

### CSS
- [ ] **Reaproveitar** `components/` (não duplicar)
- [ ] Adicionar específicos do módulo em `modules/pasta_<modulo>/` se necessário

### Build
- [ ] Ajustar `scripts/combine_static_<modulo>.py` (JS_FILES + CSS_FILES)
- [ ] **Conferir** que CSS não tá em JS e vice-versa
- [ ] Rodar `python scripts/combine_static_<modulo>.py`
- [ ] **Zero** `⚠️ não encontrado`

### Antes de subir
- [ ] Criar simples funciona
- [ ] Editar (diff correto)
- [ ] Excluir/concluir/reabrir/reativar
- [ ] Detalhes
- [ ] Auditoria abre em modal (accordion)
- [ ] Toast verde em todas ações
- [ ] Filtros preservam
- [ ] Console sem erro
- [ ] **Testar em prod** (latência 200ms)

---

## 11. COMANDOS

```bash
# Build local
python scripts/combine_static_financas.py
python scripts/combine_static_tarefas.py

# Rodar Flask
python app.py

# Commit
git add .
git commit -m "feat: <modulo> padrao 2099"
git push origin main

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

## 12. REFERÊNCIAS

- HTMX: https://htmx.org/docs/
- HTMX events: https://htmx.org/events/
- OOB swaps: https://htmx.org/attributes/hx-swap-oob/
- Flask blueprints: https://flask.palletsprojects.com/en/latest/blueprints/

---

## FIM DO PLAYBOOK 2099

> **Este documento é a fonte da verdade do padrão VHORGANIZA.**
> Ao criar novo módulo: siga seção 10 (checklist).
> Ao encontrar bug: adicione em seção 9 (armadilhas).
> Ao mudar padrão: atualize as seções correspondentes.