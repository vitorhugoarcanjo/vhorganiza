// static/js/modules/pasta_orcamentos/acoes_e_modais/pasta_reativar/reativar_orcamento.js
// ==========================================================
// REATIVAR ORÇAMENTO — HTMX puro
// ==========================================================

(function() {
    'use strict';

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalReativar = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalReativarOrcamento');
        const titulo = document.getElementById('modalReativarTitulo');
        const texto = document.getElementById('modalReativarTexto');
        const nomeEl = document.getElementById('nomeOrcamentoReativar');

        // 🔥 Clona botão pra limpar listeners HTMX antigos
        let btnConfirmar = document.getElementById('btnConfirmarReativarOrcamento');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarReativarOrcamento');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de reativar não encontrado');
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
    // Delegação: clique no botão Reativar da linha
    // ==========================================================
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-reativar');
        if (!btn) return;

        e.preventDefault();
        modalAberto = false;

        const sequencia = btn.dataset.sequencia;
        const desc = btn.dataset.desc;

        window.abrirModalReativar({
            titulo: 'Reativar Orçamento',
            texto: 'Deseja reativar o orçamento: "' + desc + '"?',
            nome: desc,
            url: '/orcamentos/' + sequencia + '/reativar'
        });
    });

    // ==========================================================
    // Toast via HX-Trigger
    // ==========================================================
    document.body.addEventListener('orcamentoReativado', function(evt) {
        modalAberto = false;
        const modal = document.getElementById('modalReativarOrcamento');
        if (modal) modal.classList.remove('active');

        const msg = (evt.detail && evt.detail.message) ? evt.detail.message : 'Orçamento reativado!';
        if (window.Notificacao) window.Notificacao.sucesso(msg);
    });

    console.log('✅ Sistema de reativar (HTMX) do Orçamento carregado!');
})();