(function() {
    'use strict';

    if (window.__editSubmitLoaded) return;
    window.__editSubmitLoaded = true;

    console.log("btn_edit carregado");

    document.addEventListener('DOMContentLoaded', function() {

        const form = document.getElementById('form-edit-transacao');
        const btnSubmit = form?.querySelector('button[type="submit"]');

        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            console.log("EDIT SUBMIT");

            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = '⏳ Salvando...';
            }

            const formData = new FormData(form);

            try {
                const response = await fetch(window.location.pathname, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                let data;
                try {
                    data = await response.json();
                } catch {
                    throw new Error("Resposta inválida");
                }

                if (data.success) {
                    Notificacao.sucesso(data.message);

                    setTimeout(() => {
                        window.location.href = '/financas/';
                    }, 1500);
                } else {
                    Notificacao.erro(data.error || 'Erro ao atualizar');
                }

            } catch (error) {
                Notificacao.erro('Erro de conexão');
            } finally {
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = 'Salvar Alterações';
                }
            }
        });

    });
})();