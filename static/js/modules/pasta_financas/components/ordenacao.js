// ORDENAÇÃO DE COLUNAS - VERSÃO OTIMIZADA
(function() {
    'use strict';
    
    let colunaAtual = null;
    let ordemAtual = 'asc';
    let cacheValores = new Map();
    
    function getValorParaComparacao(celula, tipo) {
        const texto = celula?.innerText?.trim() || '';
        const cacheKey = `${tipo}_${texto}`;
        
        if (cacheValores.has(cacheKey)) return cacheValores.get(cacheKey);
        
        let valor;
        if (tipo === 'numero') {
            valor = parseFloat(texto.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
        } else if (tipo === 'data') {
            if (texto && texto !== '-') {
                const partes = texto.split('/');
                valor = partes.length === 3 ? new Date(partes[2], partes[1] - 1, partes[0]) : new Date(0);
            } else {
                valor = new Date(0);
            }
        } else {
            valor = (texto || '').toLowerCase();
        }
        
        cacheValores.set(cacheKey, valor);
        return valor;
    }
    
    function ordenarTabela(colunaIndex, tipo) {
        const tbody = document.querySelector('.custom-table tbody');
        if (!tbody) return;
        
        const linhas = Array.from(tbody.querySelectorAll('tr'));
        const linhasValidas = linhas.filter(row => !row.querySelector('td[colspan]'));
        const linhasMensagem = linhas.filter(row => row.querySelector('td[colspan]'));
        
        if (colunaAtual !== colunaIndex) cacheValores.clear();
        
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
    
    function initOrdenacao() {
        const cabecalhos = document.querySelectorAll('.custom-table th');
        const tiposColunas = [
            { index: 0, tipo: 'numero' },
            { index: 1, tipo: 'texto' },
            { index: 2, tipo: 'numero' },
            { index: 3, tipo: 'texto' },
            { index: 4, tipo: 'texto' },
            { index: 5, tipo: 'texto' },
            { index: 6, tipo: 'data' },
            { index: 7, tipo: 'data' }
        ];
        
        cabecalhos.forEach((th, idx) => {
            const colunaInfo = tiposColunas.find(c => c.index === idx);
            if (!colunaInfo) return;
            
            th.classList.add('sortable');
            
            th.addEventListener('click', () => {
                cabecalhos.forEach(h => h.classList.remove('asc', 'desc'));
                
                if (colunaAtual === idx) {
                    ordemAtual = ordemAtual === 'asc' ? 'desc' : 'asc';
                } else {
                    colunaAtual = idx;
                    ordemAtual = 'asc';
                }
                
                th.classList.add(ordemAtual === 'asc' ? 'asc' : 'desc');
                ordenarTabela(idx, colunaInfo.tipo);
            });
        });
    }
    
    function reinitOrdenacao() {
        cacheValores.clear();
        colunaAtual = null;
        ordemAtual = 'asc';
        initOrdenacao();
    }
    
    // Inicialização
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOrdenacao);
    } else {
        initOrdenacao();
    }
    
    // 🔥 CORRIGIDO: document.addEventListener (não document.body)
    document.addEventListener('htmx:afterSwap', function(evento) {
        if (evento.detail.target?.id === 'tabela-container') {
            reinitOrdenacao();
        }
    });
    
})();