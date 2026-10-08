// static/js/modules/pasta_orcamentos/modals/modal_editar_orcamento.js
// ==========================================================
// ORÇAMENTOS - MODAL EDITAR (padrão 2099)
// ==========================================================

(function() {
    'use strict';

    var orcamentoId = null;

    // ==========================================================
    // MAPA DE IDs (campo backend → input frontend)
    // ==========================================================
    var MAPA_IDS = {
        'titulo':        'editOrcamentoTitulo',
        'cliente':       'editOrcamentoCliente',
        'status':        'editOrcamentoStatus',
        'data_emissao':  'editOrcamentoDataEmissao',
        'data_validade': 'editOrcamentoDataValidade',
        'data_entrega':  'editOrcamentoDataEntrega',
    };

    // ==========================================================
    // MOSTRAR ERROS CAMPO-A-CAMPO
    // ==========================================================
    function mostrarErrosForm(errors) {
        document.querySelectorAll('.campo-erro').forEach(el => el.classList.remove('campo-erro'));
        document.querySelectorAll('.msg-erro-campo').forEach(el => el.remove());

        errors.forEach(function(er) {
            var inputId = MAPA_IDS[er.campo];
            if (!inputId) return;

            var input = document.getElementById(inputId);
            if (!input) return;

            input.classList.add('campo-erro');

            var msg = document.createElement('span');
            msg.className = 'msg-erro-campo';
            msg.textContent = er.mensagem;
            input.parentNode.appendChild(msg);
        });
    }

    function limparErrosForm() {
        document.querySelectorAll('.campo-erro').forEach(el => el.classList.remove('campo-erro'));
        document.querySelectorAll('.msg-erro-campo').forEach(el => el.remove());
    }

    // ==========================================================
    // ABRIR MODAL EDITAR
    // ==========================================================
    function abrirModalEditar(sequencia) {
        console.log('🔓 Abrindo modal EDITAR', sequencia);
        var modal = document.getElementById('modalEditarOrcamento');
        if (!modal) return;

        // Guarda a SEQUÊNCIA (não id)
        window.orcamentoSequencia = sequencia;

        var container = document.getElementById('secoes-container-modal');
        if (container) {
            container.innerHTML = `
                <div class="secoes-loading">
                    <div class="spinner"></div>
                    <p>Carregando...</p>
                </div>
            `;
        }

        // Inicializa gerenciador
        if (!window._gerenciadorEditar) {
            window._gerenciadorEditar = window.criarGerenciadorSecoes({
                containerId: 'secoes-container-modal',
                previewContainerId: 'secaoPreviewContainer',
                contadorId: 'secoesCount',
                modalSecaoId: 'modalNovaSecao',
                formSecaoId: 'formNovaSecao',
                tituloId: 'novaSecaoTitulo',
                conteudoId: 'novaSecaoConteudo',
                camposEspecificosId: 'camposEspecificos',
                tipoBtnsSelector: '#modalNovaSecao .orc-tipo-btn',
                modalTituloId: 'modalSecaoTitulo',
                btnTextoId: 'btnAdicionarTexto',
                contexto: 'editar'
            });
            window._gerenciadorEditar.configurarFormSubmit();
        }

        // Busca por SEQUÊNCIA
        fetch('/orcamentos/' + sequencia + '/dados')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    orcamentoId = data.id;

                    document.getElementById('editOrcamentoId').value = data.id;
                    document.getElementById('editOrcamentoTitulo').value = data.titulo;
                    document.getElementById('editOrcamentoCliente').value = data.cliente || '';
                    document.getElementById('editOrcamentoStatus').value = data.status || 'rascunho';

                    // 🔥 3 DATAS
                    document.getElementById('editOrcamentoDataEmissao').value  = data.data_emissao  || '';
                    document.getElementById('editOrcamentoDataValidade').value = data.data_validade || '';
                    document.getElementById('editOrcamentoDataEntrega').value  = data.data_entrega  || '';

                    atualizarStatusBadge();
                    limparErrosForm();

                    var estrutura = data.estrutura || [];

                    if (!estrutura || estrutura.length === 0) {
                        console.log('📋 Nenhuma seção. Carregando template padrão...');
                        var templateId = 'simples';
                        var template = window.OrcamentoTemplates ? window.OrcamentoTemplates.getTemplate(templateId) : null;
                        if (template) {
                            var vars = window.OrcamentoTemplates.getTemplateVariaveisPadrao(templateId);
                            estrutura = window.OrcamentoTemplates.aplicarTemplate(templateId, vars) || [];
                        }
                    }

                    window._gerenciadorEditar.carregarSecoes(estrutura);
                    modal.classList.add('active');

                } else {
                    window.Notificacao.erro(data.message);
                }
            })
            .catch(function() {
                window.Notificacao.erro('Erro ao carregar dados');
                if (container) {
                    container.innerHTML = `
                        <div class="secoes-vazio">
                            <i class="bi bi-exclamation-triangle"></i>
                            <p>Erro ao carregar seções</p>
                        </div>
                    `;
                }
            });
    }

    function fecharModalEditar() {
        var modal = document.getElementById('modalEditarOrcamento');
        if (modal) modal.classList.remove('active');
    }

    // ==========================================================
    // FUNÇÕES GLOBAIS
    // ==========================================================
    window.abrirModalEditar = abrirModalEditar;
    window.fecharModalEditar = fecharModalEditar;

    // ==========================================================
    // ATUALIZAR STATUS
    // ==========================================================
    function atualizarStatusBadge() {
        var select = document.getElementById('editOrcamentoStatus');
        var badge = document.getElementById('modalEditStatus');
        if (select && badge) {
            var status = select.value;
            var labels = {
                'rascunho':  '📝 Rascunho',
                'enviado':   '📤 Enviado',
                'aprovado':  '✅ Aprovado',
                'rejeitado': '❌ Rejeitado'
            };
            badge.textContent = labels[status] || status;
            badge.className = 'orc-badge-status ' + status;
        }
    }
    window.atualizarStatusBadge = atualizarStatusBadge;

    // ==========================================================
    // SALVAR ORÇAMENTO
    // ==========================================================
    document.getElementById('formEditarOrcamento')?.addEventListener('submit', async function(e) {
        e.preventDefault();

        var btn = document.getElementById('btnSalvarOrcamento');
        var textoOriginal = btn.innerHTML;

        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Salvando...';

        limparErrosForm();

        try {
            var estrutura = window._gerenciadorEditar ? window._gerenciadorEditar.getEstrutura() : [];
            var sequencia = window.orcamentoSequencia;

            var payload = {
                titulo:        document.getElementById('editOrcamentoTitulo').value,
                cliente:       document.getElementById('editOrcamentoCliente').value,
                status:        document.getElementById('editOrcamentoStatus').value,
                data_emissao:  document.getElementById('editOrcamentoDataEmissao').value  || null,
                data_validade: document.getElementById('editOrcamentoDataValidade').value || null,
                data_entrega:  document.getElementById('editOrcamentoDataEntrega').value  || null,
                estrutura:     estrutura
            };

            // URL nova (sequência + /editar)
            var response = await fetch('/orcamentos/' + sequencia + '/editar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            var data = await response.json();

            if (data.success) {
                window.Notificacao.sucesso(data.message);
                fecharModalEditar();

                // Padrão 2099 — recarrega só a tabela
                if (window.htmx) {
                    window.htmx.ajax('GET', '/orcamentos/', {
                        target: '#tabela-container',
                        swap: 'outerHTML'
                    });
                } else {
                    window.location.reload();
                }
            } else {
                if (data.errors && data.errors.length) {
                    mostrarErrosForm(data.errors);
                    window.Notificacao.erro('Corrija os campos em vermelho.');
                } else {
                    window.Notificacao.erro(data.message || 'Erro ao salvar orçamento');
                }
            }
        } catch (error) {
            console.error('❌ Erro:', error);
            window.Notificacao.erro('Erro ao salvar orçamento');
        } finally {
            btn.disabled = false;
            btn.innerHTML = textoOriginal;
        }
    });

    console.log('✅ MODAL EDITAR carregado!');

})();