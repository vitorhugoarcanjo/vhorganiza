// 🔥 PROTEÇÃO ANTI-DUPLICIDADE
if (!window._reativarSistemaCarregado) {
    window._reativarSistemaCarregado = true;
    
    (function() {
        console.log('✅ Sistema de reativação carregado');
        
        let modalAberto = false;
        
        // Função GLOBAL para abrir o modal
        window.abrirModalReativar = function(config) {
            if (modalAberto) {
                console.log('⚠️ Modal já está aberto, ignorando...');
                return;
            }
            
            const modal = document.getElementById('modalReativar');
            const titulo = document.getElementById('modalReativarTitulo');
            const texto = document.getElementById('modalReativarTexto');
            const btnConfirmar = document.getElementById('btnConfirmarReativar');
            const btnCancelar = document.getElementById('btnCancelarReativar');
            
            if (!modal) {
                console.error('❌ Modal não encontrado');
                window.Notificacao?.erro('Modal de reativação não encontrado');
                return;
            }
            
            console.log('✅ Abrindo modal de reativação...');
            modalAberto = true;
            
            titulo.textContent = config.titulo;
            texto.textContent = config.texto;
            modal.classList.add('active');
            
            btnConfirmar.onclick = null;
            btnCancelar.onclick = null;
            modal.onclick = null;
            
            const fecharModal = () => {
                modal.classList.remove('active');
                modalAberto = false;
            };
            
            btnConfirmar.onclick = async function() {
                this.disabled = true;
                this.textContent = '⏳ Processando...';
                try {
                    await config.onConfirm(config.data);
                    fecharModal();
                } catch (error) {
                    console.error('Erro:', error);
                    window.Notificacao?.erro(error.message || 'Erro ao processar reativação');
                } finally {
                    this.disabled = false;
                    this.textContent = 'Confirmar Reativação';
                }
            };
            
            btnCancelar.onclick = fecharModal;
            
            modal.onclick = function(e) {
                if (e.target === modal) {
                    fecharModal();
                }
            };
        };
        
        // Função para reativar
        async function executarReativacao(id, btn, isParcelamento = false) {
            const url = isParcelamento ? `/financas/reativar_parcelamento/${id}` : `/financas/reativar/${id}`;
            
            btn.disabled = true;
            btn.style.opacity = '0.5';
            btn.innerHTML = '⏳';
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // 🔥 Se for parcelamento, recarrega a página (porque removeu várias linhas)
                    if (isParcelamento) {
                        window.Notificacao?.sucesso(result.message);
                        setTimeout(() => {
                            location.reload();  // Recarrega a página inteira
                        }, 1000);
                    } else {
                        // Transação simples: remove só a linha
                        const linha = btn.closest('tr');
                        if (linha) {
                            linha.style.transition = 'opacity 0.3s';
                            linha.style.opacity = '0';
                            setTimeout(() => {
                                linha.remove();
                                if (typeof calcularTotaisFinancas === 'function') {
                                    calcularTotaisFinancas();
                                }
                                window.Notificacao?.sucesso(result.message);
                            }, 300);
                        } else {
                            location.reload();
                        }
                    }
                } else {
                    throw new Error(result.error || 'Erro ao reativar');
                }
            } catch (error) {
                console.error('❌ Erro:', error);
                window.Notificacao?.erro(error.message);
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.innerHTML = '<i class="bi bi-arrow-repeat"></i>';
            }
        }
                
        // Delegação de eventos
        const botoesProcessando = new Set();
        
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-reativar');
            if (!btn) return;
            
            if (botoesProcessando.has(btn)) {
                console.log('⚠️ Este botão já está processando, ignorando...');
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            botoesProcessando.add(btn);
            
            const id = btn.dataset.id;
            const descricao = btn.dataset.desc;
            
            console.log('🔄 Reativar:', { id, descricao });
            
            // 🔥 USA A ROTA DE VERIFICAÇÃO (GET)
            fetch(`/financas/verificar_reativacao/${id}`, {
                method: 'GET',  // <-- GET, não POST!
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('📦 Resposta da verificação:', data);
                
                if (data.tipo === 'parcelamento') {
                    window.abrirModalReativar({
                        titulo: '⚠️ Reativar Parcelamento',
                        texto: `${data.mensagem}\n\n"${data.descricao}"`,
                        data: { id, btn, isParcelamento: true },
                        onConfirm: async (data) => {
                            await executarReativacao(data.id, data.btn, true);
                            botoesProcessando.delete(btn);
                        }
                    });
                } 
                else if (data.tipo === 'parcela') {
                    // Abre modal perguntando se quer reativar o parcelamento completo
                    window.abrirModalReativar({
                        titulo: '⚠️ Reativar Parcelamento Completo',
                        texto: `${data.mensagem}\n\n"${data.descricao}"\n\nIsso vai reativar TODAS as ${data.total_parcelas} parcelas.`,
                        data: { id: data.transacao_pai_id, btn, isParcelamento: true },  // Usa o ID do pai
                        onConfirm: async (data) => {
                            await executarReativacao(data.id, data.btn, true);
                            botoesProcessando.delete(btn);
                        }
                    });
                }
                else if (data.tipo === 'simples') {
                    window.abrirModalReativar({
                        titulo: '⚠️ Reativar Transação',
                        texto: `Deseja realmente REATIVAR a transação?\n\n"${descricao}"`,
                        data: { id, btn, isParcelamento: false },
                        onConfirm: async (data) => {
                            await executarReativacao(data.id, data.btn, false);
                            botoesProcessando.delete(btn);
                        }
                    });
                }
                else {
                    window.Notificacao?.erro?.(data.error || 'Erro ao verificar');
                    botoesProcessando.delete(btn);
                }
            })
            .catch(error => {
                console.error('❌ Erro na verificação:', error);
                window.Notificacao?.erro('Erro ao verificar transação');
                botoesProcessando.delete(btn);
            });
        });
        
    })();
}