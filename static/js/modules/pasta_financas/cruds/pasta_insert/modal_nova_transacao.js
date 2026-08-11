// ==========================================
// MODAL: NOVA TRANSAÇÃO (CSS PURO)
// ==========================================

function abrirModalNovaTransacao() {
    const modal = document.getElementById('modalNovaTransacao');
    
    // Mostra o modal
    modal.style.display = 'flex';
    modal.classList.add('active');
    
    // Trava o scroll da página
    document.body.style.overflow = 'hidden';
}

function fecharModalNovaTransacao() {
    const modal = document.getElementById('modalNovaTransacao');
    
    // Esconde o modal
    modal.style.display = 'none';
    modal.classList.remove('active');
    
    // Libera o scroll
    document.body.style.overflow = '';
}

// 🔥 Fechar ao clicar no fundo escuro (overlay)
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalNovaTransacao');
    
    modal.addEventListener('click', function(event) {
        // Só fecha se clicou no overlay (fundo escuro)
        if (event.target === this) {
            fecharModalNovaTransacao();
        }
    });
});

// 🔥 Versão com verificação extra
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('modalNovaTransacao');
        // Verifica se está visível E ativo
        if (modal.style.display === 'flex' && modal.classList.contains('active')) {
            fecharModalNovaTransacao();
        }
    }
});