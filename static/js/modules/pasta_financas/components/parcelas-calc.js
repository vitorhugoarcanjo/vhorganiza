// ==========================================================
// MÓDULO: CÁLCULO E GERAÇÃO DE PARCELAS (ISOLADO)
// ==========================================================
(function() {
    'use strict';

    window.GeradorParcelasFinancas = {
        init: function(contexto) {
            var form = contexto && contexto.form ? contexto.form : (document.getElementById('formNovaTransacao') || document.getElementById('form-transacao'));
            if (!form) return;

            var valorTotalInput = form.querySelector('.valor-total') || form.querySelector('#valorTotal');
            var totalParcelasInput = form.querySelector('.total-parcelas') || form.querySelector('#totalParcelas');
            var primeiroVencimentoInput = form.querySelector('.primeiro-vencimento') || form.querySelector('#primeiroVencimento');
            var periodicidadeInput = form.querySelector('.periodicidade') || form.querySelector('#periodicidade');
            var parcelasConfigArea = form.querySelector('.parcelas-config-area') || form.querySelector('#parcelasConfigArea');
            var parcelasWrapper = form.querySelector('.parcelas-wrapper') || form.querySelector('#parcelasWrapper');
            var parcelasBody = form.querySelector('.parcelas-body') || form.querySelector('#parcelasBody');

            if (!totalParcelasInput || !parcelasBody) return;

            function gerar() {
                var numParcelas = parseInt(totalParcelasInput.value) || 1;

                if (numParcelas <= 1) {
                    if (parcelasConfigArea) parcelasConfigArea.style.display = 'none';
                    if (parcelasWrapper) parcelasWrapper.style.display = 'none';
                    parcelasBody.innerHTML = '';
                    return;
                }

                if (parcelasConfigArea) parcelasConfigArea.style.display = 'block';
                if (parcelasWrapper) parcelasWrapper.style.display = 'block';

                var strValor = (valorTotalInput ? valorTotalInput.value : '0,00').replace(/\./g, '').replace(',', '.');
                var valorTotal = parseFloat(strValor) || 0;
                var valorBase = Math.floor((valorTotal / numParcelas) * 100) / 100;
                var resto = parseFloat((valorTotal - (valorBase * numParcelas)).toFixed(2));

                var primeiroVenc = primeiroVencimentoInput ? primeiroVencimentoInput.value : '';
                var dataAtual = primeiroVenc ? new Date(primeiroVenc + 'T00:00:00') : new Date();
                var periodicidade = periodicidadeInput ? periodicidadeInput.value : 'MENSAL';

                var html = '';
                for (var i = 1; i <= numParcelas; i++) {
                    var valorParcela = (i === 1) ? (valorBase + resto) : valorBase;

                    var ano = dataAtual.getFullYear();
                    var mes = String(dataAtual.getMonth() + 1).padStart(2, '0');
                    var dia = String(dataAtual.getDate()).padStart(2, '0');
                    var dataFormatada = ano + '-' + mes + '-' + dia;

                    html += '<tr>' +
                        '<td style="font-weight: 600; vertical-align: middle;">' + i + 'x</td>' +
                        '<td><input type="text" class="form-control form-control-sm parcela-valor" value="' + valorParcela.toFixed(2).replace('.', ',') + '"></td>' +
                        '<td><input type="date" class="form-control form-control-sm parcela-data" value="' + dataFormatada + '"></td>' +
                        '</tr>';

                    if (periodicidade === 'MENSAL') {
                        dataAtual.setMonth(dataAtual.getMonth() + 1);
                    } else if (periodicidade === 'SEMANAL') {
                        dataAtual.setDate(dataAtual.getDate() + 7);
                    } else if (periodicidade === 'ANUAL') {
                        dataAtual.setFullYear(dataAtual.getFullYear() + 1);
                    }
                }
                parcelasBody.innerHTML = html;
            }

            // Ativa o evento 'input' para atualizar instantaneamente ao digitar a quantidade
            if (totalParcelasInput) {
                totalParcelasInput.removeEventListener('input', gerar);
                totalParcelasInput.addEventListener('input', gerar);
            }
            if (primeiroVencimentoInput) {
                primeiroVencimentoInput.removeEventListener('change', gerar);
                primeiroVencimentoInput.addEventListener('change', gerar);
            }
            if (periodicidadeInput) {
                periodicidadeInput.removeEventListener('change', gerar);
                periodicidadeInput.addEventListener('change', gerar);
            }

            // Expõe o método de geração no elemento form caso precise ser acionado externamente
            form._gerarParcelasFinancas = gerar;

            gerar();
        }
    };
})();