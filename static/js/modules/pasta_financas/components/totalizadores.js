// totalizadores.js - VERSÃO COMPLETA E CORRIGIDA

function calcularTotaisFinancas() {
    const linhas = document.querySelector('.custom-table tbody')?.children || [];
    let totalReceitas = 0;
    let totalDespesas = 0;
    
    for (let i = 0; i < linhas.length; i++) {
        const linha = linhas[i];
        if (linha.querySelector('td[colspan]')) continue;
        
        const colunas = linha.cells;
        if (colunas.length < 3) continue;
        
        const tipo = colunas[1]?.innerText || '';
        const valorTexto = colunas[2]?.innerText || 'R$ 0,00';
        
        let valor = parseFloat(valorTexto.replace('R$', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
        
        if (tipo.includes('Receita')) totalReceitas += valor;
        else if (tipo.includes('Despesa')) totalDespesas += valor;
    }
    
    const saldo = totalReceitas - totalDespesas;
    const formatar = (v) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    
    const elReceitas = document.getElementById('totalReceitas');
    const elDespesas = document.getElementById('totalDespesas');
    const elSaldo = document.getElementById('totalSaldo');
    
    if (elReceitas) elReceitas.innerHTML = formatar(totalReceitas);
    if (elDespesas) elDespesas.innerHTML = formatar(totalDespesas);
    if (elSaldo) elSaldo.innerHTML = formatar(saldo);
}

// ==========================================================
// 🔥 INICIALIZAÇÃO
// ==========================================================

// 1. Quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(calcularTotaisFinancas, 100);
    });
} else {
    setTimeout(calcularTotaisFinancas, 100);
}

// 2. 🔥 DEPOIS QUE O HTMX ATUALIZAR A TABELA
document.addEventListener('htmx:afterSwap', function(evento) {
    if (evento.detail.target?.id === 'tabela-container') {
        setTimeout(calcularTotaisFinancas, 150);
    }
});

// 3. 🔥 DEPOIS DE QUALQUER REQUISIÇÃO HTMX
document.addEventListener('htmx:afterRequest', function(evento) {
    const target = evento.detail.target;
    if (target && (target.id === 'tabela-container' || target.closest('#tabela-container'))) {
        setTimeout(calcularTotaisFinancas, 150);
    }
});

// 4. Quando o formulário de filtros for submetido
document.addEventListener('submit', function(e) {
    if (e.target.id === 'form-filtros') {
        setTimeout(calcularTotaisFinancas, 200);
    }
});

// 5. 🔥 TAMBÉM QUANDO OS BOTÕES DE FILTRO RÁPIDO FOREM CLICADOS
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-pure');
    if (btn && btn.closest('#form-filtros')) {
        setTimeout(calcularTotaisFinancas, 300);
    }
});

console.log('✅ Totalizadores carregados e monitorando mudanças!');