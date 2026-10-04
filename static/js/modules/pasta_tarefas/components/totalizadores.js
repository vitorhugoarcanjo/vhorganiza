// static/js/modules/pasta_tarefas/components/totalizadores.js
// ==========================================================
// Atualiza os contadores do footer após HTMX trocar a tabela
// ==========================================================

(function() {
    'use strict';

    function recalcularContadoresTarefas() {
        var tbody = document.querySelector('#tbody-tarefas');
        if (!tbody) return;

        var linhas = tbody.querySelectorAll('tr');
        var pendentes = 0;
        var andamento = 0;
        var concluidas = 0;

        linhas.forEach(function(tr) {
            // Ignora linha de "vazio"
            if (tr.querySelector('td[colspan]')) return;

            var badges = tr.querySelectorAll('.badge-pure');
            var statusTxt = '';

            badges.forEach(function(b) {
                var t = b.textContent.trim();
                if (t.indexOf('Concluída') !== -1) statusTxt = 'concluido';
                else if (t.indexOf('Andamento') !== -1) statusTxt = 'em andamento';
                else if (t.indexOf('Pendente') !== -1) statusTxt = 'pendente';
            });

            if (statusTxt === 'concluido')    concluidas++;
            else if (statusTxt === 'em andamento') andamento++;
            else if (statusTxt === 'pendente')     pendentes++;
        });

        var elP = document.getElementById('totalPendentes');
        var elA = document.getElementById('totalAndamento');
        var elC = document.getElementById('totalConcluidas');

        if (elP) elP.textContent = pendentes;
        if (elA) elA.textContent = andamento;
        if (elC) elC.textContent = concluidas;
    }

    // 🔥 HTMX troca a tabela → recalcula
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;

        if (target.id === 'tabela-container' ||
            target.id === 'tbody-tarefas' ||
            target.closest('#tabela-container')) {
            recalcularContadoresTarefas();
        }
    });

    console.log('✅ Totalizadores Tarefas carregados!');
})();