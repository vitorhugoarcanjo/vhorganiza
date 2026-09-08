// ==========================================================
// SEÇÕES - TIPOS E TEMPLATES (GLOBAL)
// ==========================================================
// 
// 📌 FUNÇÃO: Define todos os tipos de seção disponíveis no sistema
// 
// 🔧 COMO USAR:
//   - Adicione um novo tipo dentro do objeto TIPOS_SECAO
//   - Cada tipo deve ter: id, icone, nome, cor, campos, template
// 
// 📝 ESTRUTURA DE UM TIPO:
//   nome_do_tipo: {
//       id: 'identificador',        // ← Usado internamente
//       icone: '📝',                // ← Emoji do tipo
//       nome: 'Seção',              // ← Nome exibido no botão
//       cor: '#3b82f6',             // ← Cor do badge
//       campos: ['titulo', 'conteudo'], // ← Campos que este tipo usa
//       template: function(dados) { // ← Como o preview é renderizado
//           return `<div>...</div>`;
//       }
//   }
// 
// 📍 ONDE É USADO:
//   - secoes-render.js (para exibir os badges)
//   - secoes-preview.js (para renderizar o preview)
//   - secoes-manager.js (para saber quais campos mostrar)
// 
// ✅ TIPOS DISPONÍVEIS:
//   - secao:        📝 Seção (titulo + conteudo)
//   - cabecalho:    📄 Cabeçalho (titulo + conteudo centralizado)
//   - tabela:       📊 Tabela (titulo + colunas + linhas)
//   - lista:        📌 Lista (titulo + itens)
//   - destaque:     ⭐ Destaque (titulo + conteudo + cor)
//   - valor:        💰 Valor (titulo + conteudo + valor + descricao)
//   - observacao:   ℹ️ Observação (apenas conteudo)
// 
// 🚀 PARA ADICIONAR UM NOVO TIPO:
//   1. Copie a estrutura de um tipo existente
//   2. Altere id, icone, nome, cor
//   3. Defina os campos que ele vai usar
//   4. Crie o template HTML do preview
//   5. Depois vá em secoes-manager.js e adicione os campos específicos
// ==========================================================
(function() {
    'use strict';

    var TIPOS_SECAO = {
        secao: {
            id: 'secao',
            icone: '📝',
            nome: 'Seção',
            cor: '#3b82f6',
            campos: ['titulo', 'conteudo'],
            template: function(dados) {
                return `
                    <div class="orc-secao-preview-item">
                        <div class="orc-secao-preview-titulo" style="color: #3b82f6;">${dados.titulo || 'Seção'}</div>
                        <div class="orc-secao-preview-conteudo">${dados.conteudo || ''}</div>
                    </div>
                `;
            }
        },
        cabecalho: {
            id: 'cabecalho',
            icone: '📄',
            nome: 'Cabeçalho',
            cor: '#8b5cf6',
            campos: ['titulo', 'conteudo'],
            template: function(dados) {
                return `
                    <div class="orc-secao-preview-cabecalho">
                        <div class="orc-secao-preview-titulo-cabecalho">${dados.titulo || 'ORÇAMENTO'}</div>
                        <div class="orc-secao-preview-conteudo">${dados.conteudo || ''}</div>
                    </div>
                `;
            }
        },
        tabela: {
            id: 'tabela',
            icone: '📊',
            nome: 'Tabela',
            cor: '#10b981',
            campos: ['titulo', 'colunas', 'linhas'],
            template: function(dados) {
                var colunas = dados.colunas || [];
                var linhas = dados.linhas || [];
                var html = '<table class="orc-secao-preview-tabela"><thead><tr>';
                colunas.forEach(function(c) { html += '<th>' + c + '</th>'; });
                html += '</tr></thead><tbody>';
                linhas.forEach(function(linha) {
                    html += '<tr>';
                    linha.forEach(function(celula) { html += '<td>' + celula + '</td>'; });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                return `
                    <div class="orc-secao-preview-item">
                        <div class="orc-secao-preview-titulo" style="color: #10b981;">${dados.titulo || 'Tabela'}</div>
                        ${html}
                    </div>
                `;
            }
        },
        lista: {
            id: 'lista',
            icone: '📌',
            nome: 'Lista',
            cor: '#f59e0b',
            campos: ['titulo', 'itens'],
            template: function(dados) {
                var itens = dados.itens || [];
                var html = '<ul class="orc-secao-preview-lista">';
                itens.forEach(function(item) { html += '<li>' + item + '</li>'; });
                html += '</ul>';
                return `
                    <div class="orc-secao-preview-item">
                        <div class="orc-secao-preview-titulo" style="color: #f59e0b;">${dados.titulo || 'Lista'}</div>
                        ${html}
                    </div>
                `;
            }
        },
        destaque: {
            id: 'destaque',
            icone: '⭐',
            nome: 'Destaque',
            cor: '#ef4444',
            campos: ['titulo', 'conteudo', 'cor'],
            template: function(dados) {
                var cores = { azul: '#2563eb', verde: '#22c55e', vermelho: '#ef4444', amarelo: '#f59e0b' };
                var cor = cores[dados.cor || 'azul'] || '#2563eb';
                return `
                    <div class="orc-secao-preview-destaque" style="border-color: ${cor}; background: ${cor}15;">
                        <div class="orc-secao-preview-titulo-destaque" style="color: ${cor};">${dados.titulo || 'Destaque'}</div>
                        <div class="orc-secao-preview-conteudo-destaque">${dados.conteudo || ''}</div>
                    </div>
                `;
            }
        },
        valor: {
            id: 'valor',
            icone: '💰',
            nome: 'Valor',
            cor: '#10b981',
            campos: ['titulo', 'conteudo', 'valor', 'descricao_valor'],
            template: function(dados) {
                var conteudo = dados.conteudo || '';
                var valor = dados.valor || 'R$ 0,00';
                var descricao = dados.descricao_valor || '';
                if (valor && !valor.includes('R$')) {
                    valor = 'R$ ' + valor;
                }
                return `
                    <div class="orc-secao-preview-valor">
                        <div class="orc-secao-preview-titulo-valor">${dados.titulo || 'Valor'}</div>
                        ${conteudo ? '<div class="orc-secao-preview-conteudo-valor-texto">' + conteudo + '</div>' : ''}
                        <div class="orc-secao-preview-valor-destaque">${valor}</div>
                        ${descricao ? '<div class="orc-secao-preview-descricao-valor">' + descricao + '</div>' : ''}
                    </div>
                `;
            }
        },
        observacao: {
            id: 'observacao',
            icone: 'ℹ️',
            nome: 'Observação',
            cor: '#6b7280',
            campos: ['conteudo'],
            template: function(dados) {
                return `
                    <div class="orc-secao-preview-observacao">
                        <div class="orc-secao-preview-conteudo">${dados.conteudo || ''}</div>
                    </div>
                `;
            }
        }
    };

    window.SecoesTypes = { TIPOS_SECAO: TIPOS_SECAO };
    console.log('✅ SECOES-TYPES carregado!');

})();