// static/js/modules/pasta_categorias/categorias.js
// ==========================================================
// ORQUESTRADOR - CATEGORIAS
// ==========================================================

(function() {
    'use strict';

    function recarregarTabelaCategorias() {
        var tabelaContainer = document.getElementById('tabela-container');
        if (!tabelaContainer) return;
        var urlRefresh = tabelaContainer.dataset.urlRefresh || '/categorias/';
        if (window.htmx) {
            window.htmx.ajax('GET', urlRefresh, {
                target: '#tabela-container',
                swap: 'outerHTML',
                headers: { 'HX-Request': 'true' }
            });
        }
    }

    function init() {
        document.body.addEventListener('atualizarTabelaCategorias', function() {
            recarregarTabelaCategorias();
        });
    }

    window.recarregarTabelaCategorias = recarregarTabelaCategorias;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ CATEGORIAS - MAIN carregado!');
})();