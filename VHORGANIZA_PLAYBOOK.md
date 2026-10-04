# VHORGANIZA — PLAYBOOK TÉCNICO
## Padrão de desenvolvimento dos módulos CRUD (Flask + HTMX + JS modular)

**Versão:** 1.0
**Data:** Outubro/2026
**Projeto:** VHORGANIZA
**Módulo referência:** Finanças (100% funcional)
**Próximos módulos:** Tarefas e demais CRUDs do sistema

---

## 1. VISÃO GERAL

### 1.1 Stack
- **Backend:** Flask + PostgreSQL
- **Frontend:** HTMX (navegação/tabela) + JS modular vanilla (forms/modais)
- **Templates:** Jinja2
- **Build JS:** `python combina.py` (concatena/minifica módulos em `*.min.js`)
- **Deploy:** Git → VPS (Contabo/Alemanha) → `systemctl restart gestao_financeira`
- **Latência real prod:** ~200ms (Brasil ↔ Alemanha) — considerar em qualquer `setTimeout`

### 1.2 Princípios
1. Backend separado por camadas: rota → service → query
2. Frontend sem framework: JS modular com IIFE + classes
3. HTMX puro: troca de `<tbody>`, sem reload de página
4. Sem `setTimeout` para sincronizar com rede: usar eventos (`htmx:afterSwap`)
5. Respostas sempre `200`: HTMX ignora `HX-Trigger` em 4xx/5xx
6. JSON em ambos insert/edit: `request.json` no backend, `Content-Type: application/json` no front

---

## 2. ESTRUTURA DE PASTAS (padrão por módulo)

```
rotas/pasta_<MODULO>/
├── __init__.py                 # Blueprint principal + register_blueprint dos CRUDs
├── <modulo>.py                 # Rotas principais (listagem, detalhes, filtros)
├── queries.py                  # SQL puro (classe <Modulo>Queries)
├── filters.py                  # Filtros (session, query string)
├── formatters.py               # Serialização / formatação BR
├── services/
│   └── services_<modulo>.py    # Lógica de negócio principal
└── crud/
    ├── pasta_insert/
    │   ├── __init__.py         # bp_insert + add_url_rule
    │   ├── insert_<x>.py       # view_funcs (GET modal + POST salvar)
    │   ├── services.py         # <X>Service (INSERT)
    │   └── validacoes.py       # validar + converter_valor_br
    ├── pasta_edit/
    │   ├── __init__.py
    │   ├── edit_<x>.py
    │   ├── services.py
    │   └── validacoes.py
    ├── pasta_delete/
    ├── pasta_quitar/
    ├── pasta_estornar/
    └── pasta_reativar/

templates/pasta_<MODULO>/
├── tela_<modulo>.html
├── _tabela_<modulo>.html              # Partial <table> + <tbody> (hx-target)
├── modais/
│   ├── modal_nova_<x>.html.jinja
│   └── modal_editar_<x>.html.jinja
└── partials/
    └── form_<x>.html.jinja             # Form compartilhado novo/edit

static/js/modules/pasta_<MODULO>/
├── core/
│   ├── formatadores.js                 # window.Formatadores<Modulo>
│   └── <X>Form.js                      # Classe compartilhada (create/edit)
├── components/
│   ├── totalizadores.js
│   └── botoes_outros_filtros.js
├── modals/
│   ├── <x>-nova.js
│   └── <x>-editar.js
└── <modulo>.js                         # Orquestrador (main)
```

---

## 3. BACKEND — PADRÕES OBRIGATÓRIOS

### 3.1 Blueprint principal (`__init__.py`)

```python
from flask import Blueprint

bp_<modulo> = Blueprint('<modulo>', __name__)

# Rotas principais
from .<modulo> import ini_<modulo>, detalhes, limpar_filtros
bp_<modulo>.add_url_rule('/', view_func=ini_<modulo>, methods=['GET', 'POST'])
bp_<modulo>.add_url_rule('/detalhes/<int:id>', view_func=detalhes)
bp_<modulo>.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

# CRUDs (cada um com seu prefixo)
from .crud.pasta_insert import bp_insert
from .crud.pasta_edit import bp_edit
from .crud.pasta_delete import bp_delete
# ... outros

bp_<modulo>.register_blueprint(bp_insert, url_prefix='/nova_<x>')
bp_<modulo>.register_blueprint(bp_edit, url_prefix='/edit_<x>')
bp_<modulo>.register_blueprint(bp_delete, url_prefix='/excluir_<x>')
```

### 3.2 Blueprint de CRUD (`crud/pasta_insert/__init__.py`)

