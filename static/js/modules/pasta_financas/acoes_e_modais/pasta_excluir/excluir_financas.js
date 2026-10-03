// static/js/modules/pasta_financas/acoes_e_modais/pasta_excluir/excluir_financas.js
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

        const modal = document.getElementById('modalExcluirFinancas');
        const titulo = document.getElementById('modalExcluirTitulo');
        const texto = document.getElementById('modalExcluirTexto');

        // 🔥 Clona botão pra limpar listeners HTMX antigos
        let btnConfirmar = document.getElementById('btnConfirmarExcluirFinancas');
        if (btnConfirmar && btnConfirmar.parentNode) {
            const clone = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(clone, btnConfirmar);
            btnConfirmar = clone;
        }

        const btnCancelar = document.getElementById('btnCancelarExcluirFinancas');

        if (!modal || !btnConfirmar || !btnCancelar) {
            console.error('❌ Modal de exclusão não encontrado');
            return;
        }

        modalAberto = true;
        titulo.textContent = config.titulo;
        texto.textContent = config.texto;
        modal.classList.add('active');

        // Configura hx-post dinamicamente
        btnConfirmar.setAttribute('hx-post', config.url);
        btnConfirmar.setAttribute('hx-target', '#tbody-transacoes');
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

        // Fecha se sucesso (200/204) OU se 409 (conflict → tratado por evento)
        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            const status = evt.detail.xhr.status;
            if (status >= 200 && status < 300) {
                fecharModal();
            } else if (status === 409) {
                // Deixa o listener global tratar
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

        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;

        window.abrirModalExcluir({
            titulo: 'Inativar Transação',
            texto: 'Deseja inativar a transação: "' + descricao + '"?',
            url: '/financas/excluir_transacao/' + id
        });
    });

    // ==========================================================
    // Backend dispara isso via HX-Trigger quando é parcelamento
    // ==========================================================
    document.body.addEventListener('pedirConfirmacaoParcelamento', function(evt) {
        const dados = evt.detail;
        if (!dados || !dados.pai_id) return;

        // 🔥 Zera o estado (o 1º modal já fechou)
        modalAberto = false;

        // Abre 2º modal perguntando se quer inativar tudo
        setTimeout(function() {
            window.abrirModalExcluir({
                titulo: '⚠️ Atenção! Parcelamento Detectado',
                texto: 'Esta transação faz parte de um parcelamento.\n\nDeseja inativar TODAS as parcelas?',
                url: '/financas/excluir_transacao/parcelamento/' + dados.pai_id
            });
        }, 200);
    });

    // ==========================================================
    // Toast via HX-Trigger
    // ==========================================================
    document.body.addEventListener('transacaoInativada', function() {
        modalAberto = false;
        const modal = document.getElementById('modalExcluirFinancas');
        if (modal) modal.classList.remove('active');

        if (window.Notificacao) window.Notificacao.sucesso('Transação inativada com sucesso!');
        if (typeof calcularTotaisFinancas === 'function') calcularTotaisFinancas();
    });

    console.log('✅ Sistema de exclusão (HTMX) carregado!');
})();