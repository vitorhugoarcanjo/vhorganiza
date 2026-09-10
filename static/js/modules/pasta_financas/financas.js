// ==========================================================
// FINANÇAS - MAIN
// ==========================================================

(function() {
    'use strict';

    /**
     * Recarrega a tabela de finanças via HTMX mantendo os filtros atuais.
     * Busca a URL do data-attribute do container ou usa '/financas' como fallback.
     */
    function recarregarTabelaFinancas() {
        var tabelaContainer = document.getElementById('tabela-container');
        if (!tabelaContainer) return;

        // Recupera a URL configurada no data-url-refresh do container, ou usa a rota principal
        var urlRefresh = tabelaContainer.dataset.urlRefresh || '/financas';

        htmx.ajax('GET', urlRefresh, {
            target: '#tabela-container',
            swap: 'outerHTML'
        });
    }

    /**
     * Inicializa os ouvintes de eventos da página.
     */
    function init() {
        // Escuta evento personalizado enviado pelo backend (Response Header: HX-Trigger: atualizarTabelaFinancas)
        document.body.addEventListener('atualizarTabelaFinancas', function() {
            recarregarTabelaFinancas();
        });

        // Re-inicializa componentes após troca do fragmento HTMX na tabela
        document.addEventListener('htmx:afterSwap', function(evento) {
            if (evento.detail.target && evento.detail.target.id === 'tabela-container') {
                // Eventos de clique com o botão direito ou inicializações de UI da tabela podem vir aqui
                if (typeof window.inicializarMenuContexto === 'function') {
                    window.inicializarMenuContexto();
                }
            }
        });
    }

    // Exporta a função para escopo global para acionamento direto via onclick ou outros modais
    window.recarregarTabelaFinancas = recarregarTabelaFinancas;

    // Executar após o carregamento da árvore DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ FINANÇAS - MAIN carregado!');

})();