// static/js/modules/pasta_categorias/modals/categoria-editar.js
// ==========================================================
// MODAL EDITAR CATEGORIA
// ==========================================================

(function() {
    'use strict';

    var formInstance = null;

    window.fecharModalEditarCategoria = function() {
        var container = document.getElementById('modal-editar-container');
        if (container) container.innerHTML = '';
        document.body.style.overflow = '';
        formInstance = null;
    };

    // Quando o HTMX carrega o modal, inicializa o form
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'modal-editar-container') {
            document.body.style.overflow = 'hidden';
            formInstance = new window.CategoriaForm('edit');
            formInstance.init();
        }
    });

    // ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalEditarCategoria');
            if (modal) fecharModalEditarCategoria();
        }
    });

    console.log('✅ Modal editar categoria carregado!');
})();