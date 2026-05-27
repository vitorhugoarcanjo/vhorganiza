function excluirTransacao(id, descricao) {
    if (typeof window.abrirModal === 'undefined') {
        alert("Erro ao carregar modal. Recarregue a página.");
        return;
    }

    window.abrirModal({
        titulo: "Excluir Transação",
        texto: `Deseja inativar a transação: "${descricao}"?`,
        onConfirm: async () => {
            const response = await fetch(`/financas/excluir/${id}`, {
                method: "POST",
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                const linha = document.querySelector(`button[onclick*="excluirTransacao(${id},"]`).closest('tr');
                if (linha) linha.remove();
                
                const contador = document.querySelector('.badge-pure.bg-primary');
                if (contador) {
                    const qtdAtual = parseInt(contador.innerText);
                    contador.innerText = `${qtdAtual - 1} transações`;
                }
            } else {
                alert("Erro ao excluir transação");
            }
        }
    });
}