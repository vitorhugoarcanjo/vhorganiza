// ==========================================================
// TEMAS - COMBINAÇÕES DE CORES
// ==========================================================

(function() {
    'use strict';

    var TEMAS = {
        // ==========================================================
        // TEMA 1: AZUL (PADRÃO)
        // ==========================================================
        azul: {
            id: 'azul',
            nome: '🔵 Azul',
            cores: {
                primaria: '#2563eb',
                secundaria: '#3b82f6',
                destaque: '#10b981',
                alerta: '#ef4444',
                texto: '#1e293b',
                texto_claro: '#64748b',
                fundo: '#ffffff',
                fundo_card: '#f8fafc',
                borda: '#e2e8f0'
            }
        },

        // ==========================================================
        // TEMA 2: VERDE
        // ==========================================================
        verde: {
            id: 'verde',
            nome: '🟢 Verde',
            cores: {
                primaria: '#059669',
                secundaria: '#10b981',
                destaque: '#22c55e',
                alerta: '#ef4444',
                texto: '#1e293b',
                texto_claro: '#64748b',
                fundo: '#ffffff',
                fundo_card: '#f0fdf4',
                borda: '#bbf7d0'
            }
        },

        // ==========================================================
        // TEMA 3: ROXO
        // ==========================================================
        roxo: {
            id: 'roxo',
            nome: '🟣 Roxo',
            cores: {
                primaria: '#7c3aed',
                secundaria: '#8b5cf6',
                destaque: '#22c55e',
                alerta: '#ef4444',
                texto: '#1e293b',
                texto_claro: '#64748b',
                fundo: '#ffffff',
                fundo_card: '#f5f3ff',
                borda: '#ddd6fe'
            }
        },

        // ==========================================================
        // TEMA 4: ESCURO (MODERNO)
        // ==========================================================
        escuro: {
            id: 'escuro',
            nome: '🌙 Escuro',
            cores: {
                primaria: '#8b5cf6',
                secundaria: '#7c3aed',
                destaque: '#22c55e',
                alerta: '#ef4444',
                texto: '#f1f5f9',
                texto_claro: '#94a3b8',
                fundo: '#0f172a',
                fundo_card: '#1e293b',
                borda: '#334155'
            }
        },

        // ==========================================================
        // TEMA 5: ROSA
        // ==========================================================
        rosa: {
            id: 'rosa',
            nome: '🌸 Rosa',
            cores: {
                primaria: '#db2777',
                secundaria: '#ec4899',
                destaque: '#22c55e',
                alerta: '#ef4444',
                texto: '#1e293b',
                texto_claro: '#64748b',
                fundo: '#ffffff',
                fundo_card: '#fdf2f8',
                borda: '#fbcfe8'
            }
        },

        // ==========================================================
        // TEMA 6: AMARELO (ENERGÉTICO)
        // ==========================================================
        amarelo: {
            id: 'amarelo',
            nome: '🟡 Amarelo',
            cores: {
                primaria: '#d97706',
                secundaria: '#f59e0b',
                destaque: '#22c55e',
                alerta: '#ef4444',
                texto: '#1e293b',
                texto_claro: '#64748b',
                fundo: '#ffffff',
                fundo_card: '#fffbeb',
                borda: '#fde68a'
            }
        }
    };

    // ==========================================================
    // FUNÇÕES
    // ==========================================================
    function getTema(id) {
        return TEMAS[id] || TEMAS.azul;
    }

    function getTemas() {
        return TEMAS;
    }

    function getTemasList() {
        var lista = [];
        Object.keys(TEMAS).forEach(function(key) {
            lista.push({
                id: TEMAS[key].id,
                nome: TEMAS[key].nome
            });
        });
        return lista;
    }

    function aplicarTema(id) {
        var tema = getTema(id);
        if (!tema) return false;

        var vars = window.OrcamentoVariaveis.getVariaveis();
        
        // Aplica as cores do tema
        Object.keys(tema.cores).forEach(function(key) {
            vars['cor_' + key] = tema.cores[key];
        });

        window.OrcamentoVariaveis.setVariaveis(vars);
        window.OrcamentoVariaveis.aplicarVariaveisCSS();

        return true;
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.OrcamentoTemas = {
        TEMAS: TEMAS,
        getTema: getTema,
        getTemas: getTemas,
        getTemasList: getTemasList,
        aplicarTema: aplicarTema
    };

    console.log('✅ ORCAMENTO-TEMAS carregado!');

})();