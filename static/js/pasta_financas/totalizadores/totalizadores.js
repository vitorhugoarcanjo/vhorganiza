function calcularTotaisFinancas() {
    const linhas = document.querySelectorAll('.custom-table tbody tr');
    let totalReceitas = 0;
    let totalDespesas = 0;
    
    linhas.forEach(linha => {
        // Pula a linha de "nenhuma transação"
        if (linha.querySelector('td[colspan]')) return;
        
        const colunas = linha.querySelectorAll('td');
        if (colunas.length < 3) return;
        
        // Coluna TIPO (índice 1) e VALOR (índice 2)
        const tipo = colunas[1]?.innerText || '';
        const valorTexto = colunas[2]?.innerText || 'R$ 0,00';
        
        // Remove "R$" e converte
        let valor = parseFloat(valorTexto.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());
        if (isNaN(valor)) valor = 0;
        
        if (tipo.includes('Receita')) {
            totalReceitas += valor;
        } else if (tipo.includes('Despesa')) {
            totalDespesas += valor;
        }
    });
    
    const saldo = totalReceitas - totalDespesas;
    
    document.getElementById('totalReceitas').innerHTML = `R$ ${totalReceitas.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('totalDespesas').innerHTML = `R$ ${totalDespesas.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('totalSaldo').innerHTML = `R$ ${saldo.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Executa quando a página carregar
document.addEventListener('DOMContentLoaded', calcularTotaisFinancas);

// Recalcula após consulta (filtros via POST)
const formFiltros = document.querySelector('.form-filtros-total');
if (formFiltros) {
    formFiltros.addEventListener('submit', function() {
        setTimeout(calcularTotaisFinancas, 300);
    });
}
