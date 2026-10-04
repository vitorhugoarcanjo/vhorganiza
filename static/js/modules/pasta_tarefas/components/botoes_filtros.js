// static/js/modules/pasta_tarefas/components/botoes_filtros.js
// ==========================================================
// Atualiza o visual dos botões de filtro (Ativas/Inativas/Todas)
// após HTMX trocar a tabela
// ==========================================================

(function() {
    'use strict';

    function atualizarBotoesTarefas() {
        var input = document.getElementById('mostrar_inativas_input');
        if (!input) return;

        var valor = input.value;
        if (!valor) return;

        document.querySelectorAll('#botoes-transacao .btn-filter').forEach(function(btn) {
            btn.classList.remove('btn-active-toggle');
        });

        var botaoAtivo = document.querySelector(
            '#botoes-transacao button[hx-vals*=\'mostrar_inativas": "' + valor + '"\']'
        );
        if (botaoAtivo) botaoAtivo.classList.add('btn-active-toggle');
    }

    // HTMX troca a tabela → atualiza botões
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;

        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            atualizarBotoesTarefas();
        }
    });

    console.log('✅ Botoes filtros Tarefas carregado!');
})();