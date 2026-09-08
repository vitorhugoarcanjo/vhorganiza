// ==========================================================
// SEÇÕES - PREVIEW (GLOBAL)
// ==========================================================
// 
// 📌 FUNÇÃO: Gera o preview de uma seção em tempo real
// 
// 🔧 COMO USAR:
//   - Chamar SecoesPreview.previewSecao(dados)
//   - Chamar SecoesPreview.previewOrcamento(orcamento, estrutura)
// 
// 📝 PARÂMETROS:
//   - dados: { tipo, titulo, conteudo, ...campos específicos }
//   - orcamento: { titulo, cliente, data, status }
//   - estrutura: Array de objetos (as seções)
// 
// 🎯 O QUE FAZ:
//   - previewSecao: Usa o template do tipo definido em TIPOS_SECAO
//   - previewOrcamento: Monta o orçamento completo com todas as seções
// 
// 📍 ONDE É USADO:
//   - secoes-manager.js (atualizarPreview)
//   - modal_novo_orcamento.js (previewNovoOrcamento)
//   - modal_editar_orcamento.js (quando carrega dados)
// 
// 🏷️ CLASSES CSS UTILIZADAS (com prefixo orc-):
//   - .orc-secao-preview-valor, .orc-secao-preview-destaque, etc
//   - As classes são definidas no CSS e usadas pelos templates
// 
// 🚀 PARA ADICIONAR UM NOVO TIPO DE PREVIEW:
//   1. Vá em secoes-types.js
//   2. Adicione o novo tipo com seu template
//   3. O previewSecao automaticamente usará o novo template
// ==========================================================
(function() {
    'use strict';

    function previewSecao(dados) {
        var tipos = window.SecoesTypes ? window.SecoesTypes.TIPOS_SECAO : {};
        var tipoInfo = tipos[dados.tipo || 'secao'];
        if (!tipoInfo) return '<div class="orc-secao-preview-empty">Tipo inválido</div>';
        return tipoInfo.template(dados);
    }

    function previewOrcamento(orcamento, estrutura) {
        var titulo = orcamento.titulo || 'Sem título';
        var cliente = orcamento.cliente || 'Não informado';
        var data = orcamento.data || 'Não informada';
        var status = orcamento.status || 'rascunho';
        
        var statusLabels = {
            'rascunho': '📝 Rascunho',
            'enviado': '📤 Enviado',
            'aprovado': '✅ Aprovado',
            'rejeitado': '❌ Rejeitado'
        };
        
        var tipos = window.SecoesTypes ? window.SecoesTypes.TIPOS_SECAO : {};
        var secoesHtml = '';
        
        if (estrutura && estrutura.length > 0) {
            estrutura.forEach(function(secao) {
                var tipoInfo = tipos[secao.tipo || 'secao'];
                if (tipoInfo) secoesHtml += tipoInfo.template(secao);
            });
        }
        
        if (!secoesHtml) {
            secoesHtml = '<div class="orc-secao-preview-empty">Nenhuma seção adicionada</div>';
        }
        
        return `
            <div class="orc-preview-orcamento">
                <div class="orc-preview-header-orcamento">
                    <h1>ORÇAMENTO</h1>
                    <p>${titulo}</p>
                </div>
                <div class="orc-preview-info-orcamento">
                    <div><strong>Cliente:</strong> ${cliente}</div>
                    <div><strong>Data:</strong> ${data}</div>
                    <div><strong>Status:</strong> ${statusLabels[status] || status}</div>
                </div>
                <div class="orc-preview-secoes-orcamento">${secoesHtml}</div>
                <div class="orc-preview-footer-orcamento">Documento gerado em ${new Date().toLocaleString('pt-BR')}</div>
            </div>
        `;
    }

    window.SecoesPreview = {
        previewSecao: previewSecao,
        previewOrcamento: previewOrcamento
    };

    console.log('✅ SECOES-PREVIEW carregado!');

})();