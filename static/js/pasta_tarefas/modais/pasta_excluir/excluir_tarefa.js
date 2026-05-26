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
            if (response.ok) location.reload();
            else alert("Erro ao excluir tarefa");
        }
    });
}