// static/js/pasta_financas/pasta_insert/btn_insert.js

(function() {
    'use strict';

    if (window.__BTN_INSERT_RODANDO) {
        console.warn("btn_insert já rodou");
        return;
    }
    window.__BTN_INSERT_RODANDO = true;

    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('form-transacao');
        const btnSubmit = document.getElementById('btn-submit');
        const btnCancelar = document.querySelector('.botoes-footer .btn-secondary');
        
        if (!form) {
            console.error("Form não encontrado!");
            return;
        }
        
        console.log("btn_insert.js carregado - form encontrado");
        
        const handleSubmit = async function(e) {
            e.preventDefault();
            e.stopPropagation();

            console.log("SUBMIT DISPARADO - AJAX");
            
            // Desabilita SALVAR
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = '<i class="bi bi-save"></i> Salvando...';
            }
            
            // Desabilita CANCELAR
            if (btnCancelar) {
                btnCancelar.style.pointerEvents = 'none';
                btnCancelar.style.opacity = '0.5';
            }
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/nova_transacao/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                console.log("Resposta:", data);
                
                if (data.success) {
                    console.log("SUCESSO! Redirecionando...");
                    
                    if (typeof Notificacao !== 'undefined') {
                        Notificacao.sucesso(data.message);
                    }
                    
                    setTimeout(() => {
                        window.location.href = '/financas/';
                    }, 1500);
                } else {
                    if (typeof Notificacao !== 'undefined') {
                        Notificacao.erro(data.error || 'Erro ao cadastrar transação');
                    }
                    
                    // Reabilita os botões
                    if (btnSubmit) {
                        btnSubmit.disabled = false;
                        btnSubmit.innerHTML = '<i class="bi bi-save"></i> Salvar';
                    }
                    if (btnCancelar) {
                        btnCancelar.style.pointerEvents = 'auto';
                        btnCancelar.style.opacity = '1';
                    }
                }

            } catch (error) {
                console.error("Erro:", error);
                if (typeof Notificacao !== 'undefined') {
                    Notificacao.erro('Erro de conexão. Tente novamente.');
                }
                
                // Reabilita os botões
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '<i class="bi bi-save"></i> Salvar';
                }
                if (btnCancelar) {
                    btnCancelar.style.pointerEvents = 'auto';
                    btnCancelar.style.opacity = '1';
                }
            }
        };
        
        form.removeEventListener('submit', handleSubmit);
        form.addEventListener('submit', handleSubmit);
        
        console.log("Listener de submit adicionado ao form");
    });
})();