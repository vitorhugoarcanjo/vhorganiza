# 14 — Categorias Inline (Feature)

## 14.1 Objetivo

Permitir criar categorias **sem sair do fluxo** de nova tarefa/finança.

**Problema hoje:**
- Pra criar uma categoria, o usuário precisa **sair** do modal de tarefa/finança
- Ir pra tela de categorias
- Criar
- Voltar pro modal
- Reabrir o select

**Solução:**
- Botão `+` no lado do `<select>` de categoria
- Abre **mini-modal empilhado** pra criar
- Cria no backend
- Adiciona `<option>` no select **automaticamente** e já seleciona

## 14.2 UX Final

**Modal Nova Tarefa:**
```
┌─────────────────────────────────────────┐
│  Nova Tarefa                       [X]  │
├─────────────────────────────────────────┤
│  Título:    [___________________]       │
│  Descrição: [___________________]       │
│                                         │
│  Categoria: [Trabalho ▼] [+]           │ ← 🆕 BOTÃO +
│  ...                                    │
└─────────────────────────────────────────┘
```

**Ao clicar no `+`:**
```
┌─────────────────────────────────────────┐
│  Nova Tarefa (fundo)                    │
│                                         │
│    ┌─────────────────────────┐          │
│    │ Nova Categoria     [X]  │ ← 🆕    │
│    ├─────────────────────────┤          │
│    │ Nome: [__________]      │          │
│    │ Cor:  [#2563eb]         │          │
│    │                         │          │
│    │ [Cancelar] [Criar]      │          │
│    └─────────────────────────┘          │
└─────────────────────────────────────────┘
```

**Ao criar:**
- Mini-modal fecha
- `<option>` nova aparece no select **já selecionada**
- Toast verde: `Categoria "Trabalho" criada!`

## 14.3 Backend

### Rota nova

```
POST /categorias/criar-inline
Body: { modulo: "tarefas" | "financas" | "orcamentos", nome: "...", cor: "#2563eb" }
Response: { success: true, id: 42, nome: "Trabalho", cor: "#2563eb" }
```

### View

```python
# rotas/pasta_categorias/logica_criar_inline.py
from flask import request, jsonify, session
import logging

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

logger = logging.getLogger(__name__)


@login_required
def criar_categoria_inline():
    """Cria categoria inline (via modal de outra feature)."""
    user_id = session['user_id']
    conexao = None

    try:
        payload = request.get_json() or {}

        modulo = payload.get('modulo') or 'financas'
        nome   = (payload.get('nome') or '').strip()
        cor    = (payload.get('cor') or '#2563eb').strip()

        # Valida
        if not nome:
            return jsonify({
                'success': False,
                'message': 'Nome é obrigatório',
                'type': 'erro'
            }), 400

        # Mapeia módulo → tabela
        mapa = {
            'financas':   'categorias_financas',
            'tarefas':    'categorias_tarefas',
            'orcamentos': 'categorias_orcamentos',  # futuro
        }
        tabela = mapa.get(modulo)
        if not tabela:
            return jsonify({
                'success': False,
                'message': 'Módulo inválido',
                'type': 'erro'
            }), 400

        # INSERT
        conexao, cursor = ini_conexao()

        # Verifica duplicada
        cursor.execute(
            f"SELECT id FROM {tabela} WHERE user_id = %s AND LOWER(nome) = LOWER(%s)",
            (user_id, nome)
        )
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': f'Já existe uma categoria "{nome}"',
                'type': 'erro'
            }), 400

        cursor.execute(
            f"INSERT INTO {tabela} (user_id, nome, cor) VALUES (%s, %s, %s) RETURNING id",
            (user_id, nome, cor)
        )
        novo_id = cursor.fetchone()[0]

        conexao.commit()

        return jsonify({
            'success': True,
            'id': novo_id,
            'nome': nome,
            'cor': cor,
        }), 201

    except Exception as e:
        if conexao:
            conexao.rollback()
        logger.exception(f"Erro ao criar categoria inline user_id={user_id}")
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}',
            'type': 'erro'
        }), 500
```

### Registro no `__init__.py` do módulo categorias

```python
from .logica_criar_inline import criar_categoria_inline

bp_categorias.add_url_rule(
    '/criar-inline',
    view_func=criar_categoria_inline,
    methods=['POST']
)
```

## 14.4 Frontend

### Template — Botão + no lado do select

**No `form_tarefa.html.jinja` (ou form_transacao.html.jinja):**

