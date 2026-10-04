// static/js/modules/pasta_tarefas/modals/tarefa-nova.js
// ==========================================================
// MODAL NOVA TAREFA - HTMX injeta, JS inicializa
// ==========================================================

(function() {
    'use strict';

    var formInstance = null;

    function instanciar() {
        var formEl = document.getElementById('formNovaTarefa');
        if (!formEl) return null;
        if (formInstance && formInstance.form === formEl) return formInstance;

        formInstance = new window.TarefaForm(formEl, {
            mode: 'create',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message || 'Tarefa salva!');
                fecharModalNovaTarefa();

                // Recarrega tabela via HTMX
                if (window.recarregarTabelaTarefas) {
                    window.recarregarTabelaTarefas();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/tarefas', { target: '#tabela-container', swap: 'outerHTML' });
                }
            }
        });
        return formInstance;
    }

    function fecharModalNovaTarefa() {
        var container = document.getElementById('modal-nova-container');
        if (container) container.innerHTML = '';
        document.body.style.overflow = '';
        formInstance = null;
    }

    function salvarNovaTarefa() {
        var f = instanciar();
        if (!f) return;

        var btn = document.querySelector('#footerFixoNova .btn-footer-primary');
        if (btn) {
            btn.disabled = true;
            btn.dataset.txt = btn.innerHTML;
            btn.innerHTML = 'Salvando...';
        }

        f.submit('/tarefas/nova_tarefa/salvar')
         .catch(function() { /* já notificado */ })
         .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.txt || 'SALVAR';
            }
         });
    }

    // ==========================================================
    // HTMX injeta o modal → inicializa o form
    // ==========================================================
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;
        if (target.id !== 'modal-nova-container') return;

        var formEl = document.getElementById('formNovaTarefa');
        if (!formEl) return;

        // Foca no título
        setTimeout(function() {
            var titulo = formEl.querySelector('.js-titulo');
            if (titulo) titulo.focus();
        }, 100);

        // Instancia o form
        instanciar();
        document.body.style.overflow = 'hidden';

        console.log('🔁 HTMX injetou modal NOVA TAREFA');
    });

    // Escape fecha
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalNovaTarefa');
            if (modal && modal.offsetParent !== null) fecharModalNovaTarefa();
        }
    });

    // Clique fora fecha
    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaTarefa');
        if (modal && e.target === modal) fecharModalNovaTarefa();
    });

    // Exposição global
    window.fecharModalNovaTarefa = fecharModalNovaTarefa;
    window.salvarNovaTarefa = salvarNovaTarefa;

    console.log('✅ MODAL NOVA TAREFA carregado!');
})();