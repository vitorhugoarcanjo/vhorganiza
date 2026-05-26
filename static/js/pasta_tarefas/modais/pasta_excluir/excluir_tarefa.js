function excluirTarefa(id, titulo) {
    if (typeof window.abrirModal === 'undefined') {
        alert("Erro ao carregar modal. Recarregue a página.");
        return;
    }

    window.abrirModal({
        titulo: "Excluir Tarefa",
        texto: `Deseja inativar a tarefa: "${titulo}"?`,
        onConfirm: async () => {
            const response = await fetch(`/tarefas/excluir/${id}`, {
                method: "POST",
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                // Remove a linha da tabela sem recarregar a página
                const linha = document.querySelector(`button[onclick*="excluirTarefa(${id},"]`).closest('tr');
                if (linha) linha.remove();
                
                // Opcional: atualiza contador de tarefas
                const contador = document.querySelector('.badge-pure.bg-primary');
                if (contador) {
                    const qtdAtual = parseInt(contador.innerText);
                    contador.innerText = `${qtdAtual - 1} tarefas`;
                }
            } else {
                alert("Erro ao excluir tarefa");
            }
        }
    });
}