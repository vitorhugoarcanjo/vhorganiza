// static/js/modules/pasta_financas/components/botoes_outros_filtros.js
// ==========================================================
// Atualiza visual dos botões de filtro após HTMX
// ==========================================================

(function() {
    'use strict';

    function atualizarBotoesTransacao() {
        const input = document.getElementById('mostrar_inativas_input');
        if (!input) return;

        const valor = input.value;
        if (!valor) return;

        document.querySelectorAll('#botoes-transacao .btn-filter').forEach(function(btn) {
            btn.classList.remove('btn-active-toggle');
        });

        const botaoAtivo = document.querySelector(
            '#botoes-transacao button[hx-vals*=\'mostrar_inativas": "' + valor + '"\']'
        );
        if (botaoAtivo) botaoAtivo.classList.add('btn-active-toggle');
    }

    // 🔥 afterSwap (DOM pronto, sem setTimeout)
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        const target = evt.detail.target;
        if (!target) return;

        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            atualizarBotoesTransacao();
        }
    });

    console.log('✅ botoes_outros_filtros carregado!');
})();