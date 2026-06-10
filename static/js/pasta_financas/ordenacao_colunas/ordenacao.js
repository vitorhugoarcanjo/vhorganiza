// ordenacao.js - VERSÃO OTIMIZADA COM HTMX
(function() {
    'use strict';
    
    let colunaAtual = null;
    let ordemAtual = 'asc';
    
    // CACHE para valores processados (evita recalcular)
    let cacheValores = new Map();
    
    function getValorParaComparacao(celula, tipo) {
        const texto = celula?.innerText?.trim() || '';
        
        // Usa cache se já calculou antes
        const cacheKey = `${tipo}_${texto}`;
        if (cacheValores.has(cacheKey)) {
            return cacheValores.get(cacheKey);
        }
        
        let valor;
        
        if (tipo === 'numero') {
            valor = parseFloat(texto.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
        } 
        else if (tipo === 'data') {
            if (texto && texto !== '-') {
                const partes = texto.split('/');
                if (partes.length === 3) {
                    valor = new Date(partes[2], partes[1] - 1, partes[0]);
                } else {
                    valor = new Date(0);
                }
            } else {
                valor = new Date(0);
            }
        } 
        else { // texto
            valor = (texto || '').toLowerCase();
        }
        
        cacheValores.set(cacheKey, valor);
        return valor;
    }
    
    function ordenarTabela(colunaIndex, tipo) {
        const tbody = document.querySelector('.custom-table tbody');
        if (!tbody) return;
        
        const linhas = Array.from(tbody.querySelectorAll('tr'));
        
        const linhasValidas = [];
        const linhasMensagem = [];
        
        for (let i = 0; i < linhas.length; i++) {
            const linha = linhas[i];
            if (linha.querySelector('td[colspan]')) {
                linhasMensagem.push(linha);
            } else {
                linhasValidas.push(linha);
            }
        }
        
        if (colunaAtual !== colunaIndex) {
            cacheValores.clear();
        }
        
        const linhasComValor = linhasValidas.map(linha => ({
            linha: linha,
            valor: getValorParaComparacao(linha.children[colunaIndex], tipo)
        }));
        
        linhasComValor.sort((a, b) => {
            const valorA = a.valor;
            const valorB = b.valor;
            
            if (valorA < valorB) return ordemAtual === 'asc' ? -1 : 1;
            if (valorA > valorB) return ordemAtual === 'asc' ? 1 : -1;
            return 0;
        });
        
        const fragment = document.createDocumentFragment();
        
        for (let i = 0; i < linhasComValor.length; i++) {
            fragment.appendChild(linhasComValor[i].linha);
        }
        
        for (let i = 0; i < linhasMensagem.length; i++) {
            fragment.appendChild(linhasMensagem[i]);
        }
        
        tbody.innerHTML = '';
        tbody.appendChild(fragment);
    }
    
    function initOrdenacao() {
        const cabecalhos = document.querySelectorAll('.custom-table th');
        
        const tiposColunas = [
            { index: 0, tipo: 'numero', nome: 'SEQ' },
            { index: 1, tipo: 'texto', nome: 'TIPO' },
            { index: 2, tipo: 'numero', nome: 'VALOR' },
            { index: 3, tipo: 'texto', nome: 'DESCRICAO' },
            { index: 4, tipo: 'texto', nome: 'STATUS' },
            { index: 5, tipo: 'texto', nome: 'CATEGORIA' },
            { index: 6, tipo: 'data', nome: 'EMISSAO' },
            { index: 7, tipo: 'data', nome: 'VENCIMENTO' }
        ];
        
        cabecalhos.forEach((th, idx) => {
            th.classList.add('sortable');
            
            const colunaInfo = tiposColunas.find(c => c.index === idx);
            if (!colunaInfo) return;
            
            let timeout = null;
            
            th.addEventListener('click', () => {
                if (timeout) return;
                
                timeout = setTimeout(() => {
                    cabecalhos.forEach(h => {
                        h.classList.remove('asc', 'desc');
                    });
                    
                    if (colunaAtual === idx) {
                        ordemAtual = ordemAtual === 'asc' ? 'desc' : 'asc';
                    } else {
                        colunaAtual = idx;
                        ordemAtual = 'asc';
                    }
                    
                    th.classList.add(ordemAtual === 'asc' ? 'asc' : 'desc');
                    ordenarTabela(idx, colunaInfo.tipo);
                    
                    timeout = null;
                }, 10);
            });
        });
    }
    
    // 🔥 NOVO: Função para re-inicializar após HTMX
    function reinitOrdenacao() {
        cacheValores.clear();
        colunaAtual = null;
        ordemAtual = 'asc';
        initOrdenacao();
    }
    
    // Inicializa na primeira carga
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOrdenacao);
    } else {
        initOrdenacao();
    }
    
    // 🔥 NOVO: Detecta substituição da tabela pelo HTMX
    document.body.addEventListener('htmx:afterSwap', function(evento) {
        if (evento.detail.target.id === 'tabela-container') {
            reinitOrdenacao();
        }
    });
    
})();