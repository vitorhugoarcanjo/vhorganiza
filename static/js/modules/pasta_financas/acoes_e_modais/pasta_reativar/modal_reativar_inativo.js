// static/js/modules/pasta_financas/acoes_e_modais/pasta_reativar/modal_reativar_inativo.js
// ==========================================================
// MODAL REATIVAR — HTMX puro
// ==========================================================

(function() {
    'use strict';

    if (window._reativarSistemaCarregado) return;
    window._reativarSistemaCarregado = true;

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalReativar = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalReativar');
        const titulo = document.getElementById('modalReativarTitulo');
        const texto = document.getElementById('modalReativarTexto');

        // 🔥 CLONA o botão pra limpar qualquer listener antigo
        let btnConfirmar = document.getElementById('btnConfirmarReativar');
        const btnConfirmarNovo = btnConfirmar.cloneNode(true);
        btnConfirmar.parentNode.replaceChild(btnConfirmarNovo, btnConfirmar);
        btnConfirmar = btnConfirmarNovo;

        const btnCancelar = document.getElementById('btnCancelarReativar');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de reativação não encontrado');
            return;
        }

        modalAberto = true;
        titulo.textContent = config.titulo;
        texto.textContent = config.texto;
        modal.classList.add('active');

        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', config.target);
        btnConfirmar.setAttribute('hx-swap', config.swap || 'outerHTML');

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
            if (evt.detail.successful) {
                fecharModal();
                btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
            }
        });
    };

    // ==========================================================
    // Delegação: clique no botão Reativar da linha
    // ==========================================================
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-reativar');
        if (!btn) return;

        e.preventDefault();

        // 🔥 ZERA o estado (garante que a 2ª vez funcione)
        modalAberto = false;

        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;

        fetch('/financas/reativar_transacao/verificar/' + id, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(data => {
            if (data.tipo === 'parcela') {
                window.abrirModalReativar({
                    titulo: '⚠️ Reativar Parcelamento Completo',
                    texto: data.mensagem + '\n\n"' + data.descricao + '"\n\nIsso vai reativar TODAS as ' + data.total_parcelas + ' parcelas.',
                    url: '/financas/reativar_transacao/parcelamento/' + data.transacao_pai_id,
                    target: '#tbody-transacoes',
                    swap: 'outerHTML'
                });

            } else if (data.tipo === 'parcelamento') {
                window.abrirModalReativar({
                    titulo: '⚠️ Reativar Parcelamento',
                    texto: data.mensagem + '\n\n"' + data.descricao + '"',
                    url: '/financas/reativar_transacao/parcelamento/' + id,
                    target: '#tbody-transacoes',
                    swap: 'outerHTML'
                });

            } else if (data.tipo === 'simples') {
                window.abrirModalReativar({
                    titulo: '⚠️ Reativar Transação',
                    texto: 'Deseja realmente REATIVAR a transação?\n\n"' + descricao + '"',
                    url: '/financas/reativar_transacao/' + id,
                    target: '#linha-transacao-' + id,
                    swap: 'outerHTML'
                });

            } else {
                if (window.Notificacao) window.Notificacao.erro(data.error || 'Erro ao verificar');
            }
        })
        .catch(error => {
            console.error('❌ Erro na verificação:', error);
            if (window.Notificacao) window.Notificacao.erro('Erro ao verificar transação');
        });
    });

    // ==========================================================
    // Toast + reset via HX-Trigger
    // ==========================================================
    document.body.addEventListener('transacaoReativada', function() {
        // 🔥 RESETA o estado (defensivo — caso o afterRequest não dispare)
        modalAberto = false;
        const modal = document.getElementById('modalReativar');
        if (modal) modal.classList.remove('active');

        if (window.Notificacao) {
            window.Notificacao.sucesso('Transação reativada com sucesso!');
        }
        if (typeof calcularTotaisFinancas === 'function') {
            calcularTotaisFinancas();
        }
    });

    console.log('✅ Sistema de reativação (HTMX) carregado!');
})();