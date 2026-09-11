(function() {
    'use strict';
    window.ApiTransacao = {
        async enviar(url, formData) {
            const res = await fetch(url || window.location.href, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            return { ok: res.ok, data };
        }
    };
})();