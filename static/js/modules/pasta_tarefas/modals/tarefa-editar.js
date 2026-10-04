// static/js/modules/pasta_tarefas/modals/tarefa-editar.js
// ==========================================================
// MODAL EDITAR TAREFA - HTMX injeta, JS popula via /dados/
// ==========================================================

(function() {
    'use strict';

    var sequenciaAtual = null;
    var formInstance = null;

    function instanciar(formEl) {
        if (!formEl) return null;
        if (formInstance && formInstance.form === formEl) return formInstance;

        formInstance = new window.TarefaForm(formEl, {
            mode: 'edit',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message || 'Tarefa atualizada!');
                fecharModalEditarTarefa();

                if (window.recarregarTabelaTarefas) {
                    window.recarregarTabelaTarefas();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/tarefas', { target: '#tabela-container', swap: 'outerHTML' });
                }
            }
        });
        return formInstance;
    }

    function abrirModalEditarTarefa(seq) {
        sequenciaAtual = seq;

        var modal = document.getElementById('modalEditarTarefa');
        var formEl = document.getElementById('formEditarTarefa');
        if (!modal || !formEl) return;

        if (!sequenciaAtual) {
            if (window.Notificacao) window.Notificacao.erro('Sequência da tarefa não identificada.');
            return;
        }

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Spinner
        var body = modal.querySelector('.fin-modal-body');
        var loading = null;
        if (body) {
            loading = document.createElement('div');
            loading.id = 'editLoadingOverlay';
            loading.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;justify-content:center;align-items:center;flex-direction:column;z-index:10;border-radius:8px;';
            loading.innerHTML = '<div style="width:40px;height:40px;border:4px solid #fff;border-top-color:#2563eb;border-radius:50%;animation:spin 0.8s linear infinite;"></div><p style="color:#fff;margin-top:10px;">Carregando dados...</p>';
            body.style.position = 'relative';
            body.appendChild(loading);
        }

        fetch('/tarefas/edit_tarefas/dados/' + sequenciaAtual, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function(resposta) {
            if (loading) loading.remove();
            var data = resposta.data || resposta;

            // Atualiza título do modal
            var tituloEl = modal.querySelector('#finEditarSequencia');
            if (tituloEl && data.sequencia) {
                tituloEl.textContent = 'Editar Tarefa #' + data.sequencia;
            }
            if (formEl && data.sequencia) {
                formEl.dataset.tarefaSequencia = data.sequencia;
            }

            var f = instanciar(formEl);
            if (f) f.setData(data);
        })
        .catch(function(error) {
            console.error('❌ Erro no GET dados:', error);
            if (loading) loading.remove();
            if (body) body.innerHTML = '<div style="color:#ef4444;padding:20px;">Erro ao carregar dados</div>';
        });
    }

    function fecharModalEditarTarefa() {
        var container = document.getElementById('modal-editar-container');
        if (container) container.innerHTML = '';
        document.body.style.overflow = '';
        formInstance = null;
        sequenciaAtual = null;
    }

    function salvarEditarTarefa() {
        var formEl = document.getElementById('formEditarTarefa');
        sequenciaAtual = (formEl && formEl.dataset.tarefaSequencia) || sequenciaAtual;

        if (!sequenciaAtual || sequenciaAtual === 'None') {
            if (window.Notificacao) window.Notificacao.erro('Sequência da tarefa não identificada.');
            return;
        }

        var f = instanciar(formEl);
        if (!f) return;

        var btn = document.querySelector('#footerFixoEditar .btn-footer-primary');
        if (btn) {
            btn.disabled = true;
            btn.dataset.txt = btn.innerHTML;
            btn.innerHTML = 'Salvando...';
        }

        f.submit('/tarefas/edit_tarefas/' + sequenciaAtual)
         .catch(function() { /* já notificado */ })
         .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.txt || 'ATUALIZAR';
            }
         });
    }

    // ==========================================================
    // HTMX injeta o modal → popula
    // ==========================================================
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;
        if (target.id !== 'modal-editar-container') return;

        var formEl = document.getElementById('formEditarTarefa');
        if (!formEl) return;

        var seq = formEl.dataset.tarefaSequencia;
        if (!seq || seq === 'None') {
            console.warn('⚠️ HTMX injetou modal de editar sem data-tarefa-sequencia');
            return;
        }

        console.log('🔁 HTMX injetou modal EDITAR TAREFA, populando via /dados/' + seq);
        abrirModalEditarTarefa(seq);
    });

    // Escape / clique fora
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalEditarTarefa');
            if (modal && modal.offsetParent !== null) fecharModalEditarTarefa();
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalEditarTarefa');
        if (modal && e.target === modal) fecharModalEditarTarefa();
    });

    // Exposição global
    window.abrirModalEditarTarefa = abrirModalEditarTarefa;
    window.fecharModalEditarTarefa = fecharModalEditarTarefa;
    window.salvarEditarTarefa = salvarEditarTarefa;

    console.log('✅ MODAL EDITAR TAREFA carregado!');
})();