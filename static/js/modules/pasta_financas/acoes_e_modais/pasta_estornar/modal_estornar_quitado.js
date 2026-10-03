// static/js/modules/pasta_financas/acoes_e_modais/pasta_estornar/modal_estornar_quitado.js
// ==========================================================
// MODAL ESTORNAR — HTMX puro
// ==========================================================

(function() {
    'use strict';

    if (window._estornoSistemaCarregado) return;
    window._estornoSistemaCarregado = true;

    let modalAberto = false;

    // ==========================================================
    // Abrir o modal
    // ==========================================================
    window.abrirModalEstornar = function(config) {
        if (modalAberto) return;

        const modal = document.getElementById('modalEstornar');
        const titulo = document.getElementById('modalEstornarTitulo');
        const texto = document.getElementById('modalEstornarTexto');
        const btnConfirmar = document.getElementById('btnConfirmarEstornar');
        const btnCancelar = document.getElementById('btnCancelarEstornar');

        if (!modal || !btnConfirmar || !btnCancelar) return;

        modalAberto = true;

        titulo.textContent = config.titulo;
        texto.textContent = config.texto;
        modal.classList.add('active');

        // 🔥 Define a URL do hx-post dinamicamente
        btnConfirmar.setAttribute('hx-post', '/financas/estornar_transacao/' + config.id);
        btnConfirmar.setAttribute('hx-target', '#linha-transacao-' + config.id);
        btnConfirmar.setAttribute('hx-swap', 'outerHTML');

        // 🔥 Processa HTMX no botão (senão ele ignora atributos novos)
        if (window.htmx) window.htmx.process(btnConfirmar);

        const fecharModal = () => {
            modal.classList.remove('active');
            modalAberto = false;
            btnConfirmar.removeAttribute('hx-post');
            btnConfirmar.removeAttribute('hx-target');
        };

        btnCancelar.onclick = fecharModal;
        modal.onclick = function(e) {
            if (e.target === modal) fecharModal();
        };

        // Fechar após sucesso (HTMX dispara htmx:afterRequest)
        btnConfirmar.addEventListener('htmx:afterRequest', function onDone(evt) {
            if (evt.detail.successful) {
                fecharModal();
                btnConfirmar.removeEventListener('htmx:afterRequest', onDone);
            }
        });
    };

    // ==========================================================
    // Delegação: clique no botão Estornar da linha
    // ==========================================================
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-estornar');
        if (!btn) return;

        e.preventDefault();

        const id = btn.dataset.id;
        const descricao = btn.dataset.desc;
        const tipo = btn.dataset.tipo;
        const tipoTexto = tipo === 'despesa' ? 'DESPESA' : 'RECEITA';

        window.abrirModalEstornar({
            id: id,
            titulo: '⚠️ Estornar ' + tipoTexto,
            texto: 'Deseja realmente ESTORNAR a transação?\n\n"' + descricao + '"\n\nEla voltará para o status ABERTO.'
        });
    });

    // ==========================================================
    // Toast quando o backend dispara HX-Trigger
    // ==========================================================
    document.body.addEventListener('transacaoEstornada', function() {
        if (window.Notificacao) {
            window.Notificacao.sucesso('Transação estornada com sucesso!');
        }
        if (typeof calcularTotaisFinancas === 'function') {
            calcularTotaisFinancas();
        }
    });

    console.log('✅ Sistema de estorno (HTMX) carregado!');
})();