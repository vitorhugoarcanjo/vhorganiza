let bloqueioExclusao = false;

function excluirTarefa(id, titulo) {

    if (bloqueioExclusao) return;

    abrirModal({
        titulo: "Excluir Tarefa",
        texto: `Deseja inativar: "${titulo}"?`,

        onConfirm: async () => {

            bloqueioExclusao = true;

            try {
                const res = await fetch(`/tarefas/excluir/${id}`, {
                    method: "POST"
                });

                if (!res.ok) throw new Error();

                location.reload();

            } catch (e) {
                alert("Erro ao excluir");
            } finally {
                bloqueioExclusao = false;
            }
        }
    });
}