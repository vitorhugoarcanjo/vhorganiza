// static/js/modules/pasta_tarefas/tarefas.js
// ==========================================================
// TAREFAS - MAIN (só orquestra)
// ==========================================================

(function() {
    'use strict';

    /**
     * Recarrega a tabela de tarefas via HTMX mantendo os filtros atuais.
     */
    function recarregarTabelaTarefas() {
        var tabelaContainer = document.getElementById('tabela-container');
        if (!tabelaContainer) return;

        var urlRefresh = tabelaContainer.dataset.urlRefresh || '/tarefas';

        htmx.ajax('GET', urlRefresh, {
            target: '#tabela-container',
            swap: 'outerHTML'
        });
    }

    /**
     * Inicializa os ouvintes de eventos da página.
     */
    function init() {
        // Escuta evento personalizado enviado pelo backend
        document.body.addEventListener('atualizarTabelaTarefas', function() {
            recarregarTabelaTarefas();
        });

        // Reinicializa componentes após troca do fragmento HTMX
        document.addEventListener('htmx:afterSwap', function(evento) {
            if (evento.detail.target && evento.detail.target.id === 'tabela-container') {
                if (typeof window.inicializarMenuContexto === 'function') {
                    window.inicializarMenuContexto();
                }
            }
        });
    }

    // Exporta para uso global
    window.recarregarTabelaTarefas = recarregarTabelaTarefas;

    // Executa após carregamento
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ TAREFAS - MAIN carregado!');

})();