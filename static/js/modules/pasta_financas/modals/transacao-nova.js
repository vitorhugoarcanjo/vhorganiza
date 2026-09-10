// ==========================================================
// MÓDULO: MODAL DE NOVA TRANSAÇÃO (APENAS CONTROLE DE ABRIR/FECHAR)
// ==========================================================
(function() {
    'use strict';

    function obterDataLocalHoje() {
        var hoje = new Date();
        var ano = hoje.getFullYear();
        var mes = String(hoje.getMonth() + 1).padStart(2, '0');
        var dia = String(hoje.getDate()).padStart(2, '0');
        return ano + '-' + mes + '-' + dia;
    }

    function limparFormularioModal() {
        var form = document.getElementById('formNovaTransacao') || document.getElementById('form-transacao');
        if (!form) return;

        form.reset();

        var hojeStr = obterDataLocalHoje();
        var valorTotal = form.querySelector('#valorTotal');
        if (valorTotal) valorTotal.value = '0,00';

        var totalParcelas = form.querySelector('#totalParcelas');
        if (totalParcelas) totalParcelas.value = '1';

        ['dataEmissao', 'dataVencimento', 'primeiroVencimento'].forEach(function(id) {
            var el = form.querySelector('#' + id);
            if (el) el.value = hojeStr;
        });

        var tipoHidden = form.querySelector('#tipoHidden');
        if (tipoHidden) tipoHidden.value = '';

        form.querySelectorAll('.tipo-btn').forEach(function(b) {
            b.classList.remove('active');
        });

        var badge = form.querySelector('#finTipoBadge');
        if (badge) {
            badge.textContent = '📊 Selecionar';
            badge.className = 'fin-tipo-badge';
        }

        var configArea = form.querySelector('#parcelasConfigArea');
        if (configArea) configArea.style.display = 'none';

        var wrapper = form.querySelector('#parcelasWrapper');
        if (wrapper) wrapper.style.display = 'none';

        var parcelasBody = form.querySelector('#parcelasBody');
        if (parcelasBody) {
            parcelasBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
        }
    }

    function abrirModalNovaTransacao() {
        console.log('🔓 Abrindo modal Nova Transação');
        var modal = document.getElementById('modalNovaTransacao');
        if (!modal) return;

        limparFormularioModal();

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
        limparFormularioModal();
    }

    // Exportações globais para abrir/fechar via HTML
    window.abrirModalNovaTransacao = abrirModalNovaTransacao;
    window.fecharModalNovaTransacao = fecharModalNovaTransacao;

    // Fechar com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalNovaTransacao');
            if (modal && modal.classList.contains('active')) {
                fecharModalNovaTransacao();
            }
        }
    });

    // Fechar clicando no fundo escuro
    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaTransacao');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            fecharModalNovaTransacao();
        }
    });

    console.log('✅ MODAL NOVA TRANSAÇÃO (Controlador) carregado!');
})();