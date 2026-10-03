// static/js/modules/pasta_financas/components/botoes_outros_filtros.js
// ==========================================================
// Atualiza visual dos botões de filtro após HTMX
// ==========================================================

(function() {
    'use strict';

    function atualizarBotoesTransacao() {
        const input = document.getElementById('mostrar_inativas_input');
        if (!input) return;

        const valor = input.value;   // '0' | '1' | '2'
        if (!valor) return;

        // Remove active de todos (usa .btn-filter, não .btn-pure)
        document.querySelectorAll('#botoes-transacao .btn-filter').forEach(function(btn) {
            btn.classList.remove('btn-active-toggle');
        });

        // Encontra o botão ativo pelo atributo hx-vals
        const botaoAtivo = document.querySelector(
            '#botoes-transacao button[hx-vals*=\'mostrar_inativas": "' + valor + '"\']'
        );
        if (botaoAtivo) botaoAtivo.classList.add('btn-active-toggle');
    }

    // 🔥 Após HTMX substituir a tabela
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        const target = evt.detail.target;
        if (!target) return;

        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            setTimeout(atualizarBotoesTransacao, 0);
        }
    });

    // 🔥 Após qualquer request HTMX (fallback)
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.detail.target;
        if (!target) return;

        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            setTimeout(atualizarBotoesTransacao, 50);
        }
    });

    console.log('✅ botoes_outros_filtros carregado!');
})();