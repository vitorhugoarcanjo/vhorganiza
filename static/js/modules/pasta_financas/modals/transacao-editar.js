// ==========================================================
// MODAL EDITAR TRANSAÇÃO
// ==========================================================

(function() {
    'use strict';

    var transacaoId = null;

    // ==========================================================
    // ABRIR MODAL
    // ==========================================================
    function abrirModalEditarTransacao(id) {
        console.log('🔓 Abrindo modal Editar Transação', id);
        transacaoId = id;
        
        var modal = document.getElementById('modalEditarTransacao');
        if (!modal) {
            console.error('❌ Modal não encontrado!');
            return;
        }

        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        var body = modal.querySelector('.fin-modal-body');
        if (body) {
            body.innerHTML = `
                <div style="text-align: center; padding: 30px; color: var(--texto-mutado);">
                    <div class="spinner-pure"></div>
                    <p style="margin-top: 10px;">Carregando dados...</p>
                </div>
            `;
        }

        // 🔥 PASSO 1: CARREGA O HTML DO MODAL (COM PREFIXO /financas/)
        fetch('/financas/edit_transacoes/' + id, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            return response.text();
        })
        .then(function(html) {
            if (html) {
                var modalBox = modal.querySelector('.fin-modal-box');
                if (modalBox) {
                    modalBox.innerHTML = html;
                }
                // 🔥 PASSO 2: CARREGA OS DADOS EM JSON (COM PREFIXO /financas/)
                carregarDados(id);
            }
        })
        .catch(function(error) {
            console.error('❌ Erro:', error);
            if (body) {
                body.innerHTML = '<div style="color: #ef4444; padding: 20px;">Erro ao carregar dados</div>';
            }
        });
    }

    // ==========================================================
    // CARREGAR DADOS (JSON)
    // ==========================================================
    function carregarDados(id) {
        // 🔥 COM PREFIXO /financas/
        fetch('/financas/edit_transacoes/dados/' + id, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) { return response.json(); })
        .then(function(result) {
            if (result.success) {
                if (result.data.sequencia && result.data.sequencia !== id) {
                    transacaoId = result.data.sequencia;
                    console.log('🔄 Redirecionado para o pai:', transacaoId);
                }
                preencherForm(result.data);
            } else {
                var body = document.querySelector('#modalEditarTransacao .fin-modal-body');
                if (body) {
                    body.innerHTML = '<div style="color: #ef4444; padding: 20px;">' + (result.error || 'Erro ao carregar dados') + '</div>';
                }
            }
        })
        .catch(function(error) {
            console.error('❌ Erro:', error);
            var body = document.querySelector('#modalEditarTransacao .fin-modal-body');
            if (body) {
                body.innerHTML = '<div style="color: #ef4444; padding: 20px;">Erro ao carregar dados</div>';
            }
        });
    }

    // ==========================================================
    // PREENCHER FORM
    // ==========================================================
    function preencherForm(data) {
        console.log('📦 Preenchendo form com:', data);

        var seqSpan = document.getElementById('finEditarSequencia');
        if (seqSpan) seqSpan.textContent = '#' + data.sequencia;

        var badge = document.getElementById('finEditarTipoBadge');
        if (badge) {
            if (data.tipo === 'receita') {
                badge.textContent = '📈 Receita';
                badge.className = 'fin-tipo-badge receita';
            } else if (data.tipo === 'despesa') {
                badge.textContent = '📉 Despesa';
                badge.className = 'fin-tipo-badge despesa';
            } else {
                badge.textContent = '📊 Selecionar';
                badge.className = 'fin-tipo-badge';
            }
        }

        var descricao = document.getElementById('descricaoInput');
        if (descricao) descricao.value = data.descricao || '';

        var valor = document.getElementById('valorTotal');
        if (valor) {
            var valorFormatado = parseFloat(data.valor_total).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            valor.value = valorFormatado;
        }

        var dataEmissao = document.getElementById('dataEmissao');
        if (dataEmissao) dataEmissao.value = data.data_emissao || '';

        var dataVencimento = document.getElementById('dataVencimento');
        if (dataVencimento) dataVencimento.value = data.data_vencimento || '';

        var categoria = document.getElementById('categoriaSelect');
        if (categoria) categoria.value = data.categoria_id || '';

        var totalParcelas = document.getElementById('totalParcelas');
        if (totalParcelas) totalParcelas.value = data.total_parcelas || 1;

        var intervaloDias = document.getElementById('intervaloDias');
        if (intervaloDias) intervaloDias.value = data.intervalo_dias || 30;

        var primeiroVencimento = document.getElementById('primeiroVencimento');
        if (primeiroVencimento) primeiroVencimento.value = data.data_vencimento || '';

        document.querySelectorAll('#form-transacao .tipo-btn').forEach(function(btn) {
            btn.classList.remove('active');
            if (btn.dataset.tipo === data.tipo) {
                btn.classList.add('active');
            }
        });

        var tipoHidden = document.getElementById('tipoHidden');
        if (tipoHidden) tipoHidden.value = data.tipo || '';

        var tbody = document.getElementById('parcelasBody');
        if (!tbody) return;

        if (data.parcelas && data.parcelas.length > 0) {
            var html = '';
            var numParcelas = data.parcelas.length;
            data.parcelas.forEach(function(p) {
                var valorFormatado = parseFloat(p.valor).toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
                html += '<tr>';
                html += '<td><strong>' + p.numero + '/' + numParcelas + '</strong></td>';
                html += '<td><input type="date" class="form-input data-parcela" value="' + p.data_vencimento + '" style="max-width: 140px;"></td>';
                html += '<td><input type="text" class="form-input valor-parcela-input" value="' + valorFormatado + '" style="max-width: 120px; text-align: right;"></td>';
                html += '</tr>';
            });
            tbody.innerHTML = html;

            document.getElementById('parcelasConfigArea').style.display = 'block';
            document.getElementById('parcelasWrapper').style.display = 'block';

            tbody.querySelectorAll('.valor-parcela-input').forEach(function(input) {
                input.addEventListener('input', function() {
                    if (typeof formatarValor === 'function') formatarValor(this);
                    if (typeof atualizarTotais === 'function') atualizarTotais();
                });
            });
            tbody.querySelectorAll('.data-parcela').forEach(function(input) {
                input.addEventListener('change', function() {
                    if (typeof atualizarTotais === 'function') atualizarTotais();
                });
            });
        } else {
            document.getElementById('parcelasConfigArea').style.display = 'none';
            document.getElementById('parcelasWrapper').style.display = 'none';
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
        }

        if (typeof atualizarTotais === 'function') {
            atualizarTotais();
        }
    }

    // ==========================================================
    // FECHAR MODAL
    // ==========================================================
    function fecharModalEditarTransacao() {
        console.log('🔒 Fechando modal Editar Transação');
        var modal = document.getElementById('modalEditarTransacao');
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
        document.body.style.overflow = '';
    }

    // ==========================================================
    // SALVAR
    // ==========================================================
    function salvarEditarTransacao() {
        var form = document.getElementById('form-transacao');
        if (!form) return;

        var btn = document.getElementById('btn-submit');
        if (!btn) return;

        var textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Salvando...';

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

        var formData = new FormData(form);
        var data = Object.fromEntries(formData.entries());
        data.parcelas = parcelas;

        // 🔥 COM PREFIXO /financas/
        fetch('/financas/edit_transacoes/' + transacaoId, {
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
                fecharModalEditarTransacao();
                setTimeout(function() { window.location.reload(); }, 500);
            } else {
                if (window.Notificacao) window.Notificacao.erro(result.message);
                btn.disabled = false;
                btn.innerHTML = textoOriginal;
            }
        })
        .catch(function(error) {
            console.error('❌ Erro:', error);
            if (window.Notificacao) window.Notificacao.erro('Erro ao salvar');
            btn.disabled = false;
            btn.innerHTML = textoOriginal;
        });
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.abrirModalEditarTransacao = abrirModalEditarTransacao;
    window.fecharModalEditarTransacao = fecharModalEditarTransacao;

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modal = document.getElementById('modalEditarTransacao');
            if (modal && modal.classList.contains('active')) {
                fecharModalEditarTransacao();
            }
        }
    });

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalEditarTransacao');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            fecharModalEditarTransacao();
        }
    });

    console.log('✅ MODAL EDITAR TRANSAÇÃO carregado!');

})();