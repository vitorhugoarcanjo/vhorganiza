// static/js/components/botoes_filtros.js
// ==========================================================
// ATUALIZA VISUAL DOS BOTÕES DE FILTRO (Ativos/Inativos/Todos)
// após HTMX trocar a tabela
// ==========================================================
// 🔥 COMPARTILHADO — funciona pra Finanças, Tarefas e Orçamentos
// ==========================================================

(function() {
    'use strict';

    function atualizarBotoesFiltro() {
        var input = document.getElementById('mostrar_inativas_input');
        if (!input) return;

        var valor = input.value;
        if (!valor) return;

        // Remove destaque de TODOS os botões .btn-filter da página
        document.querySelectorAll('.btn-filter').forEach(function(btn) {
            btn.classList.remove('btn-active-toggle');
        });

        // Marca como ativo o botão que bate com o valor atual
        // Procura em qualquer wrapper (botoes-orcamento, botoes-transacao, etc)
        var botaoAtivo = document.querySelector(
            '.btn-filter[hx-vals*=\'mostrar_inativas": "' + valor + '"\']'
        );
        if (botaoAtivo) {
            botaoAtivo.classList.add('btn-active-toggle');
        }
    }

    // HTMX troca a tabela → atualiza botões
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;

        // Se o swap foi na tabela OU no input hidden
        if (target.id === 'tabela-container' ||
            target.id === 'mostrar_inativas_input' ||
            target.closest('#tabela-container')) {
            atualizarBotoesFiltro();
        }
    });

    console.log('✅ Botoes filtros (compartilhado) carregado!');
})();