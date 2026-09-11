// ==========================================================
// MODAL NOVA TRANSAÇÃO - v2 (usa TransacaoForm)
// ==========================================================
(function() {
    'use strict';

    var formInstance = null;

    function instanciar() {
        var formEl = document.getElementById('formNovaTransacao');
        if (!formEl) return null;
        if (formInstance) return formInstance;

        formInstance = new window.TransacaoForm(formEl, {
            mode: 'create',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message || 'Transação salva!');
                fecharModalNovaTransacao();

                // Recarrega tabela via HTMX
                if (window.recarregarTabelaFinancas) {
                    window.recarregarTabelaFinancas();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/financas', '#tabela-container');
                } else {
                    setTimeout(function() { window.location.reload(); }, 600);
                }
            }
        });
        return formInstance;
    }

    function abrirModalNovaTransacao() {
        var modal = document.getElementById('modalNovaTransacao');
        if (!modal) return;

        var f = instanciar();
        if (f) f.reset();

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        setTimeout(function() {
            var desc = modal.querySelector('.js-descricao');
            if (desc) desc.focus();
        }, 100);
    }

    function fecharModalNovaTransacao() {
        var modal = document.getElementById('modalNovaTransacao');
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
        document.body.style.overflow = '';
        var f = instanciar();
        if (f) f.reset();
    }

    function salvarNovaTransacao() {
        var f = instanciar();
        if (!f) return;

        var btn = document.querySelector('#footerFixoNova .btn-footer-primary');
        if (btn) { btn.disabled = true; btn.dataset.txt = btn.innerHTML; btn.innerHTML = 'Salvando...'; }

        f.submit('/financas/nova_transacao/salvar')
         .catch(function() { /* já notificado */ })
         .finally(function() {
            if (btn) { btn.disabled = false; btn.innerHTML = btn.dataset.txt || 'SALVAR'; }
         });
    }

    window.abrirModalNovaTransacao = abrirModalNovaTransacao;
    window.fecharModalNovaTransacao = fecharModalNovaTransacao;
    window.salvarNovaTransacao = salvarNovaTransacao;

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalNovaTransacao');
            if (modal && modal.classList.contains('active')) fecharModalNovaTransacao();
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaTransacao');
        if (modal && modal.classList.contains('active') && e.target === modal) fecharModalNovaTransacao();
    });

    console.log('✅ MODAL NOVA TRANSAÇÃO v2 carregado!');
})();