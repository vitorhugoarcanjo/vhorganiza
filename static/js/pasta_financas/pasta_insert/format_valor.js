// Mascará para valor em reais
(function() {
    'use strict';
    
    function initMoneyMask() {
        const valorInput = document.querySelector('input[name="valor_total"]');
        if (!valorInput) return;
        
        // Muda de number para text
        valorInput.type = 'text';
        valorInput.placeholder = 'R$ 0,00';
        
        valorInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value === '') {
                this.value = '';
                return;
            }
            
            // Converte para centavos (ex: 1234 = R$ 12,34)
            let valorEmCentavos = parseInt(value);
            let reais = Math.floor(valorEmCentavos / 100);
            let centavos = valorEmCentavos % 100;
            
            // Formata com 2 casas decimais
            let formatted = reais.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            // Substitui os centavos (porque toLocaleString pode não funcionar 100% sozinho)
            formatted = formatted.replace(/\d+$/, String(centavos).padStart(2, '0'));
            
            this.value = formatted;
        });
    }
    
    // Inicializa quando o DOM carregar
    document.addEventListener('DOMContentLoaded', initMoneyMask);
})();