```jinja
<div class="form-group">
    <label><i class="bi bi-tags"></i> Categoria</label>
    <div class="categoria-wrapper">
        <select name="categoria_id" class="form-select js-categoria">
            <option value="">⚠️ Sem categoria</option>
            {% for cat in categorias %}
                <option value="{{ cat[0] }}"
                        data-cor="{{ cat[2] or '#6c757d' }}">
                    {{ cat[1] }}
                </option>
            {% endfor %}
        </select>
        <button type="button"
                class="btn-add-categoria"
                onclick="abrirModalNovaCategoria('tarefas')"
                title="Nova categoria">
            <i class="bi bi-plus-lg"></i>
        </button>
    </div>
</div>
```

### CSS — `.categoria-wrapper`

```css
.categoria-wrapper {
    display: flex;
    gap: 6px;
    align-items: center;
}

.categoria-wrapper .form-select {
    flex: 1;
}

.btn-add-categoria {
    width: 40px;
    height: 40px;
    border: 2px solid var(--border-sutil);
    border-radius: 8px;
    background: transparent;
    color: var(--cor-ativa);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.btn-add-categoria:hover {
    border-color: var(--cor-ativa);
    background: rgba(37, 99, 235, 0.08);
}
```

### Mini-modal (`modal_nova_categoria_inline.html.jinja`)

```jinja
<!-- templates/pasta_categorias/modais/modal_nova_categoria_inline.html.jinja -->
<div class="fin-modal-overlay" id="modalNovaCategoriaInline">
    <div class="fin-modal-box fin-modal-box-small">
        <div class="fin-modal-header">
            <h3><i class="bi bi-tag"></i> Nova Categoria</h3>
            <button class="fin-btn-close-modal"
                    onclick="fecharModalNovaCategoria()">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>

        <form id="formNovaCategoriaInline" class="fin-modal-form"
              onsubmit="event.preventDefault(); salvarNovaCategoriaInline();">
            <div class="fin-modal-body">
                <div class="form-group">
                    <label>Nome *</label>
                    <input type="text"
                           name="nome"
                           class="form-input js-cat-nome"
                           placeholder="Ex: Trabalho, Pessoal..."
                           maxlength="100">
                </div>
                <div class="form-group">
                    <label>Cor</label>
                    <input type="color"
                           name="cor"
                           class="form-input js-cat-cor"
                           value="#2563eb">
                </div>
            </div>

            <div class="footer-fixo-padrao">
                <div class="botoes-footer-padrao">
                    <button type="submit" class="btn-footer btn-footer-primary">
                        <i class="bi bi-check-lg"></i> CRIAR
                    </button>
                    <button type="button" class="btn-footer-cancelar"
                            onclick="fecharModalNovaCategoria()">
                        <i class="bi bi-x-circle"></i> CANCELAR
                    </button>
                </div>
                <h2>NOVA - CATEGORIA</h2>
            </div>
        </form>
    </div>
</div>
```

**CSS extra:**

```css
.fin-modal-box-small {
    height: auto;
    max-height: 60vh;
    width: 90%;
    max-width: 480px;
    border-radius: 12px;
    margin: auto;
}

.fin-modal-box-small .fin-modal-body {
    padding: 20px 24px;
}
```

### JS — `criar_categoria_inline.js`

**Local:** `static/js/components/criar_categoria_inline.js` (compartilhado)