```python
from flask import Blueprint

bp_insert = Blueprint('insert_<x>', __name__)

from .insert_<x> import <x>_modal, salvar_<x>

bp_insert.add_url_rule('/modal', view_func=<x>_modal, methods=['GET'])
bp_insert.add_url_rule('/salvar', view_func=salvar_<x>, methods=['POST'])
```

### 3.3 Rota (view_func) — PADRÃO

```python
import logging
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from .services import <X>Service
from .validacoes import validar_dados_insercao, converter_valor_br

logger = logging.getLogger(__name__)

@login_required
def salvar_<x>():
    user_id = session.get('user_id')
    conexao, cursor = ini_conexao()

    try:
        payload = request.json or {}   # SEMPRE request.json

        dados = {
            'campo1': payload.get('campo1'),
            'valor': converter_valor_br(payload.get('valor')),
            'descricao': (payload.get('descricao') or '').strip(),
        }

        # Array de itens (ex: parcelas) — vem como LISTA do front
        itens = []
        for p in (payload.get('itens') or []):
            itens.append({
                'numero': int(p.get('numero') or 0),
                'valor': converter_valor_br(p.get('valor')),
                'vencimento': p.get('vencimento'),
            })
        if itens:
            dados['itens'] = itens

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400

        sucesso, resultado = <X>Service.criar(cursor, user_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400

        conexao.commit()
        <X>Service.registrar_auditoria(resultado['id'], dados['descricao'])

        return jsonify({
            'success': True,
            'message': 'Cadastrado com sucesso!',
            'id': resultado['id']
        }), 201

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar user_id={user_id}")
        return jsonify({
            'success': False,
            'error': 'Erro interno no servidor.',
            'details': str(e)
        }), 500
```

### 3.4 converter_valor_br — PADRÃO ÚNICO (copiar em todo módulo)

```python
def converter_valor_br(valor):
    """
    Converte formato brasileiro '1.234,56' OU entrada genérica (float/int) para float.
    Retorna 0.0 em caso de falha.
    REGRA: só remove ponto se tiver vírgula (formato BR).
    """
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        valor_str = str(valor).replace('R$', '').strip()
        if ',' in valor_str:
            valor_str = valor_str.replace('.', '').replace(',', '.')
        return float(valor_str)
    except (ValueError, TypeError):
        return 0.0
```

**Por que isso importa:** se `converter_valor_br` sempre fizer `.replace('.', '')`, um float `1009.9` vira `10099.0` (bug clássico). O check `if ',' in valor_str` evita isso.

---

## 4. FRONTEND — PADRÕES OBRIGATÓRIOS

### 4.1 Classe <X>Form (compartilhada entre create/edit)

Arquivo: `static/js/modules/pasta_<MODULO>/core/<X>Form.js`

```javascript
(function() {
    'use strict';

    function <X>Form(formEl, options) {
        if (!formEl) throw new Error('<X>Form: formEl obrigatório');

        this.form = formEl;
        this.options = options || {};
        this.mode = this.options.mode || 'create';
        this.onSubmitSuccess = this.options.onSubmitSuccess || null;
        this.onSubmitError = this.options.onSubmitError || null;

        var modal = formEl.closest('.fin-modal-overlay') || formEl.closest('body');

        this.el = {
            campo1: formEl.querySelector('.js-campo1'),
            valor:  formEl.querySelector('.js-valor'),
        };

        this._bind();
    }

    <X>Form.prototype._bind = function() {
        // listeners via this.el.*
    };

    <X>Form.prototype.setData = function(data) { /* modo edit */ };

    <X>Form.prototype.getData = function() {
        return { /* payload JSON */ };
    };

    <X>Form.prototype.reset = function() { /* modo create */ };

    <X>Form.prototype.submit = function(url) {
        var self = this;
        var data = this.getData();

        if (!data.campo1) {
            if (window.Notificacao) window.Notificacao.aviso('Campo obrigatório');
            return Promise.reject(new Error('campo1 vazio'));
        }

        var body = JSON.stringify(data);
        var headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        };

        return fetch(url, { method: 'POST', headers: headers, body: body })
            .then(function(r) { return r.json().then(function(j) { return { ok: r.ok, data: j }; }); })
            .then(function(res) {
                if (!res.ok || res.data.success === false) {
                    var msg = (res.data.errors && res.data.errors[0] && res.data.errors[0].mensagem)
                              || res.data.error || 'Erro ao salvar.';
                    if (self.onSubmitError) self.onSubmitError(msg);
                    else if (window.Notificacao) window.Notificacao.erro(msg);
                    throw new Error(msg);
                }
                if (self.onSubmitSuccess) self.onSubmitSuccess(res.data);
                return res.data;
            });
    };

    window.<X>Form = <X>Form;
    console.log('<X>Form carregado!');
})();
```

