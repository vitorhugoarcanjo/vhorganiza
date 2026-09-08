// ==========================================================
// ORÇAMENTOS - MODAL EDITAR (SÓ CONFIGURA O EDITAR)
// ==========================================================
// 
// 📌 FUNÇÃO: Gerencia o modal EDITAR ORÇAMENTO
// 
// 🔧 O QUE FAZ:
//   - Abre/fecha o modal de edição
//   - Busca dados do orçamento via AJAX (/orcamentos/{id}/dados)
//   - Inicializa o gerenciador de seções com configurações do EDITAR
//   - Carrega as seções existentes
//   - Salva o orçamento via AJAX (/orcamentos/{id}/salvar-estrutura)
//   - Gera PDF
// 
// 🎯 DIFERENÇA PARA O NOVO:
//   - Usa IDs específicos do EDITAR (sem sufixo)
//   - Busca dados do banco antes de abrir
//   - Mostra loading enquanto carrega
// 
// 📍 IDs UTILIZADOS (passados para o gerenciador):
//   - containerId: 'secoes-container-modal'
//   - previewContainerId: 'secaoPreviewContainer'
//   - contadorId: 'secoesCount'
//   - modalSecaoId: 'modalNovaSecao'
//   - formSecaoId: 'formNovaSecao'
//   - tituloId: 'novaSecaoTitulo'
//   - conteudoId: 'novaSecaoConteudo'
//   - camposEspecificosId: 'camposEspecificos'
//   - tipoBtnsSelector: '#modalNovaSecao .orc-tipo-btn'
//   - modalTituloId: 'modalSecaoTitulo'
//   - btnTextoId: 'btnAdicionarTexto'
// 
// 🌐 FUNÇÕES GLOBAIS EXPORTADAS:
//   - window.abrirModalEditar
//   - window.fecharModalEditar
//   - window.abrirModalNovaSecao
//   - window.fecharModalNovaSecao
//   - window.selecionarTipo
//   - window.gerarPDFModal
//   - window.visualizarOrcamentoModal
// 
// ⚠️ ATENÇÃO: O gerenciador é inicializado apenas uma vez (singleton)
// ==========================================================
// ==========================================================
// ORÇAMENTOS - MODAL EDITAR (SÓ CONFIGURA O EDITAR)
// ==========================================================

