// ============================================
// TOTALIZADORES FINANCEIROS - VERSÃO HTMX
// ============================================

/**
 * Calcula os totais a partir da tabela visível
 */
function calcularTotaisFinancas() {
    const tbody = document.querySelector('.custom-table tbody');
    if (!tbody) return;
    
    const linhas = tbody.children;
    let totalReceitas = 0;
    let totalDespesas = 0;
    
    for (let linha of linhas) {
        // Pula linhas de agrupamento/mensagem (colspan)
        if (linha.querySelector('td[colspan]')) continue;
        
        const colunas = linha.cells;
        if (colunas.length < 3) continue;
        
        // Pega tipo (coluna 2? verifique seu índice real)
        const tipo = colunas[1]?.innerText || '';
        
        // Pega valor (coluna 3? ajuste conforme sua tabela)
        const valorTexto = colunas[2]?.innerText || 'R$ 0,00';
        
        const valor = parseFloat(
            valorTexto
                .replace('R$', '')
                .replace(/\./g, '')
                .replace(',', '.')
                .trim()
        ) || 0;
        
        if (tipo.includes('Receita')) {
            totalReceitas += valor;
        } else if (tipo.includes('Despesa')) {
            totalDespesas += valor;
        }
    }
    
    const saldo = totalReceitas - totalDespesas;
    const formatar = (v) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    
    // Atualiza os elementos (com verificação de existência)
    const elReceitas = document.getElementById('totalReceitas');
    const elDespesas = document.getElementById('totalDespesas');
    const elSaldo = document.getElementById('totalSaldo');
    
    if (elReceitas) elReceitas.innerHTML = formatar(totalReceitas);
    if (elDespesas) elDespesas.innerHTML = formatar(totalDespesas);
    if (elSaldo) elSaldo.innerHTML = formatar(saldo);
}

/**
 * Inicializa os listeners HTMX
 */
function initTotalizadoresHTMX() {
    // 1. Calcula na carga inicial
    calcularTotaisFinancas();
    
    // 2. Observa quando o HTMX troca o conteúdo da tabela
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Verifica se o swap foi no container da tabela
        if (event.target.id === 'tabela-container' || 
            event.target.closest('#tabela-container')) {
            calcularTotaisFinancas();
        }
    });
    
    // 3. Opcional: recalcula quando filtros são aplicados via POST
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const url = event.detail.pathInfo?.requestPath || '';
        if (url.includes('/financas/') || url.includes('ini_financas')) {
            // Pequeno delay pra garantir que o DOM atualizou
            setTimeout(calcularTotaisFinancas, 50);
        }
    });
}

// Inicializa apenas uma vez
if (!window._totalizadoresHTMXIniciado) {
    window._totalizadoresHTMXIniciado = true;
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTotalizadoresHTMX);
    } else {
        initTotalizadoresHTMX();
    }
}