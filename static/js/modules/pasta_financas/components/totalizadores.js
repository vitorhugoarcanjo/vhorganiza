// static/js/modules/pasta_financas/components/totalizadores.js

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

// 1. Carga inicial
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', calcularTotaisFinancas);
} else {
    calcularTotaisFinancas();
}

// 2. 🔥 Único listener — afterSwap (DOM pronto, sem setTimeout)
document.body.addEventListener('htmx:afterSwap', function(evt) {
    const target = evt.detail.target;
    if (!target) return;

    if (target.id === 'tabela-container' ||
        target.id === 'tbody-transacoes' ||
        target.closest('#tabela-container')) {
        calcularTotaisFinancas();
    }
});

console.log('✅ Totalizadores carregados!');