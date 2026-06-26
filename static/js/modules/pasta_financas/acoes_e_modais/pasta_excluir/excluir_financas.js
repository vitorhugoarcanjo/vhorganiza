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
                    if (window.Notificacao) window.Notificacao.erro('Erro ao carregar modal de exclusão');
                    return;
                }

                tituloEl.textContent = titulo;
                textoEl.textContent = texto;

                modalEl.classList.add('active');

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
                        if (error.message !== 'parcela_detectada') {
                            if (window.Notificacao) window.Notificacao.erro(error.message || 'Erro ao processar');
                        }
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
    
    async function handleExcluirClick(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;

        if (typeof window.abrirModalExcluirFinancas === 'undefined') {
            console.error('❌ Modal não carregado');
            if (window.Notificacao) window.Notificacao.erro('Erro ao carregar modal de exclusão');
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
                        method: "DELETE",
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        const linha = btn.closest('tr');
                        if (linha) {
                            linha.style.transition = 'opacity 0.3s, transform 0.3s';
                            linha.style.opacity = '0';
                            linha.style.transform = 'translateX(50px)';

                            setTimeout(() => {
                                linha.remove();
                                if (typeof calcularTotaisFinancas === 'function') {
                                    calcularTotaisFinancas();
                                }
                            }, 300);
                        }

                        if (window.Notificacao) window.Notificacao.sucesso(data.message || 'Transação inativada com sucesso!');

                    } else {
                        // CASO: É uma parcela
                        if (data.tipo_parcelamento === 'parcela') {
                            // Restaura o botão original
                            btn.disabled = false;
                            btn.style.opacity = '1';
                            btn.innerHTML = '<i class="bi bi-trash"></i>';
                            
                            // Fecha o modal atual
                            const modalEl = document.getElementById("modalExcluirFinancas");
                            if (modalEl) modalEl.classList.remove('active');
                            
                            // Limpa pendente anterior
                            window.parcelamentoPendente = null;
                            
                            // Delay para garantir que o modal anterior fechou
                            setTimeout(() => {
                                // Abre NOVO modal perguntando sobre inativar todas as parcelas
                                window.abrirModalExcluirFinancas({
                                    titulo: "⚠️ Atenção! Parcelamento Detectado",
                                    texto: `${data.mensagem}\n\nDeseja inativar TODAS as parcelas deste parcelamento?`,
                                    onConfirm: async () => {
                                        // Desabilita o botão original novamente
                                        btn.disabled = true;
                                        btn.style.opacity = '0.5';
                                        btn.innerHTML = '⏳';
                                        
                                        await excluirParcelamentoCompleto(data.transacao_pai_id, btn);
                                    }
                                });
                            }, 200);
                            
                            // Interrompe o fluxo do onConfirm
                            throw new Error('parcela_detectada');
                        }
                        
                        // CASO: É transação principal com parcelas
                        if (data.tipo_parcelamento === 'transacao_com_parcelas') {
                            // Restaura o botão original
                            btn.disabled = false;
                            btn.style.opacity = '1';
                            btn.innerHTML = '<i class="bi bi-trash"></i>';
                            
                            // Fecha o modal atual
                            const modalEl = document.getElementById("modalExcluirFinancas");
                            if (modalEl) modalEl.classList.remove('active');
                            
                            setTimeout(() => {
                                window.abrirModalExcluirFinancas({
                                    titulo: "⚠️ Atenção! Transação com Parcelas",
                                    texto: `${data.mensagem}\n\nDeseja inativar TODAS as parcelas?`,
                                    onConfirm: async () => {
                                        btn.disabled = true;
                                        btn.style.opacity = '0.5';
                                        btn.innerHTML = '⏳';
                                        await excluirParcelamentoCompleto(data.transacao_id, btn);
                                    }
                                });
                            }, 200);
                            
                            throw new Error('parcela_detectada');
                        }
                        
                        throw new Error(data.error);
                    }

                } catch (error) {
                    if (error.message !== 'parcela_detectada') {
                        if (window.Notificacao) window.Notificacao.erro(error.message || 'Erro ao inativar');
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.innerHTML = '<i class="bi bi-trash"></i>';
                    }
                }
            }
        });
    }
    
    // FUNÇÃO PARA EXCLUIR PARCELAMENTO COMPLETO
    async function excluirParcelamentoCompleto(transacaoPaiId, btnOriginal) {
        try {
            const response = await fetch(`/financas/excluir_parcelamento/${transacaoPaiId}`, {
                method: "DELETE",
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (window.Notificacao) window.Notificacao.sucesso(data.message || 'Parcelamento inativado com sucesso!');
                setTimeout(() => {
                    location.reload();
                }, 500);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            if (window.Notificacao) window.Notificacao.erro(error.message || 'Erro ao inativar parcelamento');
            if (btnOriginal) {
                btnOriginal.disabled = false;
                btnOriginal.style.opacity = '1';
                btnOriginal.innerHTML = '<i class="bi bi-trash"></i>';
            }
        }
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