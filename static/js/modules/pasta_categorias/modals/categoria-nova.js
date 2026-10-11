// static/js/modules/pasta_categorias/modals/categoria-nova.js
// ==========================================================
// MODAL NOVA CATEGORIA
// ==========================================================

(function() {
    'use strict';

    var formInstance = null;

    window.abrirModalNovaCategoria = function(modulo) {
        modulo = modulo || 'tarefas';

        if (window.htmx) {
            window.htmx.ajax('GET', '/categorias/nova_categoria/modal?modulo=' + modulo, {
                target: '#modal-nova-container',
                swap: 'innerHTML'
            });
        }
    };

    window.fecharModalNovaCategoria = function() {
        var container = document.getElementById('modal-nova-container');
        if (container) container.innerHTML = '';
        document.body.style.overflow = '';
        formInstance = null;
    };

    // Quando o HTMX carrega o modal, inicializa o form
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'modal-nova-container') {
            document.body.style.overflow = 'hidden';
            formInstance = new window.CategoriaForm('create');
            formInstance.init();
        }
    });

    // ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalNovaCategoria');
            if (modal) fecharModalNovaCategoria();
        }
    });

    console.log('✅ Modal nova categoria carregado!');
})();