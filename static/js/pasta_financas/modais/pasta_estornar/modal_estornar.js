// 🔥 PROTEÇÃO ANTI-DUPLICIDADE
if (!window._estornoSistemaCarregado) {
    window._estornoSistemaCarregado = true;
    
    (function() {
        console.log('✅ Sistema de estorno carregado');
        
        let modalAberto = false;
        
        // Função GLOBAL para abrir o modal
        window.abrirModalEstornar = function(config) {
            if (modalAberto) {
                console.log('⚠️ Modal já está aberto, ignorando...');
                return;
            }
            
            const modal = document.getElementById('modalEstornar');
            const titulo = document.getElementById('modalEstornarTitulo');
            const texto = document.getElementById('modalEstornarTexto');
            const btnConfirmar = document.getElementById('btnConfirmarEstornar');
            const btnCancelar = document.getElementById('btnCancelarEstornar');
            
            if (!modal) {
                console.error('❌ Modal não encontrado');
                window.Notificacao?.erro('Modal de estorno não encontrado');
                return;
            }
            
            console.log('✅ Abrindo modal de estorno...');
            modalAberto = true;
            
            // Configura textos
            titulo.textContent = config.titulo;
            texto.textContent = config.texto;
            
            // 🔥 USA CLASSE CSS
            modal.classList.add('active');
            
            // Remove eventos antigos
            btnConfirmar.onclick = null;
            btnCancelar.onclick = null;
            modal.onclick = null;
            
            // Função para fechar
            const fecharModal = () => {
                modal.classList.remove('active');
                modalAberto = false;
            };
            
            // Configura botão confirmar
            btnConfirmar.onclick = async function() {
                this.disabled = true;
                this.textContent = '⏳ Processando...';
                try {
                    await config.onConfirm(config.data);
                    fecharModal();
                } catch (error) {
                    console.error('Erro:', error);
                    window.Notificacao?.erro(error.message || 'Erro ao processar estorno');
                } finally {
                    this.disabled = false;
                    this.textContent = 'Confirmar Estorno';
                }
            };
            
            // Configura botão cancelar
            btnCancelar.onclick = fecharModal;
            
            // Fecha ao clicar fora
            modal.onclick = function(e) {
                if (e.target === modal) {
                    fecharModal();
                }
            };
        };
        
        // 🔥 Delegação de eventos - SÓ BLOQUEIA O MESMO BOTÃO
        const botoesProcessando = new Set();
        
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-estornar');
            if (!btn) return;
            
            // 🔥 Se ESTE botão específico já está processando, ignora
            if (botoesProcessando.has(btn)) {
                console.log('⚠️ Este botão já está processando, ignorando...');
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            // Marca este botão como "processando"
            botoesProcessando.add(btn);
            
            const id = btn.dataset.id;
            const descricao = btn.dataset.desc;
            const tipo = btn.dataset.tipo;
            const tipoTexto = tipo === 'despesa' ? 'DESPESA' : 'RECEITA';
            
            console.log('🔄 Estornar:', { id, descricao, tipo });
            
            window.abrirModalEstornar({
                titulo: `⚠️ Estornar ${tipoTexto}`,
                texto: `Deseja realmente ESTORNAR a transação?\n\n"${descricao}"\n\nEla voltará para o status ABERTO.`,
                data: { id, btn, descricao, tipo },
                
                onConfirm: async (data) => {
                    const { id, btn } = data;
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                    btn.innerHTML = '⏳';
                    
                    try {
                        const response = await fetch(`/estornar_transacao/${id}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            const linha = btn.closest('tr');
                            if (linha) {
                                linha.style.transition = 'opacity 0.3s';
                                linha.style.opacity = '0';
                                setTimeout(() => {
                                    linha.remove();
                                    if (typeof calcularTotaisFinancas === 'function') {
                                        calcularTotaisFinancas();
                                    }
                                }, 300);
                            }
                            window.Notificacao?.sucesso(result.message || 'Transação estornada com sucesso!');
                        } else {
                            throw new Error(result.error || 'Erro ao estornar');
                        }
                    } catch (error) {
                        console.error('❌ Erro:', error);
                        window.Notificacao?.erro(error.message || 'Erro ao estornar');
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.innerHTML = '<i class="bi bi-arrow-return-left"></i>';
                    } finally {
                        // 🔥 Libera ESTE botão específico
                        botoesProcessando.delete(btn);
                    }
                }
            });
            
            // Se o modal for fechado sem confirmar, libera o botão
            const observer = new MutationObserver(() => {
                const modal = document.getElementById('modalEstornar');
                if (modal && !modal.classList.contains('active')) {
                    botoesProcessando.delete(btn);
                    observer.disconnect();
                }
            });
            
            const modal = document.getElementById('modalEstornar');
            if (modal) {
                observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
            }
        });
        
    })();
}