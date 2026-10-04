// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_concluir/concluir_tarefa.js
// ==========================================================
// CONCLUIR — HTMX puro (com motivo)
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalConcluirTarefa = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalConcluirTarefa');
        const tituloEl = document.getElementById('concluirTitulo');
        const motivoEl = document.getElementById('motivoConclusao');

        // 🔥 Clona botão pra limpar listeners HTMX antigos
        let btnConfirmar = document.getElementById('btnConfirmarConcluirTarefa');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarConcluirTarefa');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de conclusão não encontrado');
            return;
        }

        modalAberto = true;
        if (tituloEl) tituloEl.textContent = 'Tarefa: ' + (config.titulo || '');
        if (motivoEl) motivoEl.value = '';
        modal.classList.add('active');

        // Configura hx-post dinamicamente
        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-tarefas');
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        // Passa o motivo como parâmetro do POST
        btnConfirmar.setAttribute('hx-include', '#motivoConclusao');

        if (window.htmx) window.htmx.process(btnConfirmar);

        const fecharModal = () => {
            modal.classList.remove('active');
            modalAberto = false;
        };

        btnCancelar.onclick = fecharModal;
        modal.onclick = function(e) {
            if (e.target === modal) fecharModal();
        };

        // Fecha se sucesso
        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            const status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) {
                fecharModal();
            }
            btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
        });
    };

    // ==========================================================
    // Delegação: clique no botão Concluir da linha
    // ==========================================================
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-concluir');
        if (!btn) return;

        e.preventDefault();

        modalAberto = false;

        const seq = btn.dataset.sequencia;
        const titulo = btn.dataset.titulo;

        window.abrirModalConcluirTarefa({
            titulo: titulo,
            url: '/tarefas/concluir_tarefa/' + seq
        });
    });

    // ==========================================================
    // Toast via HX-Trigger
    // ==========================================================
    document.body.addEventListener('tarefaConcluida', function() {
        modalAberto = false;
        const modal = document.getElementById('modalConcluirTarefa');
        if (modal) modal.classList.remove('active');

        if (window.Notificacao) window.Notificacao.sucesso('Tarefa concluída com sucesso!');
    });

    console.log('✅ Sistema de conclusão Tarefas (HTMX) carregado!');
})();