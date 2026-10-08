// static/js/modules/pasta_orcamentos/core/pdf.js
// ==========================================================
// ORÇAMENTOS - PDF (GLOBAL)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // GERAR PDF (GLOBAL)
    // Abre o PDF do orçamento JÁ SALVO em nova aba
    // ==========================================================
    function gerarPDF(sequencia) {
        if (!sequencia) {
            window.Notificacao.erro('Orçamento não encontrado!');
            return;
        }
        window.open('/orcamentos/' + sequencia + '/pdf', '_blank');
    }

    // ==========================================================
    // ESTILOS DO PREVIEW (com variáveis)
    // Usado pelo pdf-preview.js
    // ==========================================================
    function getPDFStyles() {
        var vars = window.OrcamentoVariaveis ? window.OrcamentoVariaveis.getVariaveis() : {};

        return `
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: ${vars.fonte_corpo || 'Inter, sans-serif'};
                color: ${vars.cor_texto || '#1e293b'};
                background: ${vars.cor_fundo || '#ffffff'};
                line-height: ${vars.pdf_espacamento || 1.6};
            }
            .pdf-container { max-width: 1000px; margin: 0 auto; background: ${vars.cor_fundo || '#ffffff'}; padding: 40px; border-radius: 8px; }
            .pdf-header { text-align: center; border-bottom: 3px solid ${vars.cor_primaria || '#2563eb'}; padding-bottom: 20px; margin-bottom: 30px; }
            .pdf-header h1 { font-size: 28px; font-weight: 800; color: ${vars.cor_primaria || '#2563eb'}; margin: 0; }
            .pdf-header .subtitulo { font-size: 16px; color: ${vars.cor_texto_claro || '#64748b'}; margin-top: 4px; }
            .pdf-header .numero { font-size: 14px; color: ${vars.cor_texto_claro || '#94a3b8'}; margin-top: 4px; }
            .pdf-info { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; background: ${vars.cor_fundo_card || '#f8fafc'}; padding: 16px 20px; border-radius: 8px; margin-bottom: 30px; border: 1px solid ${vars.cor_borda || '#e2e8f0'}; }
            .pdf-info-item .label { font-size: 11px; font-weight: 700; color: ${vars.cor_texto_claro || '#94a3b8'}; text-transform: uppercase; display: block; }
            .pdf-info-item .value { font-size: 15px; font-weight: 600; color: ${vars.cor_texto || '#1e293b'}; margin-top: 2px; display: block; }
            .pdf-secao { margin-bottom: 24px; border: 1px solid ${vars.cor_borda || '#e2e8f0'}; border-radius: 8px; padding: 16px 20px; }
            .pdf-secao-titulo { font-size: 16px; font-weight: 700; color: ${vars.cor_primaria || '#2563eb'}; border-bottom: 2px solid ${vars.cor_borda || '#e2e8f0'}; padding-bottom: 8px; margin-bottom: 10px; }
            .pdf-secao-conteudo { font-size: 14px; color: ${vars.cor_texto || '#334155'}; white-space: pre-wrap; line-height: 1.7; }
            .pdf-secao-tipo-cabecalho { text-align: center; padding: 20px; border-bottom: 3px solid ${vars.cor_secundaria || '#8b5cf6'}; margin-bottom: 24px; }
            .pdf-secao-tipo-cabecalho h2 { font-size: 22px; font-weight: 700; color: ${vars.cor_secundaria || '#8b5cf6'}; margin: 0; }
            .pdf-secao-tipo-cabecalho p { font-size: 14px; color: ${vars.cor_texto_claro || '#64748b'}; margin-top: 4px; }
            .pdf-tabela { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
            .pdf-tabela th { background: ${vars.cor_fundo_card || '#f1f5f9'}; font-weight: 600; padding: 8px 12px; border: 1px solid ${vars.cor_borda || '#e2e8f0'}; text-align: left; }
            .pdf-tabela td { padding: 8px 12px; border: 1px solid ${vars.cor_borda || '#e2e8f0'}; }
            .pdf-lista { padding-left: 24px; margin: 8px 0; }
            .pdf-lista li { margin-bottom: 4px; font-size: 14px; }
            .pdf-destaque { border: 2px solid ${vars.cor_alerta || '#ef4444'}; border-radius: 8px; padding: 16px 20px; text-align: center; margin: 12px 0; }
            .pdf-destaque .titulo { font-weight: 700; font-size: 14px; color: ${vars.cor_alerta || '#ef4444'}; }
            .pdf-destaque .conteudo { font-size: 18px; font-weight: 700; color: ${vars.cor_alerta || '#ef4444'}; margin-top: 4px; }
            .pdf-valor { border: 2px solid ${vars.cor_destaque || '#10b981'}; border-radius: 8px; padding: 20px 24px; text-align: center; margin: 12px 0; }
            .pdf-valor .titulo { font-weight: 700; font-size: 14px; color: ${vars.cor_destaque || '#10b981'}; text-transform: uppercase; }
            .pdf-valor .itens { text-align: left; font-size: 13px; margin: 8px 0; padding: 8px 16px; background: ${vars.cor_fundo_card || '#f8fafc'}; border-radius: 6px; list-style: none; }
            .pdf-valor .itens li { padding: 2px 0; }
            .pdf-valor .total { font-size: 28px; font-weight: 800; color: ${vars.cor_destaque || '#10b981'}; padding: 8px 0; border-top: 2px solid ${vars.cor_destaque || '#10b981'}25; margin-top: 8px; }
            .pdf-valor .descricao { font-size: 13px; color: ${vars.cor_texto_claro || '#64748b'}; margin-top: 6px; padding-top: 6px; border-top: 1px solid ${vars.cor_destaque || '#10b981'}15; }
            .pdf-observacao { background: ${vars.cor_fundo_card || '#f8fafc'}; border-left: 3px solid ${vars.cor_texto_claro || '#6b7280'}; padding: 12px 16px; border-radius: 4px; font-size: 13px; color: ${vars.cor_texto_claro || '#475569'}; margin: 12px 0; }
            .pdf-footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px solid ${vars.cor_borda || '#e2e8f0'}; font-size: 12px; color: ${vars.cor_texto_claro || '#94a3b8'}; }
        `;
    }

    // Exporta
    window.gerarPDF = gerarPDF;
    window.getPDFStyles = getPDFStyles;

    console.log('✅ ORCAMENTO-PDF carregado!');

})();