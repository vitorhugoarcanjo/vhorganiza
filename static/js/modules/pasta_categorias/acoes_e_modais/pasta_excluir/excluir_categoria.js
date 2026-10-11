// static/js/modules/pasta_categorias/acoes_e_modais/pasta_excluir/excluir_categoria.js
// ==========================================================
// INATIVAR CATEGORIA — HTMX puro
// ==========================================================

(function() {
    'use strict';

    var modalAberto = false;

    window.fecharModalExcluirCategoria = function() {
        var modal = document.getElementById('modalExcluirCategoria');
        if (modal) modal.classList.remove('active');
        modalAberto = false;
    };

    window.abrirModalExcluirCategoria = function(config) {
        if (modalAberto) return;

        var modal = document.getElementById('modalExcluirCategoria');
        var nomeEl = document.getElementById('nomeCategoriaExcluir');

        var btnConfirmar = document.getElementById('btnConfirmarExcluirCategoria');
        if (btnConfirmar && btnConfirmar.parentNode) {
            var clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        var btnCancelar = document.getElementById('btnCancelarExcluirCategoria');

        if (!modal || !btnConfirmar || !btnCancelar) return;

        modalAberto = true;
        if (nomeEl) nomeEl.textContent = config.nome;
        modal.classList.add('active');

        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-categorias-' + config.modulo);
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        if (window.htmx) window.htmx.process(btnConfirmar);

        btnCancelar.onclick = window.fecharModalExcluirCategoria;
        modal.onclick = function(e) {
            if (e.target === modal) window.fecharModalExcluirCategoria();
        };

        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            var status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) window.fecharModalExcluirCategoria();
            btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
        });
    };

    // Delegação
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-excluir');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        window.abrirModalExcluirCategoria({
            nome: btn.dataset.nome,
            url: '/categorias/excluir_categoria/' + btn.dataset.id,
            modulo: btn.closest('tbody').id.replace('tbody-categorias-', '')
        });
    });

    // Toast via HX-Trigger
    document.body.addEventListener('categoriaInativada', function(evt) {
        modalAberto = false;
        var modal = document.getElementById('modalExcluirCategoria');
        if (modal) modal.classList.remove('active');

        var msg = evt.detail && evt.detail.message ? evt.detail.message : 'Categoria inativada!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de exclusão de categorias carregado!');
})();