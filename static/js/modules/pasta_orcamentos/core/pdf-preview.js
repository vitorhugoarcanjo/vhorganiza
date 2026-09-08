// ==========================================================
// ORÇAMENTOS - PREVIEW (GLOBAL)
// ==========================================================
// FUNÇÃO: Gerencia a visualização do orçamento para NOVO e EDITAR
//         Integra com VARIÁVEIS e TEMAS para personalização
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // RENDERIZAR PREVIEW (COM VARIÁVEIS)
    // ==========================================================
    function renderizarPreview(orcamento, estrutura) {
        var vars = window.OrcamentoVariaveis ? window.OrcamentoVariaveis.getVariaveis() : {};
        var styles = window.getPDFStyles ? window.getPDFStyles() : '';
        
        var html = renderOrcamentoHTML(orcamento, estrutura, vars);
        
        var htmlCompleto = `
            <style>${styles}</style>
            <div class="pdf-container">
                ${html}
            </div>
        `;
        
        return htmlCompleto;
    }

    // ==========================================================
    // GERAR HTML DO ORÇAMENTO
    // ==========================================================
    function renderOrcamentoHTML(orcamento, estrutura, vars) {
        var titulo = orcamento.titulo || 'Sem título';
        var cliente = orcamento.cliente || 'Não informado';
        var data = orcamento.data || 'Não informada';
        var status = orcamento.status || 'rascunho';
        var moeda = vars.moeda || 'R$';
        
        var statusLabels = {
            'rascunho': 'Rascunho',
            'enviado': 'Enviado',
            'aprovado': 'Aprovado',
            'rejeitado': 'Rejeitado'
        };
        
        var html = `
            <div class="pdf-header">
                <h1>ORÇAMENTO</h1>
                <div class="subtitulo">${titulo}</div>
                <div class="numero">${new Date().toLocaleDateString('pt-BR')}</div>
            </div>
            <div class="pdf-info">
                <div class="pdf-info-item">
                    <span class="label">Cliente</span>
                    <span class="value">${cliente}</span>
                </div>
                <div class="pdf-info-item">
                    <span class="label">Status</span>
                    <span class="value">${statusLabels[status] || status}</span>
                </div>
                <div class="pdf-info-item">
                    <span class="label">Data</span>
                    <span class="value">${data}</span>
                </div>
            </div>
        `;
        
        if (estrutura && estrutura.length > 0) {
            estrutura.forEach(function(secao) {
                var tipo = secao.tipo || 'secao';
                
                if (tipo === 'cabecalho') {
                    html += `
                        <div class="pdf-secao-tipo-cabecalho">
                            <h2>${secao.titulo || 'ORÇAMENTO'}</h2>
                            <p>${secao.conteudo || ''}</p>
                        </div>
                    `;
                } else if (tipo === 'secao') {
                    html += `
                        <div class="pdf-secao">
                            <div class="pdf-secao-titulo">${secao.titulo || 'Seção'}</div>
                            <div class="pdf-secao-conteudo">${secao.conteudo || ''}</div>
                        </div>
                    `;
                } else if (tipo === 'tabela') {
                    var colunas = secao.colunas || [];
                    var linhas = secao.linhas || [];
                    var tabelaHtml = '<table class="pdf-tabela"><thead><tr>';
                    colunas.forEach(function(c) {
                        tabelaHtml += '<th>' + c + '</th>';
                    });
                    tabelaHtml += '</tr></thead><tbody>';
                    linhas.forEach(function(linha) {
                        tabelaHtml += '<tr>';
                        linha.forEach(function(celula) {
                            tabelaHtml += '<td>' + celula + '</td>';
                        });
                        tabelaHtml += '</tr>';
                    });
                    tabelaHtml += '</tbody></table>';
                    html += `
                        <div class="pdf-secao">
                            <div class="pdf-secao-titulo">${secao.titulo || 'Tabela'}</div>
                            ${tabelaHtml}
                        </div>
                    `;
                } else if (tipo === 'lista' || tipo === 'numerada') {
                    var itens = secao.itens || [];
                    var listaHtml = '<ul class="pdf-lista">';
                    itens.forEach(function(item) {
                        listaHtml += '<li>' + item + '</li>';
                    });
                    listaHtml += '</ul>';
                    html += `
                        <div class="pdf-secao">
                            <div class="pdf-secao-titulo">${secao.titulo || 'Lista'}</div>
                            ${listaHtml}
                        </div>
                    `;
                } else if (tipo === 'destaque') {
                    html += `
                        <div class="pdf-destaque">
                            <div class="titulo">${secao.titulo || 'Destaque'}</div>
                            <div class="conteudo">${secao.conteudo || ''}</div>
                        </div>
                    `;
                } else if (tipo === 'valor') {
                    var valor = secao.valor || 'R$ 0,00';
                    if (valor && !valor.includes(moeda)) {
                        valor = moeda + ' ' + valor;
                    }
                    var itensValor = secao.conteudo || '';
                    var itensHtml = '';
                    if (itensValor) {
                        itensHtml = '<div class="itens">';
                        itensValor.split('\n').forEach(function(linha) {
                            if (linha.trim()) {
                                itensHtml += '<li>' + linha.replace(/(R\$|R$|R\s*\$)[\s]*([\d.,]+)/g, '<strong>$1 $2</strong>') + '</li>';
                            }
                        });
                        itensHtml += '</div>';
                    }
                    html += `
                        <div class="pdf-valor">
                            <div class="titulo">${secao.titulo || 'Valor'}</div>
                            ${itensHtml}
                            <div class="total">${valor}</div>
                            ${secao.descricao_valor ? '<div class="descricao">' + secao.descricao_valor + '</div>' : ''}
                        </div>
                    `;
                } else if (tipo === 'observacao') {
                    html += `
                        <div class="pdf-observacao">
                            ${secao.conteudo || ''}
                        </div>
                    `;
                } else {
                    html += `
                        <div class="pdf-secao">
                            <div class="pdf-secao-titulo">${secao.titulo || 'Seção'}</div>
                            <div class="pdf-secao-conteudo">${secao.conteudo || ''}</div>
                        </div>
                    `;
                }
            });
        } else {
            html += '<div class="secoes-vazio">Nenhuma seção adicionada.</div>';
        }
        
        html += `
            <div class="pdf-footer">
                Documento gerado em ${new Date().toLocaleString('pt-BR')}
            </div>
        `;
        
        return html;
    }

    // ==========================================================
    // ABRIR PREVIEW
    // ==========================================================
    function abrirPreview(orcamento, estrutura) {
        var html = renderizarPreview(orcamento, estrutura);
        var content = document.getElementById('previewContent');
        if (content) {
            content.innerHTML = html;
        }
        document.getElementById('modalPreview').classList.add('active');
    }

    // ==========================================================
    // FECHAR PREVIEW
    // ==========================================================
    function fecharPreview() {
        document.getElementById('modalPreview').classList.remove('active');
    }

    // ==========================================================
    // PREVIEW DO NOVO
    // ==========================================================
    function previewNovoOrcamento() {
        var orcamento = {
            titulo: document.getElementById('novoTitulo').value || 'Sem título',
            cliente: document.getElementById('novoCliente').value || 'Não informado',
            data: document.getElementById('novoData').value ? new Date(document.getElementById('novoData').value).toLocaleDateString('pt-BR') : 'Não informada',
            status: document.getElementById('novoStatus').value
        };
        var estrutura = window._gerenciadorNovo ? window._gerenciadorNovo.getEstrutura() : [];
        abrirPreview(orcamento, estrutura);
    }

    // ==========================================================
    // PREVIEW DO EDITAR
    // ==========================================================
    function previewEditarOrcamento() {
        var orcamento = {
            titulo: document.getElementById('editOrcamentoTitulo').value || 'Sem título',
            cliente: document.getElementById('editOrcamentoCliente').value || 'Não informado',
            data: document.getElementById('editOrcamentoData').value ? new Date(document.getElementById('editOrcamentoData').value).toLocaleDateString('pt-BR') : 'Não informada',
            status: document.getElementById('editOrcamentoStatus').value
        };
        var estrutura = window._gerenciadorEditar ? window._gerenciadorEditar.getEstrutura() : [];
        abrirPreview(orcamento, estrutura);
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.OrcamentoPreview = {
        abrir: abrirPreview,
        fechar: fecharPreview,
        novo: previewNovoOrcamento,
        editar: previewEditarOrcamento,
        renderizar: renderizarPreview
    };

    window.previewNovoOrcamento = previewNovoOrcamento;
    window.fecharPreview = fecharPreview;

    console.log('✅ ORCAMENTO-PREVIEW carregado!');

})();