# 06 — Frontend

## 6.1 Classe `<X>Form` (core, compartilhada)

- `mode: 'create'` ou `'edit'`
- `setData(data)` — popula no edit
- `getData()` — serializa pro POST
- `submit(url)` — **SEMPRE JSON** + validações
- `reset()` — limpa no create

## 6.2 Submits

- **insert/edit** → `fetch` + JSON
- **delete/concluir/reativar** → **HTMX puro**

## 6.3 Pós-insert = `htmx.ajax`

**NUNCA `window.location.reload()`.**

```javascript
if (data.success) {
    window.Notificacao.sucesso(data.message);
    fecharModal();

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

## 6.4 Validação campo-a-campo

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

function limparErrosForm() {
    document.querySelectorAll('.campo-erro').forEach(el => el.classList.remove('campo-erro'));
    document.querySelectorAll('.msg-erro-campo').forEach(el => el.remove());
}
```

## 6.5 Padrão de ação HTMX (1 arquivo por ação)

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

## 6.6 Orquestrador `<modulo>.js`

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

## 6.7 Auditoria modal (accordion)

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

## 6.8 JS compartilhado

**`static/js/components/botoes_filtros.js`** — atualiza o visual dos botões do toggle:

```javascript
(function() {
    'use strict';

    function atualizarBotoesFiltro() {
        var input = document.getElementById('mostrar_inativas_input');
        if (!input) return;
        var valor = input.value;
        if (!valor) return;

        document.querySelectorAll('.btn-filter').forEach(function(btn) {
            btn.classList.remove('btn-active-toggle');
        });

        var botaoAtivo = document.querySelector(
            '.btn-filter[hx-vals*=\'mostrar_inativas": "' + valor + '"\']'
        );
        if (botaoAtivo) botaoAtivo.classList.add('btn-active-toggle');
    }

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;
        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            atualizarBotoesFiltro();
        }
    });

    console.log('✅ Botoes filtros (compartilhado) carregado!');
})();
```