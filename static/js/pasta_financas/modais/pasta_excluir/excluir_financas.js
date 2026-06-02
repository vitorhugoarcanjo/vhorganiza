// Sistema de Exclusão de Finanças - UNIFICADO
(function() {
    // ===== PARTE 1: CONFIGURA O MODAL =====
    function initModal() {
        const modal = document.getElementById("modalExcluirFinancas");
        if (!modal) return;
        
        if (!window.abrirModalExcluirFinancas) {
            window.abrirModalExcluirFinancas = function({ titulo, texto, onConfirm }) {
                const modalEl = document.getElementById("modalExcluirFinancas");
                const btnCancelar = document.getElementById("btnCancelarExcluirFinancas");
                const btnConfirmar = document.getElementById("btnConfirmarExcluirFinancas");
                const tituloEl = document.getElementById("modalExcluirTitulo");
                const textoEl = document.getElementById("modalExcluirTexto");

                if (!modalEl || !btnCancelar || !btnConfirmar) {
                    console.error('❌ Elementos do modal não encontrados');
                    window.Notificacao?.erro('Erro ao carregar modal de exclusão');
                    return;
                }

                tituloEl.textContent = titulo;
                textoEl.textContent = texto;

                modalEl.classList.add('active');

                // Limpa eventos antigos
                btnConfirmar.onclick = null;
                btnCancelar.onclick = null;
                modalEl.onclick = null;

                let bloqueio = false;

                btnConfirmar.onclick = async () => {
                    if (bloqueio) return;
                    bloqueio = true;
                    
                    const originalText = btnConfirmar.innerText;
                    btnConfirmar.innerText = "Processando...";

                    try {
                        if (onConfirm) await onConfirm();
                        modalEl.classList.remove('active');
                    } catch (error) {
                        window.Notificacao?.erro(error.message || 'Erro ao processar');
                    } finally {
                        btnConfirmar.innerText = originalText;
                        bloqueio = false;
                    }
                };

                btnCancelar.onclick = () => {
                    modalEl.classList.remove('active');
                };

                modalEl.onclick = (e) => {
                    if (e.target === modalEl) modalEl.classList.remove('active');
                };
            };
        }
    }
    
    // ===== PARTE 2: CONFIGURA OS BOTÕES =====
    function initBotoes() {
        document.querySelectorAll('.btn-excluir').forEach(btn => {
            btn.onclick = null;
            btn.addEventListener('click', handleExcluirClick);
        });
    }
    
    function handleExcluirClick(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;

        if (typeof window.abrirModalExcluirFinancas === 'undefined') {
            console.error('❌ Modal não carregado');
            window.Notificacao?.erro('Erro ao carregar modal de exclusão');
            return;
        }

        window.abrirModalExcluirFinancas({
            titulo: "Inativar Transação",
            texto: `Deseja inativar a transação: "${descricao}"?`,
            
            onConfirm: async () => {
                try {
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
                            if (typeof calcularTotaisFinancas === 'function') {
                                calcularTotaisFinancas();
                            }
                        }, 300);

                        window.Notificacao?.sucesso(data.message || 'Transação inativada com sucesso!');

                    } else {
                        throw new Error(data.error);
                    }

                } catch (error) {
                    window.Notificacao?.erro(error.message || 'Erro ao inativar');
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.innerHTML = '<i class="bi bi-trash"></i>';
                }
            }
        });
    }
    
    // ===== INICIALIZA =====
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initModal();
            initBotoes();
        });
    } else {
        initModal();
        initBotoes();
    }
})();