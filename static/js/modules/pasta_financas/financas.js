// ==========================================================
// FINANÇAS - MAIN
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // TOTALIZADORES
    // ==========================================================
    function calcularTotaisFinancas() {
        var linhas = document.querySelector('.custom-table tbody')?.children || [];
        var totalReceitas = 0;
        var totalDespesas = 0;
        
        for (var i = 0; i < linhas.length; i++) {
            var linha = linhas[i];
            if (linha.querySelector('td[colspan]')) continue;
            
            var colunas = linha.cells;
            if (colunas.length < 3) continue;
            
            var tipo = colunas[1]?.innerText || '';
            var valorTexto = colunas[2]?.innerText || 'R$ 0,00';
            
            var valor = parseFloat(valorTexto.replace('R$', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
            
            if (tipo.includes('Receita')) totalReceitas += valor;
            else if (tipo.includes('Despesa')) totalDespesas += valor;
        }
        
        var saldo = totalReceitas - totalDespesas;
        var formatar = function(v) {
            return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
        };
        
        var elReceitas = document.getElementById('totalReceitas');
        var elDespesas = document.getElementById('totalDespesas');
        var elSaldo = document.getElementById('totalSaldo');
        
        if (elReceitas) elReceitas.innerHTML = formatar(totalReceitas);
        if (elDespesas) elDespesas.innerHTML = formatar(totalDespesas);
        if (elSaldo) elSaldo.innerHTML = formatar(saldo);
    }

    // ==========================================================
    // INICIALIZAR
    // ==========================================================
    function init() {
        // Totalizadores
        setTimeout(calcularTotaisFinancas, 100);
        
        // HTMX - atualiza totalizadores
        document.addEventListener('htmx:afterSwap', function(evento) {
            if (evento.detail.target?.id === 'tabela-container') {
                setTimeout(calcularTotaisFinancas, 150);
            }
        });
        
        document.addEventListener('htmx:afterRequest', function(evento) {
            var target = evento.detail.target;
            if (target && (target.id === 'tabela-container' || target.closest('#tabela-container'))) {
                setTimeout(calcularTotaisFinancas, 150);
            }
        });
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.calcularTotaisFinancas = calcularTotaisFinancas;

    // ==========================================================
    // EXECUTAR
    // ==========================================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ FINANÇAS - MAIN carregado!');

})();