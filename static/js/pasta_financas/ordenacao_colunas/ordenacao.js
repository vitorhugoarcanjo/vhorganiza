// Ordenação de colunas na tabela
(function() {
    'use strict';
    
    let colunaAtual = null;
    let ordemAtual = 'asc';
    
    function ordenarTabela(colunaIndex, tipo) {
        const tabela = document.querySelector('.custom-table tbody');
        if (!tabela) return;
        
        const linhas = Array.from(tabela.querySelectorAll('tr'));
        
        // Filtra linhas válidas (ignora mensagem "nenhuma transação")
        const linhasValidas = linhas.filter(linha => {
            return !linha.querySelector('td[colspan]');
        });
        
        // Ordena as linhas
        linhasValidas.sort((a, b) => {
            const celulaA = a.children[colunaIndex]?.innerText.trim() || '';
            const celulaB = b.children[colunaIndex]?.innerText.trim() || '';
            
            let valorA = celulaA;
            let valorB = celulaB;
            
            // Converte para número se for valor monetário
            if (tipo === 'numero') {
                valorA = parseFloat(celulaA.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
                valorB = parseFloat(celulaB.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
            }
            // Converte para data se for data
            else if (tipo === 'data') {
                valorA = new Date(celulaA.split('/').reverse().join('-')) || new Date(0);
                valorB = new Date(celulaB.split('/').reverse().join('-')) || new Date(0);
            }
            
            if (valorA < valorB) return ordemAtual === 'asc' ? -1 : 1;
            if (valorA > valorB) return ordemAtual === 'asc' ? 1 : -1;
            return 0;
        });
        
        // Reconstroi a tabela
        linhasValidas.forEach(linha => tabela.appendChild(linha));
        
        // Mantém as linhas de mensagem no final
        const linhasMensagem = linhas.filter(linha => linha.querySelector('td[colspan]'));
        linhasMensagem.forEach(linha => tabela.appendChild(linha));
    }
    
    function initOrdenacao() {
        const cabecalhos = document.querySelectorAll('.custom-table th');
        
        // Tipos de cada coluna (índice, tipo)
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
            // Adiciona classe sortable
            th.classList.add('sortable');
            
            // Encontra o tipo da coluna
            const colunaInfo = tiposColunas.find(c => c.index === idx);
            if (!colunaInfo) return;
            
            th.addEventListener('click', () => {
                // Reseta as setas das outras colunas
                cabecalhos.forEach(h => {
                    h.classList.remove('asc', 'desc');
                });
                
                // Alterna a ordem
                if (colunaAtual === idx) {
                    ordemAtual = ordemAtual === 'asc' ? 'desc' : 'asc';
                } else {
                    colunaAtual = idx;
                    ordemAtual = 'asc';
                }
                
                // Adiciona classe para mostrar a seta
                th.classList.add(ordemAtual === 'asc' ? 'asc' : 'desc');
                
                // Ordena
                ordenarTabela(idx, colunaInfo.tipo);
            });
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOrdenacao);
    } else {
        initOrdenacao();
    }
})();