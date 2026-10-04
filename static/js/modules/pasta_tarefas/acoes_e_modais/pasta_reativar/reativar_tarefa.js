// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_reativar/reativar_tarefa.js
// ==========================================================
// REATIVAR TAREFA — HTMX puro (modal dedicado)
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    window.abrirModalReativarTarefa = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalReativarTarefa');
        const titulo = document.getElementById('modalReativarTitulo');
        const texto = document.getElementById('modalReativarTexto');

        let btnConfirmar = document.getElementById('btnConfirmarReativarTarefa');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarReativarTarefa');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de reativar não encontrado');
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
        const btn = e.target.closest('.btn-reativar');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        window.abrirModalReativarTarefa({
            titulo: '🔄 Reativar Tarefa',
            texto: 'Deseja reativar a tarefa "' + btn.dataset.titulo + '"?',
            url: '/tarefas/reativar_tarefa/' + btn.dataset.sequencia
        });
    });

    document.body.addEventListener('tarefaReativada', function(evt) {
        modalAberto = false;
        const modal = document.getElementById('modalReativarTarefa');
        if (modal) modal.classList.remove('active');

        const msg = evt.detail && evt.detail.message ? evt.detail.message : 'Tarefa reativada!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de reativar Tarefas (HTMX) carregado!');
})();