```javascript
// static/js/components/criar_categoria_inline.js
// ==========================================================
// CRIAR CATEGORIA INLINE — modal empilhado
// ==========================================================

(function() {
    'use strict';

    var moduloAtivo = null;

    // ==========================================================
    // ABRIR
    // ==========================================================
    window.abrirModalNovaCategoria = function(modulo) {
        moduloAtivo = modulo || 'financas';

        var modal = document.getElementById('modalNovaCategoriaInline');
        if (!modal) return;

        // Limpa campos
        var nome = modal.querySelector('.js-cat-nome');
        var cor = modal.querySelector('.js-cat-cor');
        if (nome) nome.value = '';
        if (cor) cor.value = '#2563eb';

        // Limpa erros
        document.querySelectorAll('.campo-erro').forEach(function(el) {
            el.classList.remove('campo-erro');
        });
        document.querySelectorAll('.msg-erro-campo').forEach(function(el) {
            el.remove();
        });

        modal.classList.add('active');

        // Foco no campo
        setTimeout(function() {
            if (nome) nome.focus();
        }, 100);
    };

    // ==========================================================
    // FECHAR
    // ==========================================================
    window.fecharModalNovaCategoria = function() {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal) modal.classList.remove('active');
        moduloAtivo = null;
    };

    // ==========================================================
    // SALVAR
    // ==========================================================
    window.salvarNovaCategoriaInline = function() {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (!modal || !moduloAtivo) return;

        var nome = (modal.querySelector('.js-cat-nome') || {}).value || '';
        var cor = (modal.querySelector('.js-cat-cor') || {}).value || '#2563eb';
        nome = nome.trim();

        // Validação front
        if (!nome) {
            var nomeInput = modal.querySelector('.js-cat-nome');
            nomeInput.classList.add('campo-erro');
            var msg = document.createElement('span');
            msg.className = 'msg-erro-campo';
            msg.textContent = 'Nome é obrigatório';
            nomeInput.parentNode.appendChild(msg);
            return;
        }

        // Botão loading
        var btn = modal.querySelector('.btn-footer-primary');
        var textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = 'Criando...';

        fetch('/categorias/criar-inline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                modulo: moduloAtivo,
                nome: nome,
                cor: cor
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                // 🔥 Adiciona <option> ao select do modal de trás
                var selects = document.querySelectorAll('.js-categoria');
                selects.forEach(function(select) {
                    var option = new Option(data.nome, data.id, true, true);
                    option.setAttribute('data-cor', data.cor);
                    select.add(option);
                    select.value = data.id;  // Seleciona automaticamente
                });

                window.Notificacao.sucesso('Categoria "' + data.nome + '" criada!');
                fecharModalNovaCategoria();
            } else {
                window.Notificacao.erro(data.message || 'Erro ao criar');
            }
        })
        .catch(function(err) {
            console.error('❌ Erro:', err);
            window.Notificacao.erro('Erro ao criar categoria');
        })
        .finally(function() {
            btn.disabled = false;
            btn.innerHTML = textoOriginal;
        });
    };

    // ==========================================================
    // ESC / clique fora
    // ==========================================================
    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Escape') return;

        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal && modal.classList.contains('active')) {
            e.stopPropagation();
            fecharModalNovaCategoria();
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            fecharModalNovaCategoria();
        }
    });

    console.log('✅ Criar categoria inline carregado!');
})();
```

**Registrar no `combine_static_<modulo>.py`:**
```python
JS_FILES = [
    'static/js/components/botoes_filtros.js',
    'static/js/components/criar_categoria_inline.js',   # 🆕
    # ...
]
```

**Incluir no template da tela (ou no `base.html`):**
```jinja
{% include 'pasta_categorias/modais/modal_nova_categoria_inline.html.jinja' %}
```

## 14.5 Aplicar em cada módulo

### Finanças

- [ ] `form_transacao.html.jinja` — adicionar botão `+`
- [ ] `transacao-nova.js` — contexto `'financas'`
- [ ] `transacao-editar.js` — contexto `'financas'`

### Tarefas

- [ ] `form_tarefa.html.jinja` — adicionar botão `+`
- [ ] `tarefa-nova.js` — contexto `'tarefas'`
- [ ] `tarefa-editar.js` — contexto `'tarefas'`

### Orçamentos

- [ ] Se tiver categoria no futuro, mesmo padrão

## 14.6 Menu lateral "Categorias"

**Adicionar no menu (sidebar):**
```jinja
<a href="{{ url_for('categorias.ini_categorias') }}" class="menu-item">
    <i class="bi bi-tags"></i>
    <span>Categorias</span>
</a>
```

**Tela de categorias:**
- [ ] Aba "Finanças"
- [ ] Aba "Tarefas"
- [ ] Aba "Orçamentos" (futuro)
- [ ] CRUD completo em cada aba

## 14.7 Prioridade

🟡 Média

## 14.8 Tempo estimado

2-3h (backend + 3 modais + tela dedicada)

## 14.9 Armadilhas

| Armadilha | Solução |
|-----------|---------|
| Modal empilhado z-index errado | O mini-modal tem z-index MAIOR que o de trás |
| ESC fecha o de trás | `e.stopPropagation()` no keydown |
| Categoria duplicada | Backend valida `LOWER(nome)` |
| `categoria_id` diferente entre tabelas | **Tabelas separadas** (`categorias_financas` vs `categorias_tarefas`) |
| Categoria criada mas não aparece | Força `select.add(option)` + `select.value = data.id` |
| `<option>` sem cor | Adiciona `data-cor` + CSS `option[data-cor]` |