// ==========================================================
// MODAL NOVA TRANSAÇÃO (SÓ ABRIR/FECHAR)
// ==========================================================

(function() {
    'use strict';

    function abrirModalNovaTransacao() {
        console.log('🔓 Abrindo modal Nova Transação');
        var modal = document.getElementById('modalNovaTransacao');
        if (!modal) return;

        // 🔥 Reseta os campos usando os IDs do partial
        var form = document.getElementById('form-transacao');
        if (form) form.reset();
        
        var valorTotal = document.getElementById('valorTotal');
        if (valorTotal) valorTotal.value = '0,00';
        
        var totalParcelas = document.getElementById('totalParcelas');
        if (totalParcelas) totalParcelas.value = '1';
        
        var dataEmissao = document.getElementById('dataEmissao');
        if (dataEmissao) {
            dataEmissao.value = new Date().toISOString().split('T')[0];
        }
        
        var dataVencimento = document.getElementById('dataVencimento');
        if (dataVencimento) {
            dataVencimento.value = new Date().toISOString().split('T')[0];
        }
        
        var primeiroVencimento = document.getElementById('primeiroVencimento');
        if (primeiroVencimento) {
            primeiroVencimento.value = new Date().toISOString().split('T')[0];
        }

        // Resetar tipo
        document.querySelectorAll('#form-transacao .tipo-btn').forEach(function(b) {
            b.classList.remove('active');
        });
        var vazioBtn = document.querySelector('#form-transacao .tipo-btn[data-tipo="vazio"]');
        if (vazioBtn) vazioBtn.classList.add('active');
        
        var tipoHidden = document.getElementById('tipoHidden');
        if (tipoHidden) tipoHidden.value = '';

        // Badge
        var badge = document.getElementById('finTipoBadge');
        if (badge) {
            badge.textContent = '📊 Selecionar';
            badge.className = 'fin-tipo-badge';
        }

        // Resetar parcelas
        var configArea = document.getElementById('parcelasConfigArea');
        if (configArea) configArea.style.display = 'none';
        
        var wrapper = document.getElementById('parcelasWrapper');
        if (wrapper) wrapper.style.display = 'none';
        
        var parcelasBody = document.getElementById('parcelasBody');
        if (parcelasBody) {
            parcelasBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
        }

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        setTimeout(function() {
            var desc = document.getElementById('descricaoInput');
            if (desc) desc.focus();
        }, 100);
    }

    function fecharModalNovaTransacao() {
        console.log('🔒 Fechando modal Nova Transação');
        var modal = document.getElementById('modalNovaTransacao');
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
        document.body.style.overflow = '';
    }

    window.abrirModalNovaTransacao = abrirModalNovaTransacao;
    window.fecharModalNovaTransacao = fecharModalNovaTransacao;

    // ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalNovaTransacao');
            if (modal && modal.classList.contains('active')) {
                fecharModalNovaTransacao();
            }
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaTransacao');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            fecharModalNovaTransacao();
        }
    });

    console.log('✅ MODAL NOVA TRANSAÇÃO carregado!');

})();