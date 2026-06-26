// botoes_outros_filtros.js
document.addEventListener('htmx:afterRequest', function() {
    const mostrarInativas = document.getElementById('mostrar_inativas_input')?.value;
    
    if (!mostrarInativas) return;

    document.querySelectorAll('#botoes-transacao .btn-pure').forEach(btn => {
        btn.classList.remove('btn-active-toggle');
    });

    const botaoAtivo = document.querySelector(
        `#botoes-transacao button[hx-vals*='mostrar_inativas": "${mostrarInativas}"']`
    );
    botaoAtivo?.classList.add('btn-active-toggle');
});