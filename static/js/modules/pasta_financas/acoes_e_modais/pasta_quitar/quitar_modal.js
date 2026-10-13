// static/js/modules/pasta_financas/acoes_e_modais/pasta_quitar/quitar_modal.js
// ==========================================================
// MODAL DE QUITAR — com data editável
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // ABRIR MODAL (HTMX carrega o HTML)
    // ==========================================================
    window.abrirModalQuitar = function(sequencia) {
        // 🔥 Fecha o modal de detalhes se estiver aberto
        var modalDetalhes = document.getElementById('modalDetalhesTransacao');
        if (modalDetalhes) {
            modalDetalhes.classList.remove('active');
        }

        if (window.htmx) {
            window.htmx.ajax('GET', '/financas/quitar_transacao/modal/' + sequencia, {
                target: '#modal-quitar-container',
                swap: 'innerHTML'
            });
        }
    };

    // ==========================================================
    // FECHAR
    // ==========================================================
    window.fecharModalQuitar = function() {
        var container = document.getElementById('modal-quitar-container');
        if (container) container.innerHTML = '';
        document.body.style.overflow = '';
    };

    // ==========================================================
    // CONFIRMAR QUITAR (POST com data)
    // ==========================================================
    window.confirmarQuitar = function() {
        var sequencia = document.getElementById('quitarSequencia').value;
        var data = document.getElementById('quitarData').value;

        if (!sequencia || !data) {
            if (window.Notificacao) window.Notificacao.erro('Data é obrigatória');
            return;
        }

        // Botão loading
        var btn = document.getElementById('btnConfirmarQuitar');
        var textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = 'Salvando...';

        // POST via fetch
        fetch('/financas/quitar_transacao/' + sequencia, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'HX-Request': 'true'
            },
            body: 'data_quitamento=' + encodeURIComponent(data)
        })
        .then(function(r) { return r.text(); })
        .then(function(html) {
            // Substitui a linha da transação
            var linhaAntiga = document.querySelector('tr[data-sequencia="' + sequencia + '"]');
            if (linhaAntiga) {
                linhaAntiga.outerHTML = html;
            } else {
                // Fallback: recarrega a tabela
                if (window.htmx) {
                    window.htmx.ajax('GET', '/financas/', {
                        target: '#tabela-container',
                        swap: 'outerHTML',
                        headers: { 'HX-Request': 'true' }
                    });
                }
            }

            // Fecha modal
            window.fecharModalQuitar();

            // Toast
            if (window.Notificacao) {
                window.Notificacao.sucesso('Transação quitada com sucesso!');
            }
        })
        .catch(function(err) {
            console.error('❌ Erro:', err);
            if (window.Notificacao) window.Notificacao.erro('Erro ao quitar');
        })
        .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = textoOriginal;
            }
        });
    };

    // ==========================================================
    // DELEGAÇÃO — clique no botão "Quitar"
    // ==========================================================
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-quitar');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        var sequencia = btn.dataset.id;
        if (sequencia) {
            window.abrirModalQuitar(sequencia);
        }
    });

    // ==========================================================
    // HTMX afterSwap — configura overflow quando o modal carrega
    // ==========================================================
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'modal-quitar-container') {
            document.body.style.overflow = 'hidden';
        }
    });

    // ==========================================================
    // ESC — fecha modal
    // ==========================================================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalQuitarTransacao');
            if (modal) window.fecharModalQuitar();
        }
    });

    console.log('✅ Modal de quitar carregado!');
})();