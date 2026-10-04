// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_auditoria/auditoria_tarefa.js
// ==========================================================
// AUDITORIA - TAREFAS (fechar modal + toggle accordion)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // FECHAR MODAL
    // ==========================================================
    if (!window.fecharModalAuditoria) {
        window.fecharModalAuditoria = function() {
            const container = document.getElementById('modal-auditoria-container');
            if (container) container.innerHTML = '';
            document.body.style.overflow = '';
        };
    }

    // ==========================================================
    // TOGGLE DO ACCORDION
    // ==========================================================
    if (!window.toggleAuditEntry) {
        window.toggleAuditEntry = function(headerEl) {
            const entry = headerEl.closest('.audit-entry');
            if (!entry) return;
            entry.classList.toggle('open');
        };
    }

    // ==========================================================
    // HTMX injeta o modal → ajusta overflow + abre o 1º registro
    // ==========================================================
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'modal-auditoria-container') {
            const modal = document.getElementById('modalAuditoria');
            if (modal) {
                modal.onclick = function(e) {
                    if (e.target === modal) window.fecharModalAuditoria();
                };

                // 🆕 Abre o primeiro registro por padrão
                const primeiro = modal.querySelector('.audit-entry');
                if (primeiro) primeiro.classList.add('open');
            }
            document.body.style.overflow = 'hidden';
        }
    });

    // ==========================================================
    // ESC fecha
    // ==========================================================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modalAuditoria');
            if (modal) window.fecharModalAuditoria();
        }
    });

    console.log('✅ Sistema de auditoria Tarefas (HTMX) carregado!');
})();