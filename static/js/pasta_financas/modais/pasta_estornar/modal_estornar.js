// Estornar transações - Versão completa e simplificada
(function() {
    console.log('Inicializando sistema de estorno...');
    
    // Função para estornar
    window.estornarTransacao = async function(id, descricao, tipo, buttonElement) {
        const tipoTexto = tipo === 'despesa' ? 'DESPESA' : 'RECEITA';
        
        // Usa confirm do navegador mesmo (mais simples)
        const confirmado = confirm(`⚠️ ESTORNAR ${tipoTexto}?\n\n"${descricao}"\n\nDeseja realmente estornar? Ela voltará para ABERTO.`);
        
        if (!confirmado) return;
        
        try {
            // Desabilita o botão
            buttonElement.disabled = true;
            buttonElement.style.opacity = '0.5';
            buttonElement.innerHTML = '⏳';
            
            // Faz a requisição
            const response = await fetch(`/estornar_transacao/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('✅ ' + result.message);
                location.reload();
            } else {
                throw new Error(result.error || 'Erro ao estornar');
            }
        } catch (error) {
            console.error('Erro no estorno:', error);
            alert('❌ ' + error.message);
            buttonElement.disabled = false;
            buttonElement.style.opacity = '1';
            buttonElement.innerHTML = '<i class="bi bi-arrow-return-left"></i>';
        }
    };
    
    // Aguarda o DOM carregar e adiciona os eventos
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', adicionarEventos);
    } else {
        adicionarEventos();
    }
    
    function adicionarEventos() {
        console.log('Procurando botões de estornar...');
        const botoes = document.querySelectorAll('.btn-estornar');
        console.log('Botões encontrados:', botoes.length);
        
        botoes.forEach(btn => {
            // Remove evento antigo se existir
            const novoBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(novoBtn, btn);
            
            // Adiciona evento novo
            novoBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const id = this.dataset.id;
                const descricao = this.dataset.desc;
                const tipo = this.dataset.tipo;
                window.estornarTransacao(id, descricao, tipo, this);
            });
        });
    }
})();