// ==========================================================
// VARIÁVEIS - DADOS REUTILIZÁVEIS (COMPLETA)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // VARIÁVEIS PADRÃO (UNIFICADO)
    // ==========================================================
    var VARIAVEIS_PADRAO = {
        // ==========================================================
        // 1. CORES - PERSONALIZÁVEIS
        // ==========================================================
        cor_primaria: '#2563eb',
        cor_secundaria: '#3b82f6',
        cor_destaque: '#10b981',
        cor_alerta: '#ef4444',
        cor_texto: '#1e293b',
        cor_texto_claro: '#64748b',
        cor_fundo: '#ffffff',
        cor_fundo_card: '#f8fafc',
        cor_borda: '#e2e8f0',
        
        // ==========================================================
        // 2. FONTES
        // ==========================================================
        fonte_titulo: 'Inter, sans-serif',
        fonte_corpo: 'Inter, sans-serif',
        
        // ==========================================================
        // 3. CONFIGURAÇÕES DO PDF
        // ==========================================================
        pdf_margem: '20mm',
        pdf_tamanho_fonte: 12,
        pdf_espacamento: 1.6,
        
        // ==========================================================
        // 4. DADOS DA EMPRESA (ORIGINAL)
        // ==========================================================
        empresa_nome: 'VHORGANIZA',
        empresa_endereco: '',
        empresa_telefone: '',
        empresa_email: '',
        responsavel: 'Vitor Hugo',
        cargo_responsavel: 'Desenvolvedor',
        
        // ==========================================================
        // 5. OBSERVAÇÕES
        // ==========================================================
        observacao_padrao: 'Este orçamento tem validade de 30 dias.',
        moeda: 'R$'
    };

    // ==========================================================
    // VARIAVEIS ATUAIS (SALVAS NO LOCALSTORAGE)
    // ==========================================================
    function getVariaveis() {
        var salvas = localStorage.getItem('orcamento_variaveis');
        if (salvas) {
            try {
                // 🔥 FAZ MERGE COM O PADRÃO (CASO FALTE ALGUMA CHAVE)
                var salvasObj = JSON.parse(salvas);
                return Object.assign({}, VARIAVEIS_PADRAO, salvasObj);
            } catch (e) {
                return VARIAVEIS_PADRAO;
            }
        }
        return VARIAVEIS_PADRAO;
    }

    function setVariaveis(variaveis) {
        localStorage.setItem('orcamento_variaveis', JSON.stringify(variaveis));
    }

    function getVariavel(nome) {
        var variaveis = getVariaveis();
        return variaveis[nome] !== undefined ? variaveis[nome] : '';
    }

    function setVariavel(nome, valor) {
        var variaveis = getVariaveis();
        variaveis[nome] = valor;
        setVariaveis(variaveis);
    }

    // ==========================================================
    // RESETAR PARA O PADRÃO
    // ==========================================================
    function resetarVariaveis() {
        setVariaveis(VARIAVEIS_PADRAO);
        return VARIAVEIS_PADRAO;
    }

    // ==========================================================
    // APLICAR VARIÁVEIS NO CSS (CORES, FONTES)
    // ==========================================================
    function aplicarVariaveisCSS() {
        var vars = getVariaveis();
        var root = document.documentElement;
        
        // Aplica as cores como variáveis CSS
        root.style.setProperty('--orc-cor-primaria', vars.cor_primaria);
        root.style.setProperty('--orc-cor-secundaria', vars.cor_secundaria);
        root.style.setProperty('--orc-cor-destaque', vars.cor_destaque);
        root.style.setProperty('--orc-cor-alerta', vars.cor_alerta);
        root.style.setProperty('--orc-cor-texto', vars.cor_texto);
        root.style.setProperty('--orc-cor-texto-claro', vars.cor_texto_claro);
        root.style.setProperty('--orc-cor-fundo', vars.cor_fundo);
        root.style.setProperty('--orc-cor-fundo-card', vars.cor_fundo_card);
        root.style.setProperty('--orc-cor-borda', vars.cor_borda);
        
        // Aplica as fontes
        root.style.setProperty('--orc-fonte-titulo', vars.fonte_titulo);
        root.style.setProperty('--orc-fonte-corpo', vars.fonte_corpo);
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.OrcamentoVariaveis = {
        VARIAVEIS_PADRAO: VARIAVEIS_PADRAO,
        getVariaveis: getVariaveis,
        setVariaveis: setVariaveis,
        getVariavel: getVariavel,
        setVariavel: setVariavel,
        resetarVariaveis: resetarVariaveis,
        aplicarVariaveisCSS: aplicarVariaveisCSS
    };

    // 🔥 APLICA AS VARIÁVEIS AO CARREGAR
    aplicarVariaveisCSS();

    console.log('✅ ORCAMENTO-VARIAVEIS carregado!');

})();