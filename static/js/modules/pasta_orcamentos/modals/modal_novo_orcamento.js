// static/js/modules/pasta_orcamentos/modals/modal_novo_orcamento.js
// ==========================================================
// ORÇAMENTOS - MODAL NOVO (padrão 2099)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // APLICAR TEMPLATE
    // ==========================================================
    function aplicarTemplate() {
        var select = document.getElementById('templateSelector');
        var templateId = select.value;

        if (!templateId) {
            window.Notificacao.aviso('Selecione um modelo primeiro!');
            return;
        }

        if (!window.OrcamentoTemplates) {
            window.Notificacao.erro('Sistema de templates não disponível!');
            return;
        }

        var template = window.OrcamentoTemplates.getTemplate(templateId);
        if (!template) {
            window.Notificacao.erro('Template não encontrado!');
            return;
        }

        var vars = window.OrcamentoTemplates.getTemplateVariaveisPadrao(templateId);
        var estrutura = window.OrcamentoTemplates.aplicarTemplate(templateId, vars);

        if (estrutura && estrutura.length > 0 && window._gerenciadorNovo) {
            window._gerenciadorNovo.carregarSecoes(estrutura);
            window.Notificacao.sucesso('Template "' + template.nome + '" aplicado!');
        } else {
            window.Notificacao.erro('Erro ao aplicar template');
        }
    }

    // ==========================================================
    // ABRIR MODAL NOVO
    // ==========================================================
    function abrirModalNovoOrcamento() {
        console.log('🔓 Abrindo modal NOVO');
        var modal = document.getElementById('modalNovoOrcamento');
        if (!modal) return;

        // Datas default (LOCAL — não UTC)
        function _dataLocalStr(date) {
            var ano = date.getFullYear();
            var mes = String(date.getMonth() + 1).padStart(2, '0');
            var dia = String(date.getDate()).padStart(2, '0');
            return ano + '-' + mes + '-' + dia;
        }

        var hoje = new Date();
        var hojeStr = _dataLocalStr(hoje);

        var validade = new Date(hoje);
        validade.setDate(validade.getDate() + 30);
        var validadeStr = _dataLocalStr(validade);

        // Limpar campos
        document.getElementById('novoTitulo').value = '';
        document.getElementById('novoCliente').value = '';
        document.getElementById('novoDataEmissao').value = hojeStr;
        document.getElementById('novoDataValidade').value = validadeStr;
        document.getElementById('novoDataEntrega').value = '';
        document.getElementById('novoStatus').value = 'rascunho';

        // Resetar template
        var select = document.getElementById('templateSelector');
        if (select) select.value = '';

        // 🔥 INICIALIZA O GERENCIADOR
        if (!window._gerenciadorNovo) {
            window._gerenciadorNovo = window.criarGerenciadorSecoes({
                containerId: 'novo-secoes-container',
                previewContainerId: 'secaoPreviewContainer',
                contadorId: 'novoSecoesCount',
                modalSecaoId: 'modalNovaSecao',
                formSecaoId: 'formNovaSecao',
                tituloId: 'novaSecaoTitulo',
                conteudoId: 'novaSecaoConteudo',
                camposEspecificosId: 'camposEspecificos',
                tipoBtnsSelector: '#modalNovaSecao .orc-tipo-btn',
                modalTituloId: 'modalSecaoTitulo',
                btnTextoId: 'btnAdicionarTexto',
                contexto: 'novo'
            });
            window._gerenciadorNovo.configurarFormSubmit();
        }

        // Carrega vazio
        window._gerenciadorNovo.carregarSecoes([]);

        // Atualiza status
        atualizarStatusPreview();

        // Abre modal
        modal.classList.add('active');
        setTimeout(function() { document.getElementById('novoTitulo').focus(); }, 100);
    }

    function fecharModalNovoOrcamento() {
        console.log('🔒 Fechando modal NOVO');
        var modal = document.getElementById('modalNovoOrcamento');
        if (modal) modal.classList.remove('active');
    }

    // ==========================================================
    // ATUALIZAR STATUS
    // ==========================================================
    function atualizarStatusPreview() {
        var select = document.getElementById('novoStatus');
        var badge = document.getElementById('novoStatusBadge');
        if (select && badge) {
            var status = select.value;
            var labels = {
                'rascunho':  '📝 Rascunho',
                'enviado':   '📤 Enviado',
                'aprovado':  '✅ Aprovado',
                'rejeitado': '❌ Rejeitado'
            };
            badge.textContent = labels[status] || status;
            badge.className = 'orc-status-badge ' + status;
        }
    }

    // ==========================================================
    // EXPORTA GLOBAIS
    // ==========================================================
    window.abrirModalNovoOrcamento = abrirModalNovoOrcamento;
    window.fecharModalNovoOrcamento = fecharModalNovoOrcamento;
    window.aplicarTemplate = aplicarTemplate;

    // ==========================================================
    // PREVIEW
    // ==========================================================
    window.previewNovoOrcamento = function() {
        if (window.OrcamentoPreview) {
            window.OrcamentoPreview.novo();
        } else {
            var orcamento = {
                titulo:        document.getElementById('novoTitulo').value || 'Sem título',
                cliente:       document.getElementById('novoCliente').value || 'Não informado',
                data_emissao:  document.getElementById('novoDataEmissao').value,
                data_validade: document.getElementById('novoDataValidade').value,
                data_entrega:  document.getElementById('novoDataEntrega').value,
                status:        document.getElementById('novoStatus').value
            };
            var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
            if (window.SecoesPreview) {
                document.getElementById('previewContent').innerHTML =
                    window.SecoesPreview.previewOrcamento(orcamento, estrutura);
            }
            document.getElementById('modalPreview').classList.add('active');
        }
    };

    window.fecharPreview = function() {
        if (window.OrcamentoPreview) {
            window.OrcamentoPreview.fechar();
        } else {
            document.getElementById('modalPreview').classList.remove('active');
        }
    };

    // ==========================================================
    // SUBMIT — CRIAR ORÇAMENTO
    // ==========================================================
    document.getElementById('formNovoOrcamento')?.addEventListener('submit', async function(e) {
        e.preventDefault();

        var btn = document.getElementById('btnCriarOrcamento');
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Criando...';

        try {
            var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];

            var payload = {
                titulo:        document.getElementById('novoTitulo').value,
                cliente:       document.getElementById('novoCliente').value,
                status:        document.getElementById('novoStatus').value,
                data_emissao:  document.getElementById('novoDataEmissao').value || null,
                data_validade: document.getElementById('novoDataValidade').value || null,
                data_entrega:  document.getElementById('novoDataEntrega').value || null,
                estrutura:     estrutura
            };

            var response = await fetch('/orcamentos/criar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            var data = await response.json();

            if (data.success) {
                window.Notificacao.sucesso(data.message);
                fecharModalNovoOrcamento();

                // 🔥 Padrão 2099 — recarrega SÓ a tabela via HTMX
                if (window.htmx) {
                    window.htmx.ajax('GET', '/orcamentos/', {
                        target: '#tabela-container',
                        swap: 'outerHTML'
                    });
                } else {
                    window.location.reload();
                }
            } else {
                // Validação backend campo-a-campo
                if (data.errors && data.errors.length) {
                    var msgs = data.errors.map(function(er) { return '• ' + er.mensagem; }).join('\n');
                    window.Notificacao.erro(msgs);
                } else {
                    window.Notificacao.erro(data.message || 'Erro ao criar orçamento');
                }
            }
        } catch (error) {
            console.error('❌ Erro:', error);
            window.Notificacao.erro('Erro ao criar orçamento');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle"></i> Criar Orçamento';
        }
    });

    console.log('✅ MODAL NOVO carregado!');

})();