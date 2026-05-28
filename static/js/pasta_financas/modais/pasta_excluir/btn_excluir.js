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
                titulo: "Inativar Transação",
                texto: `Deseja inativar a transação: "${descricao}"?`,
                textoConfirmacao: "Sim, inativar",
                textoCancela: "Cancelar",

                onConfirm: async () => {
                    try {
                        const htmlOriginal = btn.innerHTML;

                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                        btn.innerHTML = '⏳';

                        const response = await fetch(`/financas/excluir/${id}`, {
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
                                atualizarContadorFinancas();
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