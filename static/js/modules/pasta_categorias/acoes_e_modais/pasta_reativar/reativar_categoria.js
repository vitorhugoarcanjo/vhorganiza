// static/js/modules/pasta_categorias/acoes_e_modais/pasta_reativar/reativar_categoria.js
// ==========================================================
// REATIVAR CATEGORIA — HTMX puro
// ==========================================================

(function() {
    'use strict';

    var modalAberto = false;

    window.fecharModalReativarCategoria = function() {
        var modal = document.getElementById('modalReativarCategoria');
        if (modal) modal.classList.remove('active');
        modalAberto = false;
    };

    window.abrirModalReativarCategoria = function(config) {
        if (modalAberto) return;

        var modal = document.getElementById('modalReativarCategoria');
        var nomeEl = document.getElementById('nomeCategoriaReativar');

        var btnConfirmar = document.getElementById('btnConfirmarReativarCategoria');
        if (btnConfirmar && btnConfirmar.parentNode) {
            var clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        var btnCancelar = document.getElementById('btnCancelarReativarCategoria');

        if (!modal || !btnConfirmar || !btnCancelar) return;

        modalAberto = true;
        if (nomeEl) nomeEl.textContent = config.nome;
        modal.classList.add('active');

        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-categorias-' + config.modulo);
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        if (window.htmx) window.htmx.process(btnConfirmar);

        btnCancelar.onclick = window.fecharModalReativarCategoria;
        modal.onclick = function(e) {
            if (e.target === modal) window.fecharModalReativarCategoria();
        };

        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            var status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) window.fecharModalReativarCategoria();
            btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
        });
    };

    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-reativar');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        window.abrirModalReativarCategoria({
            nome: btn.dataset.nome,
            url: '/categorias/reativar_categoria/' + btn.dataset.id,
            modulo: btn.closest('tbody').id.replace('tbody-categorias-', '')
        });
    });

    document.body.addEventListener('categoriaReativada', function(evt) {
        modalAberto = false;
        var modal = document.getElementById('modalReativarCategoria');
        if (modal) modal.classList.remove('active');

        var msg = evt.detail && evt.detail.message ? evt.detail.message : 'Categoria reativada!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de reativação de categorias carregado!');
})();