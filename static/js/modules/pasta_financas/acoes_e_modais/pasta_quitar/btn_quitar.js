// static/js/modules/pasta_financas/acoes_e_modais/pasta_quitar/btn_quitar.js
// ==========================================================
// QUITAR / RECEBER — HTMX puro
// Backend devolve o HTML da linha; front só mostra toast
// ==========================================================

(function() {
    'use strict';

    // 🔥 Toast quando o backend dispara HX-Trigger: transacaoQuitada
    document.body.addEventListener('transacaoQuitada', function() {
        if (window.Notificacao) {
            window.Notificacao.sucesso('Transação quitada com sucesso!');
        }
        if (typeof calcularTotaisFinancas === 'function') {
            calcularTotaisFinancas();
        }
    });

    console.log('✅ btn_quitar (HTMX) carregado!');
})();