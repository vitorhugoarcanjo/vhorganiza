// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_reabrir/reabrir_tarefa.js
// ==========================================================
// REABRIR TAREFA — HTMX puro (modal dedicado)
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    window.abrirModalReabrirTarefa = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalReabrirTarefa');
        const titulo = document.getElementById('modalReabrirTitulo');
        const texto = document.getElementById('modalReabrirTexto');

        let btnConfirmar = document.getElementById('btnConfirmarReabrirTarefa');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarReabrirTarefa');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de reabrir não encontrado');
            return;
        }

        modalAberto = true;
        if (titulo) titulo.textContent = config.titulo;
        if (texto) texto.textContent = config.texto;
        modal.classList.add('active');

        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-tarefas');
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        if (window.htmx) window.htmx.process(btnConfirmar);

        const fecharModal = () => {
            modal.classList.remove('active');
            modalAberto = false;
        };

        btnCancelar.onclick = fecharModal;
        modal.onclick = function(e) {
            if (e.target === modal) fecharModal();
        };

        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            const status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) fecharModal();
            btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
        });
    };

    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-reabrir');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        window.abrirModalReabrirTarefa({
            titulo: '↩️ Reabrir Tarefa',
            texto: 'Deseja reabrir a tarefa "' + btn.dataset.titulo + '"?\n\nEla voltará para o status "pendente".',
            url: '/tarefas/reabrir_tarefa/' + btn.dataset.sequencia
        });
    });

    document.body.addEventListener('tarefaReaberta', function(evt) {
        modalAberto = false;
        const modal = document.getElementById('modalReabrirTarefa');
        if (modal) modal.classList.remove('active');

        const msg = evt.detail && evt.detail.message ? evt.detail.message : 'Tarefa reaberta!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de reabrir Tarefas (HTMX) carregado!');
})();