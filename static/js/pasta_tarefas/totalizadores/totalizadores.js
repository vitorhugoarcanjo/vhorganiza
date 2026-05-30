// Totalizadores da Tela de Tarefas
(function() {
    'use strict';

    function calcularTotaisTarefas() {
        const tabela = document.querySelector('.custom-table');
        if (!tabela) return;

        const linhas = tabela.querySelectorAll('tbody tr');
        let pendentes = 0;
        let andamento = 0;
        let concluidas = 0;

        linhas.forEach(linha => {
            // Pula a linha de "nenhuma tarefa"
            if (linha.querySelector('td[colspan]')) return;

            const colunas = linha.querySelectorAll('td');
            if (colunas.length < 3) return;

            // Coluna STATUS é a terceira (índice 2)
            const statusText = colunas[2]?.innerText || '';

            if (statusText.includes('Pendente')) {
                pendentes++;
            } else if (statusText.includes('Andamento')) {
                andamento++;
            } else if (statusText.includes('Concluída')) {
                concluidas++;
            }
        });

        // Atualiza os spans
        const spanPendentes = document.getElementById('totalPendentes');
        const spanAndamento = document.getElementById('totalAndamento');
        const spanConcluidas = document.getElementById('totalConcluidas');

        if (spanPendentes) spanPendentes.innerText = pendentes;
        if (spanAndamento) spanAndamento.innerText = andamento;
        if (spanConcluidas) spanConcluidas.innerText = concluidas;
    }

    // Executa quando a página carregar
    document.addEventListener('DOMContentLoaded', function() {
        calcularTotaisTarefas();

        // Observa mudanças na tabela
        const observer = new MutationObserver(function() {
            calcularTotaisTarefas();
        });

        const tabela = document.querySelector('.custom-table');
        if (tabela) {
            observer.observe(tabela, { childList: true, subtree: true });
        }

        // Quando o formulário de filtros for enviado, recalcula
        const formFiltros = document.querySelector('.form-filtros-total');
        if (formFiltros) {
            formFiltros.addEventListener('submit', function() {
                setTimeout(calcularTotaisTarefas, 300);
            });
        }
    });
})();