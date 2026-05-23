function abrirModalConcluir(botao) {
    const urlCorreta = botao.getAttribute('data-url');
    const form = document.getElementById('formConcluir');
    const overlay = document.getElementById('modalConcluir');

    form.action = urlCorreta;
    
    // Adiciona a classe active para animar
    overlay.classList.add('active');
}

function fecharModalConcluir() {
    const overlay = document.getElementById('modalConcluir');
    // Remove a classe para esconder
    overlay.classList.remove('active');
}

// Fechar se clicar fora da caixa branca
window.onclick = function(event) {
    const overlay = document.getElementById('modalConcluir');
    if (event.target == overlay) {
        fecharModalConcluir();
    }
}