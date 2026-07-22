// 🔥 COLOCA ISSO AQUI EM CIMA DE TUDO
if (window.__BTN_INSERT_RODANDO) {
    console.warn("btn_insert já rodou");
} else {
    window.__BTN_INSERT_RODANDO = true;


// static/js/pasta_tarefas/pasta_insert/btn_insert.js

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('form-tarefa');
        const btnSubmit = document.getElementById('btn-submit');
        
        if (!form) return;
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            console.log("SUBMIT DISPARADO")
            
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = '⏳ Salvando...';
            }
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/insert_tarefas/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    console.log("NOTIFICACAO SUCESSO CHAMADA");
                    Notificacao.sucesso(data.message);
                    
                    setTimeout(() => {
                        window.location.href = '/tarefas/';
                    }, 1000);
                } else {
                    Notificacao.erro(data.error || 'Erro ao cadastrar tarefa');

                    if (btnSubmit) {
                        btnSubmit.disabled = false;
                        btnSubmit.innerHTML = '✅ Salvar Tarefa';
                    }
                }

            } catch (error) {
                Notificacao.erro('Erro de conexão. Tente novamente.');

                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '✅ Salvar Tarefa';
                }
            }
        });
    });
})();

} // 🔥 FECHA AQUI