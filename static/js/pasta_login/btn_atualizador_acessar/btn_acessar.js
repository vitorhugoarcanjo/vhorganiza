// static/js/pasta_login/btn_atualizador_acessar/btn_acessar.js

// Remove qualquer listener anterior antes de adicionar
const form = document.getElementById('formLogin');

// Remove listeners anteriores (se houver)
const newForm = form.cloneNode(true);
form.parentNode.replaceChild(newForm, form);

// Adiciona o listener no form novo
newForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('btnAcessar');
    const txtBotao = document.getElementById('txtBotao');
    const spinner = document.getElementById('spinnerCarregando');
    const txtCarregando = document.getElementById('txtCarregando');
    
    // Desativa botão
    btn.disabled = true;
    txtBotao.classList.add('d-none');
    spinner.classList.remove('d-none');
    txtCarregando.classList.remove('d-none');
    
    const formData = new FormData(newForm);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Só mostra uma notificação
            if (window.Notificacao) {
                window.Notificacao.sucesso(data.message);
            }
            
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 1000);
            
        } else {
            btn.disabled = false;
            txtBotao.classList.remove('d-none');
            spinner.classList.add('d-none');
            txtCarregando.classList.add('d-none');
            
            if (window.Notificacao) {
                if (data.type === 'erro') {
                    window.Notificacao.erro(data.message);
                } else {
                    window.Notificacao.aviso(data.message);
                }
            }
        }
        
    } catch (error) {
        btn.disabled = false;
        txtBotao.classList.remove('d-none');
        spinner.classList.add('d-none');
        txtCarregando.classList.add('d-none');
        
        if (window.Notificacao) {
            window.Notificacao.erro('Erro ao conectar com o servidor');
        }
    }
});