// Botões de estornar
document.addEventListener('DOMContentLoaded', () => {
    
    function inicializarBotoes() {
        const botoes = document.querySelectorAll('.btn-estornar');
        console.log('Botões de estornar encontrados:', botoes.length);
        
        botoes.forEach(btn => {
            btn.removeEventListener('click', handleEstornarClick);
            btn.addEventListener('click', handleEstornarClick);
        });
    }
    
    async function handleEstornarClick(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        
        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;
        const tipo = btn.dataset.tipo;
        const tipoTexto = tipo === 'despesa' ? 'DESPESA' : 'RECEITA';
        
        console.log('Estornar clicado:', { id, descricao, tipo });
        
        if (typeof window.abrirModalEstornar === 'undefined') {
            console.error('Modal não disponível');
            alert('Erro: Sistema de estorno não carregado. Recarregue a página.');
            return;
        }
        
        window.abrirModalEstornar({
            titulo: `⚠️ Estornar ${tipoTexto}`,
            texto: `Deseja realmente ESTORNAR a transação?\n\n"${descricao}"\n\nEla voltará para o status ABERTO.`,
            data: { id, btn, descricao, tipo },
            
            onConfirm: async (data) => {
                const { id, btn } = data;
                
                try {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                    btn.innerHTML = '⏳';
                    
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
                            setTimeout(() => linha.remove(), 300);
                        }
                        
                        alert('✅ ' + (result.message || 'Transação estornada!'));
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        throw new Error(result.error || 'Erro ao estornar');
                    }
                } catch (error) {
                    console.error('Erro:', error);
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.innerHTML = '<i class="bi bi-arrow-return-left"></i>';
                    alert('❌ ' + error.message);
                }
            }
        });
    }
    
    inicializarBotoes();
})();