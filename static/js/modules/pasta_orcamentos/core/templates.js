// ==========================================================
// TEMPLATES - MODELOS DE ORÇAMENTO PRONTOS
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // TEMPLATES DISPONÍVEIS
    // ==========================================================
    var TEMPLATES = {
        // ==========================================================
        // TEMPLATE 1: SIMPLES
        // ==========================================================
        simples: {
            id: 'simples',
            nome: '📄 Simples',
            descricao: 'Orçamento básico com título, descrição e valor',
            estrutura: [
                {
                    tipo: 'cabecalho',
                    titulo: 'ORÇAMENTO',
                    conteudo: '{{titulo}}'
                },
                {
                    tipo: 'secao',
                    titulo: '1. DESCRIÇÃO DO PROJETO',
                    conteudo: '{{descricao}}'
                },
                {
                    tipo: 'valor',
                    titulo: '2. VALOR',
                    conteudo: '{{itens_valor}}',
                    valor: '{{valor_total}}',
                    descricao_valor: '{{descricao_valor}}'
                },
                {
                    tipo: 'observacao',
                    conteudo: '{{observacao}}'
                }
            ]
        },

        // ==========================================================
        // TEMPLATE 2: DETALHADO
        // ==========================================================
        detalhado: {
            id: 'detalhado',
            nome: '📋 Detalhado',
            descricao: 'Com escopo, entregáveis, prazo e valor',
            estrutura: [
                {
                    tipo: 'cabecalho',
                    titulo: 'ORÇAMENTO',
                    conteudo: '{{titulo}}'
                },
                {
                    tipo: 'secao',
                    titulo: '1. OBJETIVO',
                    conteudo: '{{objetivo}}'
                },
                {
                    tipo: 'lista',
                    titulo: '2. ENTREGÁVEIS',
                    itens: '{{entregaveis}}'
                },
                {
                    tipo: 'lista',
                    titulo: '3. PRAZOS',
                    itens: '{{prazos}}'
                },
                {
                    tipo: 'valor',
                    titulo: '4. VALOR',
                    conteudo: '{{itens_valor}}',
                    valor: '{{valor_total}}',
                    descricao_valor: '{{descricao_valor}}'
                },
                {
                    tipo: 'observacao',
                    conteudo: '{{observacao}}'
                }
            ]
        },

        // ==========================================================
        // TEMPLATE 3: TÉCNICO (COM TABELAS)
        // ==========================================================
        tecnico: {
            id: 'tecnico',
            nome: '📊 Técnico',
            descricao: 'Com tabelas de especificações',
            estrutura: [
                {
                    tipo: 'cabecalho',
                    titulo: 'ORÇAMENTO TÉCNICO',
                    conteudo: '{{titulo}}'
                },
                {
                    tipo: 'secao',
                    titulo: '1. ESPECIFICAÇÕES TÉCNICAS',
                    conteudo: '{{especificacoes}}'
                },
                {
                    tipo: 'tabela',
                    titulo: '2. ITENS',
                    colunas: ['Item', 'Qtd', 'Valor Unit.', 'Valor Total'],
                    linhas: '{{tabela_itens}}'
                },
                {
                    tipo: 'valor',
                    titulo: '3. VALOR TOTAL',
                    conteudo: '{{itens_valor}}',
                    valor: '{{valor_total}}',
                    descricao_valor: '{{descricao_valor}}'
                }
            ]
        },

        // ==========================================================
        // TEMPLATE 4: PROPOSTA COMERCIAL
        // ==========================================================
        comercial: {
            id: 'comercial',
            nome: '💼 Comercial',
            descricao: 'Proposta comercial com benefícios e condições',
            estrutura: [
                {
                    tipo: 'cabecalho',
                    titulo: 'PROPOSTA COMERCIAL',
                    conteudo: '{{titulo}}'
                },
                {
                    tipo: 'secao',
                    titulo: '1. SOBRE A EMPRESA',
                    conteudo: '{{sobre_empresa}}'
                },
                {
                    tipo: 'lista',
                    titulo: '2. BENEFÍCIOS',
                    itens: '{{beneficios}}'
                },
                {
                    tipo: 'tabela',
                    titulo: '3. CONDIÇÕES',
                    colunas: ['Descrição', 'Valor', 'Prazo'],
                    linhas: '{{condicoes}}'
                },
                {
                    tipo: 'valor',
                    titulo: '4. INVESTIMENTO',
                    conteudo: '{{itens_valor}}',
                    valor: '{{valor_total}}',
                    descricao_valor: '{{descricao_valor}}'
                },
                {
                    tipo: 'observacao',
                    conteudo: '{{observacao}}'
                }
            ]
        },

        // ==========================================================
        // TEMPLATE 5: PROJETO (PARA DESENVOLVIMENTO)
        // ==========================================================
        projeto: {
            id: 'projeto',
            nome: '🚀 Projeto',
            descricao: 'Para projetos de desenvolvimento com fases',
            estrutura: [
                {
                    tipo: 'cabecalho',
                    titulo: 'PROJETO',
                    conteudo: '{{titulo}}'
                },
                {
                    tipo: 'secao',
                    titulo: '1. VISÃO GERAL',
                    conteudo: '{{visao_geral}}'
                },
                {
                    tipo: 'lista',
                    titulo: '2. FASES DO PROJETO',
                    itens: '{{fases}}'
                },
                {
                    tipo: 'tabela',
                    titulo: '3. CRONOGRAMA',
                    colunas: ['Fase', 'Início', 'Fim', 'Status'],
                    linhas: '{{cronograma}}'
                },
                {
                    tipo: 'valor',
                    titulo: '4. VALOR TOTAL',
                    conteudo: '{{itens_valor}}',
                    valor: '{{valor_total}}',
                    descricao_valor: '{{descricao_valor}}'
                }
            ]
        }
    };

    // ==========================================================
    // FUNÇÕES
    // ==========================================================
    function getTemplate(id) {
        return TEMPLATES[id] || null;
    }

    function getTemplates() {
        return TEMPLATES;
    }

    function getTemplatesList() {
        var lista = [];
        Object.keys(TEMPLATES).forEach(function(key) {
            lista.push({
                id: TEMPLATES[key].id,
                nome: TEMPLATES[key].nome,
                descricao: TEMPLATES[key].descricao
            });
        });
        return lista;
    }

    // ==========================================================
    // SUBSTITUIR VARIÁVEIS
    // ==========================================================
    function substituirVariaveis(texto, variaveis) {
        return texto.replace(/\{\{(\w+)\}\}/g, function(match, nome) {
            if (variaveis[nome] !== undefined) {
                if (Array.isArray(variaveis[nome])) {
                    return variaveis[nome].join('\n');
                }
                return variaveis[nome];
            }
            return match;
        });
    }

    // ==========================================================
    // APLICAR TEMPLATE (CORRIGIDO)
    // ==========================================================
    function aplicarTemplate(id, variaveis) {
        var template = getTemplate(id);
        if (!template) return null;

        // Clona a estrutura
        var estrutura = JSON.parse(JSON.stringify(template.estrutura));
        
        estrutura.forEach(function(secao) {
            Object.keys(secao).forEach(function(key) {
                var valor = secao[key];
                
                // 1. String com variáveis
                if (typeof valor === 'string' && valor.includes('{{')) {
                    secao[key] = substituirVariaveis(valor, variaveis);
                }
                
                // 2. Array com variáveis
                if (Array.isArray(valor)) {
                    secao[key] = valor.map(function(item) {
                        if (typeof item === 'string' && item.includes('{{')) {
                            return substituirVariaveis(item, variaveis);
                        }
                        return item;
                    });
                }
                
                // 3. 🔥 ESPECIAL: Linhas da tabela (string com '|')
                if (key === 'linhas' && typeof secao[key] === 'string') {
                    var linhas = secao[key];
                    // Se tiver quebra de linha e pipe, converte pra array de arrays
                    if (linhas.includes('\n') && linhas.includes('|')) {
                        secao[key] = linhas.split('\n')
                            .filter(function(l) { return l.trim(); })
                            .map(function(linha) {
                                return linha.split('|').map(function(c) { return c.trim(); });
                            });
                    }
                    // Se tiver quebra de linha mas sem pipe, converte pra array
                    else if (linhas.includes('\n')) {
                        secao[key] = linhas.split('\n').filter(function(l) { return l.trim(); });
                    }
                }
                
                // 4. 🔥 ESPECIAL: Itens de lista (string com quebra de linha)
                if ((key === 'itens' || key === 'entregaveis' || key === 'prazos' || 
                     key === 'beneficios' || key === 'fases' || key === 'condicoes') && 
                    typeof secao[key] === 'string' && secao[key].includes('\n')) {
                    secao[key] = secao[key].split('\n').filter(function(i) { return i.trim(); });
                }
                
                // 5. 🔥 ESPECIAL: Colunas (string com vírgula)
                if (key === 'colunas' && typeof secao[key] === 'string' && secao[key].includes(',')) {
                    secao[key] = secao[key].split(',').map(function(c) { return c.trim(); });
                }
            });
        });

        return estrutura;
    }

    // ==========================================================
    // PREENCHE VARIÁVEIS DO TEMPLATE
    // ==========================================================
    function getTemplateVariaveisPadrao(id) {
        var template = getTemplate(id);
        if (!template) return {};

        var vars = {};
        var estruturaStr = JSON.stringify(template.estrutura);
        var matches = estruturaStr.match(/\{\{(\w+)\}\}/g) || [];
        
        var valoresPadrao = {
            'titulo': 'Novo Orçamento',
            'descricao': 'Descrição detalhada do projeto...',
            'objetivo': 'Este projeto tem como objetivo...',
            'entregaveis': ['Entregável 1: Descrição', 'Entregável 2: Descrição', 'Entregável 3: Descrição'],
            'prazos': ['Etapa 1: 30 dias', 'Etapa 2: 60 dias', 'Etapa 3: 90 dias'],
            'especificacoes': 'Especificações técnicas do projeto...',
            'tabela_itens': ['Item 1 | 1 | R$ 100,00 | R$ 100,00', 'Item 2 | 2 | R$ 50,00 | R$ 100,00'],
            'itens_valor': 'Item 1: R$ 100,00\nItem 2: R$ 50,00',
            'valor_total': 'R$ 150,00',
            'descricao_valor': 'Valor total do projeto',
            'observacao': 'Este orçamento tem validade de 30 dias.',
            'sobre_empresa': 'Empresa especializada em...',
            'beneficios': ['Benefício 1', 'Benefício 2', 'Benefício 3'],
            'condicoes': ['Condição 1 | R$ 100,00 | 30 dias', 'Condição 2 | R$ 50,00 | 60 dias'],
            'visao_geral': 'Visão geral do projeto...',
            'fases': ['Fase 1: Análise', 'Fase 2: Desenvolvimento', 'Fase 3: Entrega'],
            'cronograma': ['Fase 1 | 01/01 | 15/01 | Em andamento', 'Fase 2 | 16/01 | 30/01 | Pendente']
        };
        
        matches.forEach(function(match) {
            var nome = match.replace(/\{\{|\}\}/g, '');
            vars[nome] = valoresPadrao[nome] || '';
        });

        return vars;
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.OrcamentoTemplates = {
        TEMPLATES: TEMPLATES,
        getTemplate: getTemplate,
        getTemplates: getTemplates,
        getTemplatesList: getTemplatesList,
        aplicarTemplate: aplicarTemplate,
        getTemplateVariaveisPadrao: getTemplateVariaveisPadrao
    };

    console.log('✅ ORCAMENTO-TEMPLATES carregado!');

})();