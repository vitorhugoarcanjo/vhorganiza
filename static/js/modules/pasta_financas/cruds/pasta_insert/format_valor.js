// ==========================================
// MASCARA DE DINHEIRO (REUTILIZÁVEL)
// ==========================================

(function() {
    'use strict';
    
    /**
     * Aplica máscara de dinheiro em um input
     * @param {HTMLElement} input - O elemento input
     */
    function aplicarMascaraDinheiro(input) {
        if (!input) return;
        
        // Formata valor inicial se tiver
        let valorAtual = input.value;
        if (valorAtual && !isNaN(parseFloat(valorAtual))) {
            let numero = parseFloat(valorAtual);
            input.value = 'R$ ' + numero.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        // Evento de digitação
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            
            if (value === '') {
                this.value = '';
                return;
            }
            
            let numero = parseFloat(value) / 100;
            this.value = 'R$ ' + numero.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        });
        
        // Evento de blur (perder foco)
        input.addEventListener('blur', function() {
            if (this.value === '') return;
            
            let cleanValue = this.value.replace('R$', '').trim();
            let numero = parseFloat(cleanValue.replace(/\./g, '').replace(',', '.'));
            if (!isNaN(numero)) {
                this.value = 'R$ ' + numero.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        });
    }
    
    /**
     * Inicializa todos os inputs de dinheiro
     * @param {string} seletor - Seletor CSS (padrão: '.money-input')
     */
    function initMoneyMask(seletor = '.money-input') {
        document.querySelectorAll(seletor).forEach(input => {
            aplicarMascaraDinheiro(input);
        });
    }
    
    // 🔥 EXPÕE PARA USO GLOBAL
    window.initMoneyMask = initMoneyMask;
    window.aplicarMascaraDinheiro = aplicarMascaraDinheiro;
    
    // 🔥 INICIALIZA AUTOMATICAMENTE
    document.addEventListener('DOMContentLoaded', function() {
        initMoneyMask();
    });
    
})();