### 4.2 Modal Nova — Orquestrador

```javascript
(function() {
    'use strict';

    var formInstance = null;

    function instanciar() {
        var formEl = document.getElementById('formNova<X>');
        if (!formEl) return null;
        if (formInstance) return formInstance;

        formInstance = new window.<X>Form(formEl, {
            mode: 'create',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message);

                fecharModalNova<X>();

                if (window.recarregarTabela<Modulo>) {
                    window.recarregarTabela<Modulo>();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/<modulo>', '#tabela-container');
                }
            }
        });
        return formInstance;
    }

    function abrirModalNova<X>() { /* ... */ }
    function fecharModalNova<X>() { /* ... */ }
    function salvarNova<X>() {
        var f = instanciar();
        if (!f) return;
        f.submit('/<modulo>/nova_<x>/salvar')
         .catch(function() {})
         .finally(function() { /* restaura botão */ });
    }

    window.abrirModalNova<X> = abrirModalNova<X>;
    window.fecharModalNova<X> = fecharModalNova<X>;
    window.salvarNova<X> = salvarNova<X>;

    console.log('MODAL NOVA <X> carregado!');
})();
```

### 4.3 Modal Editar — Orquestrador (padrão HTMX injeta + JS popula)

```javascript
(function() {
    'use strict';

    var idAtual = null;
    var formInstance = null;

    function instanciar(formEl) {
        if (!formEl) return null;
        if (formInstance && formInstance.form === formEl) return formInstance;

        formInstance = new window.<X>Form(formEl, {
            mode: 'edit',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message);
                fecharModalEditar<X>();

                if (window.recarregarTabela<Modulo>) {
                    window.recarregarTabela<Modulo>();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/<modulo>', '#tabela-container');
                }
            }
        });
        return formInstance;
    }

    function abrirModalEditar<X>(id) {
        idAtual = id;
        var modal = document.getElementById('modalEditar<X>');
        var formEl = document.getElementById('formEditar<X>');
        if (!modal || !formEl) return;

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        fetch('/<modulo>/edit_<x>/dados/' + id, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(r) { return r.json(); })
        .then(function(resposta) {
            var data = resposta.data || resposta;
            var f = instanciar(formEl);
            if (f) f.setData(data);
        })
        .catch(function(error) {
            console.error('Erro:', error);
        });
    }

    function fecharModalEditar<X>() { /* ... */ }
    function salvarEditar<X>() { /* f.submit('/<modulo>/edit_<x>/' + idAtual) */ }

    // HTMX injeta o modal -> dispara abrir()
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;
        if (target.id !== 'modal-editar-container' && !target.closest('#modal-editar-container')) return;

        var formEl = document.getElementById('formEditar<X>');
        if (!formEl) return;
        var id = formEl.dataset.<x>Id;
        if (!id || id === 'None') return;

        console.log('HTMX injetou modal, populando via /dados/' + id);
        abrirModalEditar<X>(id);
    });

    window.abrirModalEditar<X> = abrirModalEditar<X>;
    window.fecharModalEditar<X> = fecharModalEditar<X>;
    window.salvarEditar<X> = salvarEditar<X>;

    console.log('MODAL EDITAR <X> carregado!');
})();
```

### 4.4 Componentes — SINCRONIZAÇÃO COM HTMX (CRÍTICO)

NUNCA usar `setTimeout(50)` para sincronizar com resposta HTMX. Em produção (200ms de latência), o timeout dispara antes da resposta chegar.

SEMPRE usar `htmx:afterSwap`:

```javascript
// CORRETO
document.body.addEventListener('htmx:afterSwap', function(evt) {
    var target = evt.detail.target;
    if (!target) return;

    if (target.id === 'tabela-container' ||
        target.id === 'tbody-<x>' ||
        target.closest('#tabela-container')) {
        calcularTotais<Modulo>();
        atualizarBotoesTransacao();
    }
});

// ERRADO
document.body.addEventListener('htmx:afterRequest', function(evt) {
    setTimeout(calcularTotais, 50); // race condition em produção
});
```

Eventos HTMX corretos:

| Evento | Quando usar |
|--------|-------------|
| `htmx:afterSwap` | DOM já foi trocado (padrão) |
| `htmx:afterRequest` | Só para saber se request terminou (não confiar no DOM) |
| `htmx:afterSettle` | Raramente — só se precisar esperar animações |
| `htmx:beforeSwap` | Para inspecionar resposta antes de aplicar |