(function() {
    'use strict';

    var orcamentoId = null;

    function abrirModalEditar(id) {
        console.log('🔓 Abrindo modal EDITAR', id);
        var modal = document.getElementById('modalEditarOrcamento');
        if (!modal) return;

        orcamentoId = id;

        var container = document.getElementById('secoes-container-modal');
        if (container) {
            container.innerHTML = `
                <div class="secoes-loading">
                    <div class="spinner"></div>
                    <p>Carregando...</p>
                </div>
            `;
        }

        // 🔥 INICIALIZA O GERENCIADOR (USANDO O COMPARTILHADO)
        if (!window._gerenciadorEditar) {
            window._gerenciadorEditar = window.criarGerenciadorSecoes({
                containerId: 'secoes-container-modal',
                previewContainerId: 'secaoPreviewContainer',
                contadorId: 'secoesCount',
                modalSecaoId: 'modalNovaSecao',     // ← COMPARTILHADO
                formSecaoId: 'formNovaSecao',        // ← COMPARTILHADO
                tituloId: 'novaSecaoTitulo',         // ← COMPARTILHADO
                conteudoId: 'novaSecaoConteudo',     // ← COMPARTILHADO
                camposEspecificosId: 'camposEspecificos', // ← COMPARTILHADO
                tipoBtnsSelector: '#modalNovaSecao .orc-tipo-btn', // ← COMPARTILHADO
                modalTituloId: 'modalSecaoTitulo',   // ← COMPARTILHADO
                btnTextoId: 'btnAdicionarTexto',     // ← COMPARTILHADO
                contexto: 'editar'  // ← IDENTIFICA O CONTEXTO
            });
            window._gerenciadorEditar.configurarFormSubmit();
        }

        // Busca dados do orçamento
        fetch('/orcamentos/' + id + '/dados')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    document.getElementById('editOrcamentoId').value = data.id;
                    document.getElementById('editOrcamentoTitulo').value = data.titulo;
                    document.getElementById('editOrcamentoCliente').value = data.cliente || '';
                    document.getElementById('editOrcamentoStatus').value = data.status || 'rascunho';
                    document.getElementById('editOrcamentoData').value = data.created_at || '';

                    atualizarStatusBadge();

                    // 🔥 VERIFICA SE TEM SEÇÕES
                    var estrutura = data.estrutura || [];
                    
                    // 🔥 SE NÃO TIVER SEÇÕES, CARREGA UM TEMPLATE
                    if (!estrutura || estrutura.length === 0) {
                        console.log('📋 Nenhuma seção encontrada. Carregando template padrão...');
                        
                        var templateId = 'simples';
                        var template = window.OrcamentoTemplates ? window.OrcamentoTemplates.getTemplate(templateId) : null;
                        
                        if (template) {
                            var vars = window.OrcamentoTemplates.getTemplateVariaveisPadrao(templateId);
                            estrutura = window.OrcamentoTemplates.aplicarTemplate(templateId, vars) || [];
                            console.log('✅ Template "' + templateId + '" aplicado com ' + estrutura.length + ' seções');
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
            var labels = { 'rascunho': '📝 Rascunho', 'enviado': '📤 Enviado', 'aprovado': '✅ Aprovado', 'rejeitado': '❌ Rejeitado' };
            badge.textContent = labels[status] || status;
            badge.className = 'orc-badge-status ' + status;
        }
    }
    window.atualizarStatusBadge = atualizarStatusBadge;

    // ==========================================================
    // PREVIEW
    // ==========================================================
    window.visualizarOrcamentoModal = function() {
        if (window.OrcamentoPreview) {
            window.OrcamentoPreview.editar();
        } else {
            var orcamento = {
                titulo: document.getElementById('editOrcamentoTitulo').value || 'Sem título',
                cliente: document.getElementById('editOrcamentoCliente').value || 'Não informado',
                data: document.getElementById('editOrcamentoData').value ? new Date(document.getElementById('editOrcamentoData').value).toLocaleDateString('pt-BR') : 'Não informada',
                status: document.getElementById('editOrcamentoStatus').value
            };
            var estrutura = window._gerenciadorEditar ? window._gerenciadorEditar.getEstrutura() : [];
            if (window.SecoesPreview) {
                document.getElementById('previewContent').innerHTML = window.SecoesPreview.previewOrcamento(orcamento, estrutura);
            }
            document.getElementById('modalPreview').classList.add('active');
        }
    };

    // ==========================================================
    // GERAR PDF
    // ==========================================================
    window.gerarPDFModal = function() {
        if (orcamentoId && window.gerarPDF) {
            window.gerarPDF(orcamentoId);
        } else {
            window.Notificacao.erro('ID do orçamento não encontrado!');
        }
    };

    // ==========================================================
    // SALVAR ORÇAMENTO
    // ==========================================================
    document.getElementById('formEditarOrcamento')?.addEventListener('submit', async function(e) {
        e.preventDefault();

        var btn = document.getElementById('btnSalvarOrcamento');
        var textoOriginal = btn.innerHTML;

        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Salvando...';

        try {
            var estrutura = window._gerenciadorEditar ? window._gerenciadorEditar.getEstrutura() : [];
            var response = await fetch('/orcamentos/' + orcamentoId + '/salvar-estrutura', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    titulo: document.getElementById('editOrcamentoTitulo').value,
                    cliente: document.getElementById('editOrcamentoCliente').value,
                    status: document.getElementById('editOrcamentoStatus').value,
                    estrutura: estrutura
                })
            });
            var data = await response.json();
            if (data.success) {
                window.Notificacao.sucesso(data.message);
                fecharModalEditar();
                setTimeout(function() { window.location.reload(); }, 500);
            } else {
                window.Notificacao.erro(data.message);
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