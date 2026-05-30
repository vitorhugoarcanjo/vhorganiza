// Ordenação de colunas na tabela de Tarefas
(function() {
    'use strict';
    
    let colunaAtual = null;
    let ordemAtual = 'asc';
    
    function ordenarTabela(colunaIndex, tipo) {
        const tabela = document.querySelector('.custom-table tbody');
        if (!tabela) return;
        
        const linhas = Array.from(tabela.querySelectorAll('tr'));
        
        // Filtra linhas válidas (ignora mensagem "nenhuma tarefa")
        const linhasValidas = linhas.filter(linha => {
            return !linha.querySelector('td[colspan]');
        });
        
        // Ordena as linhas
        linhasValidas.sort((a, b) => {
            let valorA = a.children[colunaIndex]?.innerText.trim() || '';
            let valorB = b.children[colunaIndex]?.innerText.trim() || '';
            
            // Converte para número se for coluna numérica
            if (tipo === 'numero') {
                valorA = parseInt(valorA) || 0;
                valorB = parseInt(valorB) || 0;
            }
            // Converte para data se for data
            else if (tipo === 'data') {
                valorA = valorA ? new Date(valorA.split('/').reverse().join('-')) : new Date(0);
                valorB = valorB ? new Date(valorB.split('/').reverse().join('-')) : new Date(0);
            }
            // Converte para texto (padrão)
            else {
                valorA = valorA.toLowerCase();
                valorB = valorB.toLowerCase();
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
        
        // Tipos de cada coluna da tabela de Tarefas
        const tiposColunas = [
            { index: 0, tipo: 'numero', nome: 'Nº REG.' },
            { index: 1, tipo: 'texto', nome: 'TÍTULO' },
            { index: 2, tipo: 'texto', nome: 'STATUS' },
            { index: 3, tipo: 'data', nome: 'DATA INICIO' },
            { index: 4, tipo: 'data', nome: 'DATA FINAL' },
            { index: 5, tipo: 'data', nome: 'DATA FINALIZAÇÃO' },
            { index: 6, tipo: 'texto', nome: 'CATEGORIA' },
            { index: 7, tipo: 'texto', nome: 'PRIORIDADE' }
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