---

## 5. PADRÃO DE RESPOSTA HTMX (Out-Of-Band)

Toda resposta HTMX que atualiza a tabela também deve atualizar os inputs de filtro e totalizadores via OOB swaps:

```python
def _renderizar_htmx(transacoes, data_inicio, data_fim, filtros, totais):
    # 1. Fragmento principal (tabela)
    tabela_html = render_template('pasta_<modulo>/_tabela_<modulo>.html', ...)

    # 2. Fragmentos OOB (substituem elementos pelo id)
    oob_html = f"""
        <input type="date" id="data_inicio_input" value="{data_inicio}" hx-swap-oob="outerHTML:#data_inicio_input">
        <input type="date" id="data_fim_input" value="{data_fim}" hx-swap-oob="outerHTML:#data_fim_input">
        <span id="totalReceitas" hx-swap-oob="innerHTML">{totais['receitas']}</span>
        <span id="totalDespesas" hx-swap-oob="innerHTML">{totais['despesas']}</span>
    """

    return tabela_html + oob_html
```

Tipos de `hx-swap-oob`:
- `outerHTML:#id` — substitui o elemento inteiro
- `innerHTML:#id` — substitui só o conteúdo interno

---

## 6. PADRÃO DE TABELA / TBODY

Template `_tabela_<modulo>.html`:

```html
<table class="custom-table" id="tabela-container">
    <thead>...</thead>
    <tbody id="tbody-<modulo>">
        {% for t in transacoes %}
            <tr data-id="{{ t.id }}">
                <button hx-get="/<modulo>/edit_<x>/{{ t.sequencia }}"
                        hx-target="#modal-editar-container"
                        hx-swap="innerHTML">
                    Editar
                </button>
            </tr>
        {% endfor %}
    </tbody>
</table>
```

Regra: o `id` do `<tbody>` bate exatamente com o `hx-target` que o JS/HTMX usa pra recarregar.

---

## 7. ARMADILHAS CONHECIDAS (aprendidas na dor)

### 7.1 Backend

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| converter_valor_br sempre remove ponto | 1009.9 vira 10099.0 | Check `if ',' in valor_str` antes de remover ponto |
| str(valor_float) no backend | JSON manda float, backend converte errado | `if isinstance(valor, (int,float)): return float(valor)` |
| traceback.print_exc() | Log sem contexto em prod | `logger.exception(f"... user_id={user_id}")` |
| request.form vs request.json misturados | Insert FormData, edit JSON | SEMPRE `request.json` |

### 7.2 Frontend

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| setTimeout(50) para sync HTMX | Funciona local, quebra em prod | `htmx:afterSwap` sempre |
| Máscara de moeda em backspace | 1.000,90 -> apaga 0 -> 100,09 | Só rodar máscara em `inputType === 'insertText'` |
| location.reload() no submit | Pisca a tela, perde scroll | `htmx.ajax('GET', '/<modulo>', '#tabela-container')` |
| Escopo de querySelector global | Um modal afeta o outro | `formEl.querySelector('.js-*')` sempre |
| IDs duplicados no DOM | Bug de "primeiro item" | Nunca usar ID — só classes `.js-*` |

### 7.3 HTMX

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| HX-Trigger em resposta 4xx | HTMX ignora header | Retornar sempre 200 + JSON com success: false |
| afterSettle com tbody | Evento não dispara | Usar afterSwap |
| hx-target errado | Substitui o elemento errado | Conferir se id do tbody bate |
| Botão clonado sem hx-post | Não dispara | Setar hx-post antes de clonar, ou reinit HTMX |

---

## 8. CHECKLIST — REPLICAR EM NOVO MÓDULO

### Backend
- [ ] Criar `rotas/pasta_<modulo>/__init__.py` com blueprint principal
- [ ] Criar `<modulo>.py` (rotas listagem/detalhes/filtros)
- [ ] Criar `queries.py`, `filters.py`, `formatters.py`, `services/`
- [ ] Criar `crud/pasta_insert/` com:
  - [ ] `__init__.py` (bp_insert + add_url_rule)
  - [ ] `insert_<x>.py` (GET modal + POST salvar com `request.json`)
  - [ ] `services.py`
  - [ ] `validacoes.py` (com converter_valor_br correto)
- [ ] Repetir para `pasta_edit/`, `pasta_delete/`, etc.
- [ ] Registrar todos os bp_* no `__init__.py` principal
- [ ] Usar `logger.exception()` em todos os except
- [ ] JSON em todos os POSTs (`request.json`)

