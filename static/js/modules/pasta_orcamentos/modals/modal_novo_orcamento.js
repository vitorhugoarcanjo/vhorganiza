// ==========================================================
// ORÇAMENTOS - MODAL NOVO (SÓ CONFIGURA O NOVO)
// ==========================================================
// 
// 📌 FUNÇÃO: Gerencia o modal NOVO ORÇAMENTO
// 
// 🔧 O QUE FAZ:
//   - Abre/fecha o modal de novo orçamento
//   - Inicializa o gerenciador de seções com configurações do NOVO
//   - Gerencia o status badge
//   - Preview do orçamento completo
//   - Salva o orçamento via AJAX
// 
// 🎯 DIFERENÇA PARA O EDITAR:
//   - Usa IDs específicos do NOVO (com sufixo "Novo")
//   - Carrega seções vazias
//   - Não busca dados do banco
// 
// 📍 IDs UTILIZADOS (passados para o gerenciador):
//   - containerId: 'novo-secoes-container'
//   - previewContainerId: 'secaoPreviewContainer'
//   - contadorId: 'novoSecoesCount'
//   - modalSecaoId: 'modalNovaSecaoNovo'
//   - formSecaoId: 'formNovaSecaoNovo'
//   - tituloId: 'novaSecaoTituloNovo'
//   - conteudoId: 'novaSecaoConteudoNovo'
//   - camposEspecificosId: 'camposEspecificosNovo'
//   - tipoBtnsSelector: '#modalNovaSecaoNovo .orc-tipo-btn'
//   - modalTituloId: 'modalSecaoTituloNovo'
//   - btnTextoId: 'btnAdicionarTextoNovo'
// 
// 🌐 FUNÇÕES GLOBAIS EXPORTADAS:
//   - window.abrirModalNovoOrcamento
//   - window.fecharModalNovoOrcamento
//   - window.abrirModalNovaSecaoNovo
//   - window.fecharModalNovaSecaoNovo
//   - window.selecionarTipoNovo
//   - window.previewNovoOrcamento
//   - window.fecharPreview
// 
// ⚠️ ATENÇÃO: O gerenciador é inicializado apenas uma vez (singleton)
// ==========================================================
// ==========================================================
// ORÇAMENTOS - MODAL NOVO
// ==========================================================

// ==========================================================
// ORÇAMENTOS - MODAL NOVO (APENAS CONFIGURAÇÃO)
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
        
        // Limpar campos
        document.getElementById('novoTitulo').value = '';
        document.getElementById('novoCliente').value = '';
        document.getElementById('novoData').value = new Date().toISOString().split('T')[0];
        document.getElementById('novoStatus').value = 'rascunho';
        
        // Resetar template
        var select = document.getElementById('templateSelector');
        if (select) select.value = '';
        
        // 🔥 INICIALIZA O GERENCIADOR (USANDO O COMPARTILHADO)
        if (!window._gerenciadorNovo) {
            window._gerenciadorNovo = window.criarGerenciadorSecoes({
                containerId: 'novo-secoes-container',
                previewContainerId: 'secaoPreviewContainer',
                contadorId: 'novoSecoesCount',
                modalSecaoId: 'modalNovaSecao',  // ← MUDOU! USA O COMPARTILHADO
                formSecaoId: 'formNovaSecao',     // ← MUDOU! USA O COMPARTILHADO
                tituloId: 'novaSecaoTitulo',      // ← MUDOU! USA O COMPARTILHADO
                conteudoId: 'novaSecaoConteudo',  // ← MUDOU! USA O COMPARTILHADO
                camposEspecificosId: 'camposEspecificos', // ← MUDOU!
                tipoBtnsSelector: '#modalNovaSecao .orc-tipo-btn', // ← MUDOU!
                modalTituloId: 'modalSecaoTitulo', // ← MUDOU!
                btnTextoId: 'btnAdicionarTexto',   // ← MUDOU!
                contexto: 'novo'  // ← NOVO! IDENTIFICA O CONTEXTO
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
            var labels = { 'rascunho': '📝 Rascunho', 'enviado': '📤 Enviado', 'aprovado': '✅ Aprovado', 'rejeitado': '❌ Rejeitado' };
            badge.textContent = labels[status] || status;
            badge.className = 'orc-status-badge ' + status;
        }
    }

    // ==========================================================
    // FUNÇÕES GLOBAIS (CHAMADAS PELO HTML)
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
                titulo: document.getElementById('novoTitulo').value || 'Sem título',
                cliente: document.getElementById('novoCliente').value || 'Não informado',
                data: document.getElementById('novoData').value ? new Date(document.getElementById('novoData').value).toLocaleDateString('pt-BR') : 'Não informada',
                status: document.getElementById('novoStatus').value
            };
            var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
            if (window.SecoesPreview) {
                document.getElementById('previewContent').innerHTML = window.SecoesPreview.previewOrcamento(orcamento, estrutura);
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
    // CRIAR ORÇAMENTO
    // ==========================================================
    document.getElementById('formNovoOrcamento')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        var btn = document.getElementById('btnCriarOrcamento');
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Criando...';
        
        try {
            var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
            var response = await fetch('/orcamentos/criar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    titulo: document.getElementById('novoTitulo').value,
                    cliente: document.getElementById('novoCliente').value,
                    status: document.getElementById('novoStatus').value,
                    estrutura: estrutura
                })
            });
            var data = await response.json();
            if (data.success) {
                window.Notificacao.sucesso(data.message);
                fecharModalNovoOrcamento();
                setTimeout(function() { window.location.reload(); }, 500);
            } else {
                window.Notificacao.erro(data.message);
            }
        } catch (error) {
            console.error('❌ Erro:', error);
            window.Notificacao.erro('Erro ao criar orçamento');
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Criar Orçamento';
        }
    });

    // ==========================================================
    // GERAR PDF
    // ==========================================================
    window.gerarPDFNovo = function() {
        if (window.gerarPDF) {
            var id = document.getElementById('novoId')?.value;
            if (id) {
                window.gerarPDF(id);
            } else {
                window.Notificacao.erro('Salve o orçamento primeiro para gerar o PDF');
            }
        } else {
            window.Notificacao.erro('Função de PDF não disponível');
        }
    };

    console.log('✅ MODAL NOVO carregado!');

})();