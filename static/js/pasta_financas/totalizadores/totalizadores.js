// Versão minimalista (só o essencial)
function calcularTotaisFinancas() {
    const linhas = document.querySelector('.custom-table tbody')?.children || [];
    let totalReceitas = 0;
    let totalDespesas = 0;
    
    // 🔥 SÓ MUDEI de forEach para for
    for (let i = 0; i < linhas.length; i++) {
        const linha = linhas[i];
        if (linha.querySelector('td[colspan]')) continue;
        
        const colunas = linha.cells; // 🔥 MUDEI de querySelectorAll para cells
        if (colunas.length < 3) continue;
        
        const tipo = colunas[1]?.innerText || '';
        const valorTexto = colunas[2]?.innerText || 'R$ 0,00';
        
        let valor = parseFloat(valorTexto.replace('R$', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
        
        if (tipo.includes('Receita')) totalReceitas += valor;
        else if (tipo.includes('Despesa')) totalDespesas += valor;
    }
    
    const saldo = totalReceitas - totalDespesas;
    const formatar = (v) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    
    document.getElementById('totalReceitas').innerHTML = formatar(totalReceitas);
    document.getElementById('totalDespesas').innerHTML = formatar(totalDespesas);
    document.getElementById('totalSaldo').innerHTML = formatar(saldo);
}

// 🔥 MUDEI: removeu setTimeout, executa direto
const formFiltros = document.querySelector('.form-filtros-total');
if (formFiltros) {
    formFiltros.addEventListener('submit', () => {
        calcularTotaisFinancas();
    });
}

document.addEventListener('DOMContentLoaded', calcularTotaisFinancas);