### Frontend
- [ ] Criar `core/formatadores.js` (window.Formatadores<Modulo>)
- [ ] Criar `core/<X>Form.js` (classe compartilhada)
- [ ] Criar `components/` (totalizadores, filtros visuais)
- [ ] Criar `modals/<x>-nova.js` e `<x>-editar.js`
- [ ] Criar `<modulo>.js` (orquestrador)
- [ ] ZERO setTimeout para sync com HTMX — usar htmx:afterSwap
- [ ] ZERO IDs globais — só classes `.js-*`

### Templates
- [ ] `tela_<modulo>.html` (layout)
- [ ] `_tabela_<modulo>.html` (partial com `<tbody id="tbody-<modulo>">`)
- [ ] `modais/modal_nova_<x>.html.jinja`
- [ ] `modais/modal_editar_<x>.html.jinja`
- [ ] `partials/form_<x>.html.jinja` (compartilhado)
- [ ] OOB swaps no retorno HTMX

### Antes de subir
- [ ] `python combina.py` roda sem erro
- [ ] Flask sobe sem erro
- [ ] Insert simples funciona (valor com 4+ dígitos)
- [ ] Insert parcelado funciona
- [ ] Edit simples funciona
- [ ] Edit parcelado funciona
- [ ] Delete/quitar/estornar/reativar funcionam
- [ ] Filtros preservam estado após editar/criar
- [ ] Totalizador atualiza após cada operação
- [ ] Console do browser sem erro vermelho

---

## 9. ROTEIRO PARA O MÓDULO TAREFAS

### 9.1 Estrutura inicial

```
rotas/pasta_tarefas/
├── __init__.py
├── tarefas.py
├── queries.py
├── filters.py
├── formatters.py
├── services/services_tarefas.py
└── crud/
    ├── pasta_insert/
    ├── pasta_edit/
    ├── pasta_delete/
    ├── pasta_concluir/     # equivale a "quitar"
    └── pasta_reabrir/      # equivale a "reativar"

templates/pasta_tarefas/
├── tela_tarefas.html
├── _tabela_tarefas.html
├── modais/
│   ├── modal_nova_tarefa.html.jinja
│   └── modal_editar_tarefa.html.jinja
└── partials/
    └── form_tarefa.html.jinja

static/js/modules/pasta_tarefas/
├── core/
│   ├── formatadores.js
│   └── TarefaForm.js
├── components/
│   ├── totalizadores.js
│   └── botoes_filtros.js
├── modals/
│   ├── tarefa-nova.js
│   └── tarefa-editar.js
└── tarefas.js
```

### 9.2 Checklist Tarefas
- [ ] Copiar converter_valor_br (mesmo que não use valor, mantém padrão)
- [ ] Reusar TransacaoForm patterns (adaptar pra TarefaForm)
- [ ] submit() sempre JSON
- [ ] htmx:afterSwap (zero setTimeout)
- [ ] OOB swaps para filtros + contadores
- [ ] logger.exception() em todos os except

### 9.3 O que NÃO copiar
- Lógica específica de parcelamento (PAI/FILHAS)
- Cálculo de valores (paraFloat, mascaraMoeda) — só se tarefa tiver valor
- _datasEditadasManualmente — só se tarefa tiver recorrência de datas

---

## 10. COMANDOS ÚTEIS

### Build + Deploy

```bash
# Local
python combina.py

# Commit
git add .
git commit -m "feat: <modulo> no padrão HTMX puro"
git push origin main

# Servidor
ssh usuario@vhorganiza.com.br
cd /var/www/vhorganiza
git fetch origin
git reset --hard origin/main
git clean -fd
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
sudo systemctl restart gestao_financeira
```

### Debug em produção

```bash
journalctl -u gestao_financeira -n 50
```

### Console browser (F12)

```javascript
// Ver listeners de um input
getEventListeners(document.querySelector('#formEditarX .js-campo'))

// Monitorar htmx
document.body.addEventListener('htmx:afterSwap', function(e) {
    console.log('swapped:', e.detail.target.id);
});
```

---

## 11. REFERÊNCIAS

- HTMX: https://htmx.org/docs/
- HTMX events: https://htmx.org/events/
- OOB swaps: https://htmx.org/attributes/hx-swap-oob/
- Flask blueprints: https://flask.palletsprojects.com/en/latest/blueprints/

---

## FIM DO PLAYBOOK

> Este documento é a fonte da verdade do padrão VHORGANIZA.
> Ao criar novo módulo, siga seção 8 (checklist) e seção 9 (se for Tarefas).
> Ao encontrar bug novo, adicione em seção 7 (armadilhas conhecidas).