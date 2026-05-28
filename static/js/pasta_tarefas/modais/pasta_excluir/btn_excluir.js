document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.btn-excluir').forEach(btn => {

        btn.addEventListener('click', () => {

            const id = btn.dataset.id;
            const descricao = btn.dataset.desc;

            if (typeof window.abrirModal === 'undefined') {
                Notificacao.erro("Erro ao carregar modal.");
                return;
            }

            window.abrirModal({
                titulo: "Inativar Tarefa",
                texto: `Deseja inativar a tarefa: "${descricao}"?`,
                textoConfirmacao: "Sim, inativar",
                textoCancela: "Cancelar",

                onConfirm: async () => {
                    try {
                        const htmlOriginal = btn.innerHTML;

                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                        btn.innerHTML = '⏳';

                        const response = await fetch(`/tarefas/excluir/${id}`, {
                            method: "POST",
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });

                        const data = await response.json();

                        if (data.success) {

                            const linha = btn.closest('tr');

                            linha.style.transition = 'opacity 0.3s, transform 0.3s';
                            linha.style.opacity = '0';
                            linha.style.transform = 'translateX(50px)';

                            setTimeout(() => {
                                linha.remove();
                                atualizarContadorTarefas();
                            }, 300);

                            Notificacao.sucesso(data.message);

                        } else {
                            throw new Error(data.error);
                        }

                    } catch (error) {
                        Notificacao.erro(error.message || 'Erro ao inativar');

                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.innerHTML = '<i class="bi bi-trash"></i>';
                    }
                }
            });

        });

    });

});

function atualizarContadorTarefas() {
    const tabela = document.querySelector('.custom-table tbody');
    const linhas = tabela.querySelectorAll('tr:not(.text-center)');
    const contador = document.querySelector('.status-direita .badge-pure');

    if (contador) {
        const total = linhas.length;
        contador.textContent = total + ' tarefas';

        if (total === 0) {
            tabela.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4 text-white-50">
                        Nenhuma tarefa cadastrada ou nesse período
                    </td>
                </tr>
            `;
        }
    }
}