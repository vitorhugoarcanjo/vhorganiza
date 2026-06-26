// Mascará para valor em reais com R$ na frente
(function() {
    'use strict';
    
    function initMoneyMask() {
        const valorInput = document.querySelector('input[name="valor_total"]');
        if (!valorInput) return;
        
        // Se já tiver um valor, formata ele primeiro
        let valorAtual = valorInput.value;
        if (valorAtual && !isNaN(parseFloat(valorAtual))) {
            let numero = parseFloat(valorAtual);
            valorInput.value = 'R$ ' + numero.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        valorInput.addEventListener('input', function(e) {
            // Remove tudo que não é número e remove R$
            let value = this.value.replace(/\D/g, '');
            
            if (value === '') {
                this.value = '';
                return;
            }
            
            // Converte para número (divide por 100 para pegar os centavos)
            let numero = parseFloat(value) / 100;
            
            // Formata como moeda brasileira com R$
            this.value = 'R$ ' + numero.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        });
        
        // Quando perder o foco, garante que tem R$ e 2 casas decimais
        valorInput.addEventListener('blur', function() {
            if (this.value === '') return;
            
            // Remove R$ se tiver
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
    
    document.addEventListener('DOMContentLoaded', initMoneyMask);
})();