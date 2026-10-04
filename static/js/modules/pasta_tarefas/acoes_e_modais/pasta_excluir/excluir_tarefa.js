// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_excluir/excluir_tarefa.js
// ==========================================================
// EXCLUIR (inativar) — HTMX puro
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalExcluirTarefa = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalConfirmacao');
        const titulo = document.getElementById('modalTitulo');
        const texto = document.getElementById('modalTexto');

        // 🔥 Clona botão pra limpar listeners HTMX antigos
        let btnConfirmar = document.getElementById('btnConfirmarExcluirTarefa');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarExcluirTarefa');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de exclusão não encontrado');
            return;
        }

        modalAberto = true;
        if (titulo) titulo.textContent = config.titulo;
        if (texto) texto.textContent = config.texto;
        modal.classList.add('active');

        // Configura hx-post dinamicamente
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
    // Delegação: clique no botão Excluir da linha
    // ==========================================================
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-excluir');
        if (!btn) return;

        e.preventDefault();

        // 🔥 Zera o estado (garante que a 2ª vez funcione)
        modalAberto = false;

        const seq = btn.dataset.sequencia;
        const titulo = btn.dataset.titulo;

        window.abrirModalExcluirTarefa({
            titulo: 'Inativar Tarefa',
            texto: 'Deseja inativar a tarefa: "' + titulo + '"?',
            url: '/tarefas/excluir_tarefa/' + seq
        });
    });

    // ==========================================================
    // Toast via HX-Trigger
    // ==========================================================
    document.body.addEventListener('tarefaInativada', function() {
        modalAberto = false;
        const modal = document.getElementById('modalConfirmacao');
        if (modal) modal.classList.remove('active');

        if (window.Notificacao) window.Notificacao.sucesso('Tarefa inativada com sucesso!');
    });

    console.log('✅ Sistema de exclusão Tarefas (HTMX) carregado!');
})();