async function atualizarTabela() {
    try {
        const response = await fetch('/financas/api/transacoes');
        const dados = await response.json();

        const tbody = document.querySelector('#tabela-financas tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        dados.forEach(item => {
            const tr = document.createElement('tr');

            const tipoLabel = item.tipo === 'receita'
                ? '<span class="badge-pure bg-success">📈 Receita</span>'
                : '<span class="badge-pure bg-warning text-dark">📉 Despesa</span>';

            tr.innerHTML = `
                <td class="td-id">${item.id}</td>
                <td>${tipoLabel}</td>
                <td class="td-titulo">${item.valor}</td>
                <td class="td-titulo" title="${item.descricao}">${item.descricao}</td>
                <td>${item.status_label}</td>
                <td>${item.categoria}</td>
                <td>${item.emissao}</td>
                <td>${item.vencimento}</td>
                <td class="td-acoes">
                    <button type="button" class="btn-acao view" onclick="verDetalhesTransacao(${item.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error('Erro ao atualizar tabela:', error);
    }
}