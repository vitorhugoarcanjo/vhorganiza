# 15 — Modais Empilhados

## 15.1 Contexto

Quando você tem **modal dentro de modal** (ex: nova tarefa → nova categoria), precisa cuidar de:

- **z-index** — o de cima precisa aparecer
- **ESC** — fecha o de cima, não o de baixo
- **Foco** — deve ir pro input do modal de cima
- **Scroll** — não pode scrollar o de baixo
- **HTMX swap** — não substituir o modal de baixo

## 15.2 Z-index

**Padrão 2099:**

| Modal | z-index |
|-------|---------|
| Modal principal (nova tarefa) | `99999` |
| Mini-modal (nova categoria) | `100000` |
| Notificação (toast) | `999999` |

**CSS:**

```css
.fin-modal-overlay {
    z-index: 99999;   /* base */
}

.fin-modal-overlay.modal-empilhado {
    z-index: 100000;  /* em cima */
}

.notificacao-toast {
    z-index: 999999;  /* sempre no topo */
}
```

**Aplicar no mini-modal:**

```html
<div class="fin-modal-overlay modal-empilhado" id="modalNovaCategoriaInline">
```

## 15.3 ESC — fecha só o de cima

**Problema:** se cada modal tem seu `keydown`, os 2 fecham ao mesmo tempo.

**Solução 2099:** cada listener verifica se **o seu** modal tá ativo. **Se sim**, fecha e **para a propagação**.

```javascript
document.addEventListener('keydown', function(e) {
    if (e.key !== 'Escape') return;

    // 🔥 Verifica se é o modal ATIVO
    var modal = document.getElementById('modalNovaCategoriaInline');
    if (!modal || !modal.classList.contains('active')) return;

    // 🔥 Fecha só esse
    fecharModalNovaCategoria();

    // 🔥 Para a propagação (o de baixo NÃO recebe)
    e.stopPropagation();
    e.preventDefault();
}, true);   // ← 🔥 useCapture = true (pega ANTES dos outros)
```

**⚠️ IMPORTANTE:** o `true` no final (3º argumento) faz o listener rodar **antes** dos outros (fase de captura).

## 15.4 Foco no input do modal de cima

**Ao abrir o mini-modal:**

```javascript
setTimeout(function() {
    var nome = modal.querySelector('.js-cat-nome');
    if (nome) nome.focus();
}, 100);
```

**Ao fechar o mini-modal:** devolve o foco pro botão `+` (opcional):

```javascript
function fecharModalNovaCategoria() {
    var modal = document.getElementById('modalNovaCategoriaInline');
    if (modal) modal.classList.remove('active');

    // Devolve foco pro botão que abriu
    var btn = document.querySelector('.btn-add-categoria');
    if (btn) btn.focus();
}
```

## 15.5 Scroll do modal de baixo

**Problema:** o modal de baixo tem `overflow: hidden` no body. O de cima **também** mexe no body.

**Solução 2099:** **só o modal raiz** mexe no `body.style.overflow`.

```javascript
// Ao abrir mini-modal: NÃO mexe no body
window.abrirModalNovaCategoria = function(modulo) {
    // ... NÃO faz: document.body.style.overflow = 'hidden';
    // O modal de baixo já fez isso
};

// Ao fechar mini-modal: NÃO mexe no body
window.fecharModalNovaCategoria = function() {
    // ... NÃO faz: document.body.style.overflow = '';
    // Deixa o modal de baixo cuidar
};
```

**Regra:** quem mexe no `body.style.overflow` é **só o modal raiz** (o primeiro).

## 15.6 HTMX swap não deve substituir modal de baixo

**Problema:** se o mini-modal é injetado via HTMX com `hx-target` errado, pode substituir o modal de baixo.

**Solução:** mini-modais **estáticos** (no `base.html` ou na tela), **não injetados**.

**RUIM:**
```html
<button hx-get="/categorias/modal-criar" hx-target="#modal-nova-container">
```

**BOM:**
```html
{% include 'pasta_categorias/modais/modal_nova_categoria_inline.html.jinja' %}
```

## 15.7 Fechar o modal de baixo não pode fechar o de cima

**Problema:** se o usuário clicar no `[X]` do modal de baixo, o de cima tem que fechar também (senão fica órfão).

**Solução 2099:** ao fechar o modal raiz, fechar todos os filhos.

```javascript
function fecharModalNovaTarefa() {
    // 🔥 Fecha todos os mini-modais abertos
    document.querySelectorAll('.fin-modal-overlay.modal-empilhado').forEach(function(el) {
        el.classList.remove('active');
    });

    // Fecha o raiz
    var container = document.getElementById('modal-nova-container');
    if (container) container.innerHTML = '';
    document.body.style.overflow = '';
    formInstance = null;
}
```

## 15.8 CSS completo pra modais empilhados

```css
/* Modal raiz (padrão) */
.fin-modal-overlay {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.85);
    display: none; justify-content: center; align-items: center;
    z-index: 99999;
    backdrop-filter: blur(8px);
}

.fin-modal-overlay.active { display: flex; }

/* Mini-modal (empilhado) */
.fin-modal-overlay.modal-empilhado {
    z-index: 100000;
    background: rgba(0, 0, 0, 0.6);   /* mais claro */
}

.fin-modal-box-small {
    height: auto;
    max-height: 60vh;
    width: 90%;
    max-width: 480px;
    border-radius: 12px;
    margin: auto;
    animation: finModalSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fin-modal-box-small .fin-modal-body {
    padding: 20px 24px;
    max-height: calc(60vh - 120px);
    overflow-y: auto;
}
```

## 15.9 Checklist — Criar modal empilhado

- [ ] **z-index** maior (`modal-empilhado`)
- [ ] **ESC** com `stopPropagation()` + `useCapture=true`
- [ ] **Foco** no input ao abrir
- [ ] **NÃO mexer** no `body.style.overflow` (deixa o modal raiz)
- [ ] **NÃO injetar** via HTMX (estático no template)
- [ ] **Fechar filhos** quando fechar o modal raiz
- [ ] **Testar:** abrir os 2, apertar ESC, ver se fecha só o de cima
- [ ] **Testar:** fechar o raiz com o mini-modal aberto → fecha tudo

## 15.10 Prioridade

🟡 Média (depende da feature de categorias inline)

## 15.11 Tempo estimado

30 min (depois que a feature de categorias estiver pronta)

## 15.12 Armadilhas comuns

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| Sem `modal-empilhado` | Mini-modal aparece ATRÁS | Adicionar classe |
| ESC sem `stopPropagation` | Fecha os 2 modais | `e.stopPropagation()` + `useCapture=true` |
| Mexer no body no mini-modal | Scroll duplo / trava | Deixa o modal raiz só |
| HTMX injeta mini-modal | Substitui modal de baixo | Mini-modal estático no template |
| Não fecha filhos | Mini-modal órfão | Fechar `.modal-empilhado` ao fechar raiz |