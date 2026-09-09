// ==========================================================
// TRANSAÇÃO - FORM COMPARTILHADO (NOVA + EDITAR)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // SELECIONAR TIPO
    // ==========================================================
    function selecionarTipo(btn) {
        var container = btn.closest('.tipo-container');
        container.querySelectorAll('.tipo-btn:not([disabled])').forEach(function(b) {
            b.classList.remove('active');
        });
        btn.classList.add('active');
        
        var hidden = document.getElementById('tipoHidden');
        if (hidden) hidden.value = btn.dataset.tipo;
        
        var badge = document.getElementById('finTipoBadge') || document.getElementById('finEditarTipoBadge');
        if (badge) {
            var tipo = btn.dataset.tipo;
            if (tipo === 'receita') {
                badge.textContent = '📈 Receita';
                badge.className = 'fin-tipo-badge receita';
            } else if (tipo === 'despesa') {
                badge.textContent = '📉 Despesa';
                badge.className = 'fin-tipo-badge despesa';
            } else {
                badge.textContent = '📊 Selecionar';
                badge.className = 'fin-tipo-badge';
            }
        }
    }

    // ==========================================================
    // FORMATAR VALOR
    // ==========================================================
    function formatarValor(input) {
        var valor = input.value.replace(/\D/g, '');
        if (valor === '') {
            input.value = '0,00';
            return;
        }
        var numero = parseInt(valor) / 100;
        var formatado = numero.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        input.value = formatado;
        atualizarTotais();
    }

    // ==========================================================
    // ATUALIZAR TOTAIS
    // ==========================================================
    function atualizarTotais() {
        var valorTotal = document.getElementById('valorTotal')?.value || '0,00';
        
        var totalOriginal = document.getElementById('totalOriginal');
        if (totalOriginal) totalOriginal.textContent = 'R$ ' + valorTotal;
        
        var soma = 0;
        document.querySelectorAll('#parcelasBody .valor-parcela-input').forEach(function(input) {
            var val = input.value.replace('.', '').replace(',', '.');
            if (!isNaN(parseFloat(val))) {
                soma += parseFloat(val);
            }
        });
        
        var somaFormatada = soma.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        var somaParcelas = document.getElementById('somaParcelas');
        if (somaParcelas) somaParcelas.textContent = 'R$ ' + somaFormatada;
        
        var totalNum = parseFloat(valorTotal.replace('.', '').replace(',', '.'));
        var diferenca = totalNum - soma;
        var difFormatada = diferenca.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        var difValor = document.getElementById('diferencaValor');
        if (difValor) difValor.textContent = 'R$ ' + difFormatada;
        
        var difItem = document.getElementById('diferencaItem');
        if (difItem) {
            difItem.style.display = Math.abs(diferenca) < 0.01 ? 'none' : 'block';
        }
    }

    // ==========================================================
    // GERAR PARCELAS
    // ==========================================================
    function gerarParcelas() {
        var numParcelas = parseInt(document.getElementById('totalParcelas').value) || 1;
        var configArea = document.getElementById('parcelasConfigArea');
        var wrapper = document.getElementById('parcelasWrapper');
        var tbody = document.getElementById('parcelasBody');
        
        if (numParcelas <= 1) {
            if (configArea) configArea.style.display = 'none';
            if (wrapper) wrapper.style.display = 'none';
            if (tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
            return;
        }
        
        if (configArea) configArea.style.display = 'block';
        if (wrapper) wrapper.style.display = 'block';
        
        var valorTotal = document.getElementById('valorTotal').value || '0,00';
        var valorNumerico = parseFloat(valorTotal.replace('.', '').replace(',', '.'));
        var valorParcela = valorNumerico / numParcelas;
        
        if (!tbody) return;
        
        var html = '';
        var primeiroVencimento = document.getElementById('primeiroVencimento').value;
        var intervalo = parseInt(document.getElementById('intervaloDias').value) || 30;
        var dataAtual = new Date(primeiroVencimento);
        
        for (var i = 1; i <= numParcelas; i++) {
            var valorFormatado = valorParcela.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            var dataFormatada = dataAtual.toISOString().split('T')[0];
            
            html += '<tr>';
            html += '<td><strong>' + i + '/' + numParcelas + '</strong></td>';
            html += '<td><input type="date" class="form-input data-parcela" value="' + dataFormatada + '" style="max-width: 140px;"></td>';
            html += '<td><input type="text" class="form-input valor-parcela-input" value="' + valorFormatado + '" style="max-width: 120px; text-align: right;"></td>';
            html += '</tr>';
            
            dataAtual.setDate(dataAtual.getDate() + intervalo);
        }
        
        tbody.innerHTML = html;
        
        tbody.querySelectorAll('.valor-parcela-input').forEach(function(input) {
            input.addEventListener('input', function() { formatarValor(this); atualizarTotais(); });
        });
        tbody.querySelectorAll('.data-parcela').forEach(function(input) {
            input.addEventListener('change', atualizarTotais);
        });
        
        atualizarTotais();
    }

    // ==========================================================
    // CARREGAR PARCELAS EXISTENTES (EDITAR)
    // ==========================================================
    function carregarParcelasExistentes() {
        var dataInput = document.getElementById('parcelasFilhasData');
        if (!dataInput || !dataInput.value) return;
        
        try {
            var parcelas = JSON.parse(dataInput.value);
            if (!parcelas || parcelas.length === 0) return;
            
            var numParcelas = parcelas.length;
            document.getElementById('totalParcelas').value = numParcelas;
            document.getElementById('primeiroVencimento').value = parcelas[0].data_vencimento || '';
            
            var tbody = document.getElementById('parcelasBody');
            if (!tbody) return;
            
            var html = '';
            parcelas.forEach(function(p, i) {
                var num = i + 1;
                html += '<tr>';
                html += '<td><strong>' + num + '/' + numParcelas + '</strong></td>';
                html += '<td><input type="date" class="form-input data-parcela" value="' + p.data_vencimento + '" style="max-width: 140px;"></td>';
                html += '<td><input type="text" class="form-input valor-parcela-input" value="' + p.valor + '" style="max-width: 120px; text-align: right;"></td>';
                html += '</tr>';
            });
            
            tbody.innerHTML = html;
            
            document.getElementById('parcelasConfigArea').style.display = 'block';
            document.getElementById('parcelasWrapper').style.display = 'block';
            
            tbody.querySelectorAll('.valor-parcela-input').forEach(function(input) {
                input.addEventListener('input', function() { formatarValor(this); atualizarTotais(); });
            });
            tbody.querySelectorAll('.data-parcela').forEach(function(input) {
                input.addEventListener('change', atualizarTotais);
            });
            
            atualizarTotais();
            
        } catch (e) {
            console.warn('Erro ao carregar parcelas:', e);
        }
    }

    // ==========================================================
    // 🔥 SUBMIT DO FORM (NOVO)
    // ==========================================================
    function submitForm(form) {
        var btn = document.getElementById('btn-submit');
        if (!btn) return;

        var textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Salvando...';

        var formData = new FormData(form);
        var data = Object.fromEntries(formData.entries());

        // Coleta parcelas
        var parcelas = [];
        document.querySelectorAll('#parcelasBody tr').forEach(function(row) {
            var inputs = row.querySelectorAll('input');
            if (inputs.length === 2) {
                parcelas.push({
                    vencimento: inputs[0].value,
                    valor: inputs[1].value
                });
            }
        });
        data.parcelas = parcelas;

        // 🔥 USA A ROTA CORRETA
        fetch('/financas/nova_transacao/salvar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        })
        .then(function(response) { return response.json(); })
        .then(function(result) {
            if (result.success) {
                if (window.Notificacao) window.Notificacao.sucesso(result.message);
                if (window.fecharModalNovaTransacao) window.fecharModalNovaTransacao();
                setTimeout(function() { window.location.reload(); }, 500);
            } else {
                if (window.Notificacao) window.Notificacao.erro(result.message || result.error || 'Erro ao salvar');
                btn.disabled = false;
                btn.innerHTML = textoOriginal;
            }
        })
        .catch(function(error) {
            console.error('❌ Erro:', error);
            if (window.Notificacao) window.Notificacao.erro('Erro ao salvar transação');
            btn.disabled = false;
            btn.innerHTML = textoOriginal;
        });
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.selecionarTipo = selecionarTipo;
    window.formatarValor = formatarValor;
    window.atualizarTotais = atualizarTotais;
    window.gerarParcelas = gerarParcelas;
    window.carregarParcelasExistentes = carregarParcelasExistentes;

    // ==========================================================
    // INICIALIZAR
    // ==========================================================
    document.addEventListener('DOMContentLoaded', function() {
        // Tipo
        document.querySelectorAll('.tipo-btn:not([disabled])').forEach(function(btn) {
            btn.addEventListener('click', function() {
                selecionarTipo(this);
            });
        });
        
        // Valor
        var valorInput = document.getElementById('valorTotal');
        if (valorInput) {
            valorInput.addEventListener('input', function() {
                formatarValor(this);
                if (document.getElementById('totalParcelas').value > 1) {
                    gerarParcelas();
                }
            });
        }
        
        // Parcelas
        document.getElementById('totalParcelas')?.addEventListener('change', gerarParcelas);
        document.getElementById('btnDistribuir')?.addEventListener('click', gerarParcelas);
        document.getElementById('primeiroVencimento')?.addEventListener('change', gerarParcelas);
        document.getElementById('intervaloDias')?.addEventListener('change', gerarParcelas);
        
        // Carregar parcelas existentes (EDITAR)
        carregarParcelasExistentes();

        // 🔥 SUBMIT DO FORM (NOVO)
        var form = document.getElementById('form-transacao');
        if (form) {
            // Remove listener antigo
            var novoForm = form.cloneNode(true);
            form.parentNode.replaceChild(novoForm, form);

            novoForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitForm(this);
            });
        }
    });

    console.log('✅ TRANSACAO-FORM carregado!');

})();