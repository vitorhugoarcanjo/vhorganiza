// static/js/pasta_financas/pasta_edit/btn_edit.js

(function() {
    'use strict';

    if (window.__BTN_EDIT_RODANDO) return;
    window.__BTN_EDIT_RODANDO = true;

    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('form-edit-transacao');
        
        if (!form) return;
        
        form.addEventListener('submit', async function(e) {
            // Se o evento já foi cancelado pela validação, não faz nada
            if (e.defaultPrevented) return;
            
            e.preventDefault(); // 🔥 IMPEDE O ENVIO NORMAL DO FORMULÁRIO
            
            const submitBtn = document.getElementById('btn-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '⏳ Salvando...';
            }
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'  // 🔥 ADICIONA ESSE HEADER
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (typeof Notificacao !== 'undefined') {
                        Notificacao.sucesso(data.message);
                    }
                    
                    // 🔥 REDIRECIONA PARA A LISTAGEM
                    setTimeout(() => {
                        window.location.href = '/financas/';
                    }, 1500);
                } else {
                    if (typeof Notificacao !== 'undefined') {
                        Notificacao.erro(data.error || 'Erro ao atualizar');
                    }
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = 'Salvar Alterações';
                    }
                }
                
            } catch (error) {
                console.error('Erro:', error);
                if (typeof Notificacao !== 'undefined') {
                    Notificacao.erro('Erro de conexão. Tente novamente.');
                }
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Salvar Alterações';
                }
            }
        });
    });
})();