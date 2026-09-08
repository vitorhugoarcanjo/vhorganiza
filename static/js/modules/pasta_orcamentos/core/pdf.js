// ==========================================================
// ORÇAMENTOS - PDF (GLOBAL)
// ==========================================================
// FUNÇÃO: Gerencia a geração de PDF para NOVO e EDITAR
//         Integra com VARIÁVEIS e TEMAS para personalização
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // GERAR PDF (GLOBAL)
    // ==========================================================
    function gerarPDF(id) {
        if (!id) {
            window.Notificacao.erro('ID do orçamento não encontrado!');
            return;
        }
        
        // Abre o PDF em nova aba
        window.open('/orcamentos/' + id + '/pdf', '_blank');
    }

    // ==========================================================
    // GERAR PDF DO NOVO
    // ==========================================================
    function gerarPDFNovo() {
        var titulo = document.getElementById('novoTitulo')?.value;
        if (!titulo || titulo.trim() === '') {
            window.Notificacao.erro('Preencha o título primeiro!');
            return;
        }

        // Verifica se já tem ID (orçamento salvo)
        var id = document.getElementById('novoId')?.value;
        if (id) {
            gerarPDF(id);
            return;
        }

        // 🔥 CRIA O ORÇAMENTO E DEPOIS GERA O PDF
        var btn = document.querySelector('#formNovoOrcamento button[type="submit"]');
        if (btn) {
            var form = document.getElementById('formNovoOrcamento');
            if (form) {
                var originalSubmit = form.onsubmit;
                form.onsubmit = function(e) {
                    e.preventDefault();
                    
                    var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
                    
                    fetch('/orcamentos/criar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            titulo: document.getElementById('novoTitulo').value,
                            cliente: document.getElementById('novoCliente').value,
                            status: document.getElementById('novoStatus').value,
                            estrutura: estrutura
                        })
                    })
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.success) {
                            document.getElementById('novoId').value = data.id;
                            gerarPDF(data.id);
                            if (window.fecharModalNovoOrcamento) {
                                window.fecharModalNovoOrcamento();
                            }
                            setTimeout(function() { window.location.reload(); }, 500);
                        } else {
                            window.Notificacao.erro(data.message);
                        }
                    })
                    .catch(function() {
                        window.Notificacao.erro('Erro ao criar orçamento');
                    });
                };
                form.submit();
                setTimeout(function() { form.onsubmit = originalSubmit; }, 100);
            }
        }
    }

    // ==========================================================
    // GERAR PDF DO PREVIEW (SEM SALVAR - NOVA FUNÇÃO)
    // ==========================================================
    function gerarPDFPreview() {
        var titulo = document.getElementById('novoTitulo')?.value;
        if (!titulo || titulo.trim() === '') {
            window.Notificacao.erro('Preencha o título primeiro!');
            return;
        }

        // Pega os dados do preview
        var orcamento = {
            titulo: titulo,
            cliente: document.getElementById('novoCliente')?.value || 'Não informado',
            data: document.getElementById('novoData')?.value ? 
                new Date(document.getElementById('novoData').value).toLocaleDateString('pt-BR') : 
                'Não informada',
            status: document.getElementById('novoStatus')?.value || 'rascunho'
        };
        
        var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
        
        // Gera o HTML do preview
        var html = window.OrcamentoPreview ? 
            window.OrcamentoPreview.renderizar(orcamento, estrutura) : 
            '';
        
        if (!html) {
            window.Notificacao.erro('Erro ao gerar preview do PDF');
            return;
        }
        
        // Abre em nova aba
        var win = window.open('', '_blank', 'width=1200,height=800');
        if (!win) {
            window.Notificacao.erro('Permita pop-ups para gerar o PDF');
            return;
        }
        
        win.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">');
        win.document.write('<title>PDF - ' + orcamento.titulo + '</title>');
        win.document.write('<style>');
        win.document.write('body { margin: 0; padding: 20px; background: #f1f5f9; }');
        win.document.write('.print-container { max-width: 1100px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }');
        win.document.write('@media print { body { padding: 0; background: #fff; } .print-container { box-shadow: none; padding: 20px; border-radius: 0; } }');
        win.document.write('</style>');
        win.document.write('</head><body>');
        win.document.write('<div class="print-container">');
        win.document.write(html);
        win.document.write('</div>');
        win.document.write('</body></html>');
        win.document.close();
        
        // Opcional: já abre o print
        setTimeout(function() {
            win.print();
        }, 500);
    }


    // ==========================================================
    // APLICAR VARIÁVEIS NO CSS DO PDF
    // ==========================================================
    function getPDFStyles() {
        var vars = window.OrcamentoVariaveis ? window.OrcamentoVariaveis.getVariaveis() : {};
        
        return `
            /* ========================================================== */
            /* PDF - ESTILOS COM VARIÁVEIS                                */
            /* ========================================================== */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: ${vars.fonte_corpo || 'Inter, sans-serif'}; 
                color: ${vars.cor_texto || '#1e293b'};
                background: ${vars.cor_fundo || '#ffffff'};
                line-height: ${vars.pdf_espacamento || 1.6};
            }
            .pdf-container {
                max-width: 1000px;
                margin: 0 auto;
                background: ${vars.cor_fundo || '#ffffff'};
                padding: 40px;
                border-radius: 8px;
            }
            
            /* CABEÇALHO */
            .pdf-header {
                text-align: center;
                border-bottom: 3px solid ${vars.cor_primaria || '#2563eb'};
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            .pdf-header h1 {
                font-size: 28px;
                font-weight: 800;
                color: ${vars.cor_primaria || '#2563eb'};
                letter-spacing: -0.5px;
                margin: 0;
            }
            .pdf-header .subtitulo {
                font-size: 16px;
                color: ${vars.cor_texto_claro || '#64748b'};
                margin-top: 4px;
            }
            .pdf-header .numero {
                font-size: 14px;
                color: ${vars.cor_texto_claro || '#94a3b8'};
                margin-top: 4px;
            }
            
            /* INFO */
            .pdf-info {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 16px;
                background: ${vars.cor_fundo_card || '#f8fafc'};
                padding: 16px 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                border: 1px solid ${vars.cor_borda || '#e2e8f0'};
            }
            .pdf-info-item .label {
                font-size: 11px;
                font-weight: 700;
                color: ${vars.cor_texto_claro || '#94a3b8'};
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            .pdf-info-item .value {
                font-size: 15px;
                font-weight: 600;
                color: ${vars.cor_texto || '#1e293b'};
                margin-top: 2px;
            }
            
            /* SEÇÕES */
            .pdf-secao {
                margin-bottom: 24px;
                border: 1px solid ${vars.cor_borda || '#e2e8f0'};
                border-radius: 8px;
                padding: 16px 20px;
            }
            .pdf-secao-titulo {
                font-size: 16px;
                font-weight: 700;
                color: ${vars.cor_primaria || '#2563eb'};
                border-bottom: 2px solid ${vars.cor_borda || '#e2e8f0'};
                padding-bottom: 8px;
                margin-bottom: 10px;
            }
            .pdf-secao-conteudo {
                font-size: 14px;
                color: ${vars.cor_texto || '#334155'};
                white-space: pre-wrap;
                line-height: 1.7;
            }
            
            /* CABEÇALHO (TIPO) */
            .pdf-secao-tipo-cabecalho {
                text-align: center;
                padding: 20px;
                border-bottom: 3px solid ${vars.cor_secundaria || '#8b5cf6'};
                margin-bottom: 24px;
            }
            .pdf-secao-tipo-cabecalho h2 {
                font-size: 22px;
                font-weight: 700;
                color: ${vars.cor_secundaria || '#8b5cf6'};
                margin: 0;
            }
            .pdf-secao-tipo-cabecalho p {
                font-size: 14px;
                color: ${vars.cor_texto_claro || '#64748b'};
                margin-top: 4px;
            }
            
            /* TABELA */
            .pdf-tabela {
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
                font-size: 13px;
            }
            .pdf-tabela th {
                background: ${vars.cor_fundo_card || '#f1f5f9'};
                font-weight: 600;
                padding: 8px 12px;
                border: 1px solid ${vars.cor_borda || '#e2e8f0'};
                text-align: left;
                color: ${vars.cor_texto || '#1e293b'};
            }
            .pdf-tabela td {
                padding: 8px 12px;
                border: 1px solid ${vars.cor_borda || '#e2e8f0'};
                color: ${vars.cor_texto || '#334155'};
            }
            
            /* LISTA */
            .pdf-lista {
                padding-left: 24px;
                margin: 8px 0;
            }
            .pdf-lista li {
                margin-bottom: 4px;
                font-size: 14px;
                color: ${vars.cor_texto || '#334155'};
            }
            
            /* DESTAQUE */
            .pdf-destaque {
                border: 2px solid ${vars.cor_alerta || '#ef4444'};
                border-radius: 8px;
                padding: 16px 20px;
                background: ${vars.cor_alerta + '15' || 'rgba(239,68,68,0.05)'};
                text-align: center;
                margin: 12px 0;
            }
            .pdf-destaque .titulo {
                font-weight: 700;
                font-size: 14px;
                color: ${vars.cor_alerta || '#ef4444'};
            }
            .pdf-destaque .conteudo {
                font-size: 18px;
                font-weight: 700;
                color: ${vars.cor_alerta || '#ef4444'};
                margin-top: 4px;
            }
            
            /* VALOR */
            .pdf-valor {
                border: 2px solid ${vars.cor_destaque || '#10b981'};
                border-radius: 8px;
                padding: 20px 24px;
                background: ${vars.cor_destaque + '0a' || 'rgba(16,185,129,0.05)'};
                text-align: center;
                margin: 12px 0;
            }
            .pdf-valor .titulo {
                font-weight: 700;
                font-size: 14px;
                color: ${vars.cor_destaque || '#10b981'};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .pdf-valor .itens {
                text-align: left;
                font-size: 13px;
                color: ${vars.cor_texto_claro || '#475569'};
                margin: 8px 0;
                padding: 8px 16px;
                background: ${vars.cor_fundo_card || '#f8fafc'};
                border-radius: 6px;
            }
            .pdf-valor .itens li {
                padding: 2px 0;
                list-style: none;
            }
            .pdf-valor .itens li strong {
                color: ${vars.cor_destaque || '#10b981'};
            }
            .pdf-valor .total {
                font-size: 28px;
                font-weight: 800;
                color: ${vars.cor_destaque || '#10b981'};
                padding: 8px 0;
                border-top: 2px solid ${vars.cor_destaque + '25' || 'rgba(16,185,129,0.15)'};
                margin-top: 8px;
            }
            .pdf-valor .descricao {
                font-size: 13px;
                color: ${vars.cor_texto_claro || '#64748b'};
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid ${vars.cor_destaque + '15' || 'rgba(16,185,129,0.15)'};
            }
            
            /* OBSERVAÇÃO */
            .pdf-observacao {
                background: ${vars.cor_fundo_card || '#f8fafc'};
                border-left: 3px solid ${vars.cor_texto_claro || '#6b7280'};
                padding: 12px 16px;
                border-radius: 4px;
                font-size: 13px;
                color: ${vars.cor_texto_claro || '#475569'};
                margin: 12px 0;
            }
            
            /* RODAPÉ */
            .pdf-footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid ${vars.cor_borda || '#e2e8f0'};
                font-size: 12px;
                color: ${vars.cor_texto_claro || '#94a3b8'};
            }
            
            /* RESPONSIVO */
            @media (max-width: 768px) {
                body { padding: 16px; }
                .pdf-container { padding: 16px; }
                .pdf-info { grid-template-columns: 1fr; gap: 8px; }
            }
        `;
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.gerarPDF = gerarPDF;
    window.gerarPDFNovo = gerarPDFNovo;
    window.gerarPDFPreview = gerarPDFPreview;
    window.getPDFStyles = getPDFStyles;

    console.log('✅ ORCAMENTO-PDF carregado!');

})();