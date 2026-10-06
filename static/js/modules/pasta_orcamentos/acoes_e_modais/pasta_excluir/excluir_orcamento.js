// static/js/modules/pasta_orcamentos/acoes_e_modais/pasta_excluir/excluir_orcamento.js
// ==========================================================
// EXCLUIR (inativar) — HTMX puro
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalExcluir = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalExcluirOrcamento');
        const titulo = document.getElementById('modalExcluirTitulo');
        const texto = document.getElementById('modalExcluirTexto');
        const nomeEl = document.getElementById('nomeOrcamentoExcluir');

        let btnConfirmar = document.getElementById('btnConfirmarExcluirOrcamento');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarExcluirOrcamento');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de exclusão não encontrado');
            return;
        }

        modalAberto = true;
        if (titulo) titulo.textContent = config.titulo;
        if (texto && config.texto) texto.textContent = config.texto;
        if (nomeEl && config.nome) nomeEl.textContent = config.nome;
        modal.classList.add('active');

        // 🔥 hx-post com SEQUÊNCIA
        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-orcamentos');
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
        modalAberto = false;

        const sequencia = btn.dataset.sequencia;
        const desc = btn.dataset.desc;

        window.abrirModalExcluir({
            titulo: 'Inativar Orçamento',
            texto: 'Deseja inativar o orçamento: "' + desc + '"?',
            nome: desc,
            url: '/orcamentos/' + sequencia + '/excluir'
        });
    });

    // ==========================================================
    // Toast via HX-Trigger
    // ==========================================================
    document.body.addEventListener('orcamentoInativado', function(evt) {
        modalAberto = false;
        const modal = document.getElementById('modalExcluirOrcamento');
        if (modal) modal.classList.remove('active');

        const msg = (evt.detail && evt.detail.message) ? evt.detail.message : 'Orçamento inativado!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de exclusão (HTMX) do Orçamento carregado!');
})();