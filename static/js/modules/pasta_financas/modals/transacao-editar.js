// ==========================================================
// MODAL EDITAR TRANSAÇÃO - DEFINITIVO
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

        // 🔥 ABRE O MODAL
        modal.classList.add('active');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // 🔥 MOSTRA LOADING (NÃO SUBSTITUI O HTML)
        var body = modal.querySelector('.fin-modal-body');
        if (body) {
            // 🔥 CRIA UM OVERLAY DE LOADING POR CIMA DO CONTEÚDO
            var loadingDiv = document.createElement('div');
            loadingDiv.id = 'editLoadingOverlay';
            loadingDiv.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                z-index: 10;
                border-radius: 8px;
            `;
            loadingDiv.innerHTML = `
                <div class="spinner-pure" style="width: 40px; height: 40px; border: 4px solid #fff; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <p style="color: #fff; margin-top: 10px;">Carregando dados...</p>
            `;
            // 🔥 USA POSITION RELATIVE NO BODY
            body.style.position = 'relative';
            body.appendChild(loadingDiv);
        }

        // 🔥 BUSCA OS DADOS EM JSON
        fetch('/financas/edit_transacoes/dados/' + id, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            return response.json();
        })
        .then(function(result) {
            if (result && result.success) {
                // 🔥 ATUALIZA O ID (SE FOR PARCELA, VAI SER O PAI)
                if (result.data.sequencia && result.data.sequencia !== id) {
                    transacaoId = result.data.sequencia;
                    console.log('🔄 ID atualizado para o pai:', transacaoId);
                }
                
                // 🔥 REMOVE O LOADING
                var overlay = document.getElementById('editLoadingOverlay');
                if (overlay) overlay.remove();

                // 🔥 PREENCHE OS CAMPOS (DIRETAMENTE, SEM RECARREGAR HTML)
                preencherForm(result.data);
            } else {
                if (body) {
                    body.innerHTML = '<div style="color: #ef4444; padding: 20px;">' + (result.error || 'Erro ao carregar dados') + '</div>';
                }
            }
        })
        .catch(function(error) {
            console.error('❌ Erro:', error);
            var overlay = document.getElementById('editLoadingOverlay');
            if (overlay) overlay.remove();
            if (body) {
                body.innerHTML = '<div style="color: #ef4444; padding: 20px;">Erro ao carregar dados</div>';
            }
        });
    }

    // ==========================================================
    // PREENCHER FORM (DIRETO, SEM RECARREGAR HTML)
    // ==========================================================
    function preencherForm(data) {
        console.log('📦 Preenchendo form com:', data);

        // 1. TÍTULO
        var seqSpan = document.getElementById('finEditarSequencia');
        if (seqSpan) seqSpan.textContent = '#' + data.sequencia;

        // 2. BADGE
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

        // 3. CAMPOS
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

        // 4. CATEGORIA
        var categoria = document.getElementById('categoriaSelect');
        if (categoria) {
            categoria.value = data.categoria_id || '';
        }

        // 5. PARCELAS
        var totalParcelas = document.getElementById('totalParcelas');
        if (totalParcelas) totalParcelas.value = data.total_parcelas || 1;

        var intervaloDias = document.getElementById('intervaloDias');
        if (intervaloDias) intervaloDias.value = data.intervalo_dias || 30;

        var primeiroVencimento = document.getElementById('primeiroVencimento');
        if (primeiroVencimento) primeiroVencimento.value = data.data_vencimento || '';

        // 6. TIPO
        document.querySelectorAll('#formEditarTransacao .tipo-btn').forEach(function(btn) {
            btn.classList.remove('active');
            if (btn.dataset.tipo === data.tipo) {
                btn.classList.add('active');
            }
        });

        var tipoHidden = document.getElementById('tipoHidden');
        if (tipoHidden) tipoHidden.value = data.tipo || '';

        // 7. PARCELAS FILHAS (CAMPO OCULTO)
        var parcelasData = document.getElementById('parcelasFilhasData');
        if (parcelasData) {
            parcelasData.value = JSON.stringify(data.parcelas || []);
        }

        // 8. DISPARA O CARREGAMENTO DAS PARCELAS
        if (data.total_parcelas > 1) {
            var event = new Event('change');
            document.getElementById('totalParcelas')?.dispatchEvent(event);
        }

        // 9. TOTAIS
        if (typeof window.atualizarTotais === 'function') {
            setTimeout(function() {
                window.atualizarTotais();
            }, 200);
        }

        console.log('✅ Form preenchido com sucesso!');
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
        var form = document.getElementById('formEditarTransacao');
        if (!form) return;

        var btn = document.querySelector('#footerFixoEditar .btn-footer-primary');
        if (!btn) return;

        var textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Salvando...';

        var formData = new FormData(form);
        var data = Object.fromEntries(formData.entries());

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

    // ESC
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