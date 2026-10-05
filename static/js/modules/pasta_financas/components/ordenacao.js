// static/js/modules/pasta_financas/components/ordenacao.js
// ==========================================================
// ORDENAÇÃO DE COLUNAS (2099)
// Event delegation — funciona sempre, sem listeners duplicados
// ==========================================================

(function() {
    'use strict';

    let colunaAtual = null;
    let ordemAtual = 'asc';

    // Tipos por índice de coluna
    const TIPOS_COLUNAS = {
        0: 'numero',   // SEQ
        1: 'texto',    // TIPO
        2: 'numero',   // VALOR
        3: 'texto',    // DESCRIÇÃO
        4: 'texto',    // STATUS
        5: 'texto',    // CATEGORIA
        6: 'data',     // EMISSÃO
        7: 'data',     // VENCIMENTO
    };

    // ==========================================================
    // EXTRAI VALOR PRA COMPARAÇÃO
    // ==========================================================
    function getValorParaComparacao(celula, tipo) {
        const texto = celula?.innerText?.trim() || '';

        if (tipo === 'numero') {
            return parseFloat(texto.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
        }
        if (tipo === 'data') {
            if (texto && texto !== '-') {
                const partes = texto.split('/');
                if (partes.length === 3) {
                    return new Date(partes[2], partes[1] - 1, partes[0]).getTime();
                }
            }
            return 0;
        }
        return (texto || '').toLowerCase();
    }

    // ==========================================================
    // ORDENA
    // ==========================================================
    function ordenarTabela(colunaIndex, tipo) {
        const tbody = document.querySelector('.custom-table tbody');
        if (!tbody) return;

        const linhas = Array.from(tbody.querySelectorAll('tr'));
        const linhasValidas = linhas.filter(row => !row.querySelector('td[colspan]'));
        const linhasMensagem = linhas.filter(row => row.querySelector('td[colspan]'));

        const linhasComValor = linhasValidas.map(linha => ({
            linha: linha,
            valor: getValorParaComparacao(linha.children[colunaIndex], tipo)
        }));

        linhasComValor.sort((a, b) => {
            if (a.valor < b.valor) return ordemAtual === 'asc' ? -1 : 1;
            if (a.valor > b.valor) return ordemAtual === 'asc' ? 1 : -1;
            return 0;
        });

        const fragment = document.createDocumentFragment();
        linhasComValor.forEach(item => fragment.appendChild(item.linha));
        linhasMensagem.forEach(row => fragment.appendChild(row));

        tbody.innerHTML = '';
        tbody.appendChild(fragment);
    }

    // ==========================================================
    // EVENT DELEGATION — 1 listener só, funciona após swap
    // ==========================================================
    document.addEventListener('click', function(e) {
        const th = e.target.closest('.custom-table th');
        if (!th) return;

        // Descobre o índice da coluna
        const ths = Array.from(th.parentNode.children);
        const idx = ths.indexOf(th);

        const tipo = TIPOS_COLUNAS[idx];
        if (!tipo) return;   // coluna "AÇÕES" (última) não ordena

        // Remove classes de todos
        document.querySelectorAll('.custom-table th').forEach(h => {
            h.classList.remove('asc', 'desc');
        });

        // Alterna ordem
        if (colunaAtual === idx) {
            ordemAtual = ordemAtual === 'asc' ? 'desc' : 'asc';
        } else {
            colunaAtual = idx;
            ordemAtual = 'asc';
        }

        th.classList.add(ordemAtual === 'asc' ? 'asc' : 'desc');
        ordenarTabela(idx, tipo);
    });

    // Aplica classe .sortable em todos os `<th>` (menos a última = AÇÕES)
    function marcarColunasOrdenaveis() {
        const ths = document.querySelectorAll('.custom-table th');
        ths.forEach((th, idx) => {
            if (TIPOS_COLUNAS[idx]) th.classList.add('sortable');
        });
    }

    // Marca ao carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', marcarColunasOrdenaveis);
    } else {
        marcarColunasOrdenaveis();
    }

    // 🔥 Após HTMX trocar a tabela, remarka (mas NÃO adiciona listener)
    document.addEventListener('htmx:afterSwap', function(evento) {
        if (evento.detail.target?.id === 'tabela-container') {
            marcarColunasOrdenaveis();
        }
    });

    console.log('✅ Ordenação Finanças (2099) carregada!');

})();