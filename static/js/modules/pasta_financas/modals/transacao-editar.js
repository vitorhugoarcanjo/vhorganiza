// ==========================================================
// MODAL EDITAR TRANSAÇÃO - v3 (HTMX injeta, JS popula)
// ==========================================================
(function() {
    'use strict';

    var transacaoId = null;
    var formInstance = null;

    function instanciar(formEl) {
        if (!formEl) return null;
        if (formInstance && formInstance.form === formEl) return formInstance;

        formInstance = new window.TransacaoForm(formEl, {
            mode: 'edit',
            onSubmitSuccess: function(result) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message || 'Transação atualizada!');
                fecharModalEditarTransacao();
                setTimeout(function() { window.location.reload(); }, 400);
            }
        });
        return formInstance;
    }

    // ==========================================================
    // ABRIR (busca dados via /dados/ e popula)
    // ==========================================================
    function abrirModalEditarTransacao(id) {
        transacaoId = id;

        var modal = document.getElementById('modalEditarTransacao');
        var formEl = document.getElementById('formEditarTransacao');
        if (!modal || !formEl) return;

        if (!transacaoId) {
            if (window.Notificacao) window.Notificacao.erro('ID da transação não identificado.');
            return;
        }

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Spinner
        var body = modal.querySelector('.fin-modal-body');
        var loadingDiv = null;
        if (body) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'editLoadingOverlay';
            loadingDiv.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;justify-content:center;align-items:center;flex-direction:column;z-index:10;border-radius:8px;';
            loadingDiv.innerHTML = '<div style="width:40px;height:40px;border:4px solid #fff;border-top-color:#2563eb;border-radius:50%;animation:spin 0.8s linear infinite;"></div><p style="color:#fff;margin-top:10px;">Carregando dados...</p>';
            body.style.position = 'relative';
            body.appendChild(loadingDiv);
        }

        fetch('/financas/edit_transacoes/dados/' + transacaoId, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function(resposta) {
            if (loadingDiv) loadingDiv.remove();
            var data = resposta.data || resposta;

            // Atualiza título
            var seqSpan = modal.querySelector('#finEditarSequencia');
            if (seqSpan && data.sequencia) {
                seqSpan.textContent = 'Editar Transação #' + data.sequencia;
            }
            if (formEl && data.sequencia) {
                formEl.dataset.transacaoId = data.sequencia;
            }

            // Popula form
            var f = instanciar(formEl);
            if (f) f.setData(data);
        })
        .catch(function(error) {
            console.error('❌ Erro no GET dados:', error);
            if (loadingDiv) loadingDiv.remove();
            if (body) body.innerHTML = '<div style="color:#ef4444;padding:20px;">Erro ao carregar dados</div>';
        });
    }

    // ==========================================================
    // FECHAR
    // ==========================================================
    function fecharModalEditarTransacao() {
        var modal = document.getElementById('modalEditarTransacao');
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
        document.body.style.overflow = '';
        formInstance = null;
    }

    // ==========================================================
    // SALVAR
    // ==========================================================
    function salvarEditarTransacao() {
        var formEl = document.getElementById('formEditarTransacao');
        transacaoId = (formEl && formEl.dataset.transacaoId) || transacaoId;

        if (!transacaoId || transacaoId === 'None') {
            if (window.Notificacao) window.Notificacao.erro('ID da transação não identificado.');
            return;
        }

        var f = instanciar(formEl);
        if (!f) return;

        var btn = document.querySelector('#footerFixoEditar .btn-footer-primary');
        if (btn) { btn.disabled = true; btn.dataset.txt = btn.innerHTML; btn.innerHTML = 'Salvando...'; }

        f.submit('/financas/edit_transacoes/' + transacaoId)
         .catch(function() { /* já notificado */ })
         .finally(function() {
            if (btn) { btn.disabled = false; btn.innerHTML = btn.dataset.txt || 'ATUALIZAR'; }
         });
    }

    // ==========================================================
    // 🔥 O FIX: escuta o HTMX injetar o modal e chama abrir()
    // ==========================================================
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        var target = evt.detail && evt.detail.target;
        if (!target) return;
        if (target.id !== 'modal-editar-container' && !target.closest('#modal-editar-container')) return;

        var formEl = document.getElementById('formEditarTransacao');
        if (!formEl) return;

        var seq = formEl.dataset.transacaoId;
        if (!seq || seq === 'None') {
            console.warn('⚠️ HTMX injetou o modal mas sem data-transacao-id');
            return;
        }

        console.log('🔁 HTMX injetou modal de editar, populando via /dados/' + seq);
        abrirModalEditarTransacao(seq);
    });

    window.abrirModalEditarTransacao = abrirModalEditarTransacao;
    window.fecharModalEditarTransacao = fecharModalEditarTransacao;
    window.salvarEditarTransacao = salvarEditarTransacao;

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalEditarTransacao');
            if (modal && modal.classList.contains('active')) fecharModalEditarTransacao();
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalEditarTransacao');
        if (modal && modal.classList.contains('active') && e.target === modal) fecharModalEditarTransacao();
    });

    console.log('✅ MODAL EDITAR TRANSAÇÃO v3 carregado!');
})();