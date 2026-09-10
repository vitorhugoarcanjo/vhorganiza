// ==========================================================
// FORMULÁRIO DE TRANSAÇÃO (LÓGICA E SUBMISSÃO)
// ==========================================================

(function() {
    'use strict';

    function initFormTransacao() {
        var form = document.getElementById('formNovaTransacao') || document.getElementById('form-transacao');
        if (!form) return;

        if (form.dataset.initialized === 'true') return;
        form.dataset.initialized = 'true';

        var valorTotalInput = document.getElementById('valorTotal');
        var totalParcelasInput = document.getElementById('totalParcelas');
        var tipoHidden = document.getElementById('tipoHidden');
        var finTipoBadge = document.getElementById('finTipoBadge');
        var parcelasConfigArea = document.getElementById('parcelasConfigArea');
        var parcelasWrapper = document.getElementById('parcelasWrapper');
        var parcelasBody = document.getElementById('parcelasBody');

        // Inicializa o módulo de parcelas externo de forma segura
        if (window.GeradorParcelasFinancas) {
            window.GeradorParcelasFinancas.init({ form: form });
        }

        function resetarFormulario() {
            form.reset();

            if (tipoHidden) tipoHidden.value = '';

            document.querySelectorAll('.tipo-btn').forEach(function(b) {
                b.classList.remove('active');
            });

            if (finTipoBadge) {
                finTipoBadge.textContent = '📊 Selecionar';
                finTipoBadge.className = 'fin-tipo-badge';
            }

            if (parcelasConfigArea) parcelasConfigArea.style.display = 'none';
            if (parcelasWrapper) parcelasWrapper.style.display = 'none';
            if (parcelasBody) parcelasBody.innerHTML = '';

            if (valorTotalInput) valorTotalInput.value = '0,00';
        }

        window.resetarFormularioTransacao = resetarFormulario;

        // 1. Alternar Tipo de Transação (Receita / Despesa)
        document.querySelectorAll('.tipo-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tipo-btn').forEach(function(b) {
                    b.classList.remove('active');
                });
                this.classList.add('active');

                var tipo = this.getAttribute('data-tipo');
                if (tipoHidden) tipoHidden.value = (tipo === 'vazio') ? '' : tipo;

                if (finTipoBadge) {
                    if (tipo === 'receita') {
                        finTipoBadge.textContent = '📈 Receita';
                        finTipoBadge.className = 'fin-tipo-badge receita';
                    } else if (tipo === 'despesa') {
                        finTipoBadge.textContent = '📉 Despesa';
                        finTipoBadge.className = 'fin-tipo-badge despesa';
                    } else {
                        finTipoBadge.textContent = '📊 Selecionar';
                        finTipoBadge.className = 'fin-tipo-badge';
                    }
                }
            });
        });

        // 2. Formatação Monetária e sincronização com as parcelas
        if (valorTotalInput) {
            valorTotalInput.addEventListener('input', function(e) {
                var value = e.target.value.replace(/\D/g, '');
                if (!value) {
                    e.target.value = '0,00';
                    if (typeof form._gerarParcelasFinancas === 'function') form._gerarParcelasFinancas();
                    return;
                }
                var floatVal = (parseFloat(value) / 100).toFixed(2);
                var parts = floatVal.split('.');
                parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                e.target.value = parts.join(',');

                if (typeof form._gerarParcelasFinancas === 'function') {
                    form._gerarParcelasFinancas();
                }
            });
        }

        // 3. Envio do Formulário via AJAX
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!tipoHidden || !tipoHidden.value) {
                if (window.Notificacao) {
                    window.Notificacao.aviso('Selecione o tipo de transação (Receita ou Despesa).');
                } else {
                    alert('Selecione o tipo de transação!');
                }
                return;
            }

            var strValor = (valorTotalInput ? valorTotalInput.value : '0,00').replace(/\./g, '').replace(',', '.');
            if (parseFloat(strValor) <= 0) {
                if (window.Notificacao) {
                    window.Notificacao.aviso('Informe um valor válido maior que zero.');
                } else {
                    alert('Informe um valor válido!');
                }
                return;
            }

            var formData = new FormData(form);
            var numParcelas = parseInt(totalParcelasInput ? totalParcelasInput.value : 1) || 1;

            if (numParcelas > 1 && parcelasBody) {
                var parcelasData = [];
                var rows = parcelasBody.querySelectorAll('tr');

                rows.forEach(function(row, idx) {
                    var inputVal = row.querySelector('.parcela-valor');
                    var inputData = row.querySelector('.parcela-data');

                    if (inputVal && inputData) {
                        var v = parseFloat(inputVal.value.replace(/\./g, '').replace(',', '.')) || 0;
                        parcelasData.push({
                            numero: idx + 1,
                            valor: v,
                            data_vencimento: inputData.value
                        });
                    }
                });

                formData.append('parcelas_detalhes', JSON.stringify(parcelasData));
            }

            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function(res) {
                return res.json().then(function(data) {
                    return { ok: res.ok, data: data };
                });
            })
            .then(function(result) {
                var data = result.data;

                if (!result.ok || data.success === false || data.sucesso === false) {
                    var msg = data.mensagem || data.erro || 'Ocorreu um erro ao salvar a transação.';
                    if (window.Notificacao) {
                        window.Notificacao.erro(msg);
                    } else {
                        alert(msg);
                    }
                    return;
                }

                if (window.Notificacao) {
                    window.Notificacao.sucesso(data.mensagem || 'Transação salva com sucesso!');
                }

                resetarFormulario();

                if (typeof window.fecharModalNovaTransacao === 'function') {
                    window.fecharModalNovaTransacao();
                }

                if (typeof window.carregarTransacoes === 'function') {
                    window.carregarTransacoes();
                } else if (window.htmx) {
                    htmx.ajax('GET', '/financas', '#tabela-container');
                } else {
                    setTimeout(function() { window.location.reload(); }, 1000);
                }
            })
            .catch(function(err) {
                console.error('❌ Erro no cadastro:', err);
                if (window.Notificacao) {
                    window.Notificacao.erro('Falha na comunicação com o servidor.');
                } else {
                    alert('Falha na comunicação com o servidor.');
                }
            })
            .finally(function() {
                if (submitBtn) submitBtn.disabled = false;
            });
        });

        // 4. Fechamento de Modal e Limpeza
        document.querySelectorAll('[data-dismiss="modal"], .btn-cancelar, [data-bs-dismiss="modal"]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                resetarFormulario();
            });
        });

        var modalElement = document.getElementById('modalNovaTransacao') || form.closest('.modal');
        if (modalElement && window.jQuery) {
            $(modalElement).on('hidden.bs.modal', function() {
                resetarFormulario();
            });
        } else if (modalElement) {
            modalElement.addEventListener('hidden.bs.modal', function() {
                resetarFormulario();
            });
        }

        console.log('✅ FORM TRANSAÇÃO inicializado!');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFormTransacao);
    } else {
        initFormTransacao();
    }
})();