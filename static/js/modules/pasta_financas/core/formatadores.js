(function() {
    'use strict';
    window.FormatadoresFinancas = {
        mascaraMoeda(input) {
            var value = input.value.replace(/\D/g, '');
            if (!value) return '0,00';
            var floatVal = (parseFloat(value) / 100).toFixed(2);
            var parts = floatVal.split('.');
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            return parts.join(',');
        },
        paraFloat(strValor) {
            return parseFloat((strValor || '0,00').replace(/\./g, '').replace(',', '.')) || 0;
        }
    };
})();