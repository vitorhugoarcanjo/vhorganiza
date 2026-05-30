// LOGOUT COM NOTIFICAÇÃO (sem flash)
const logoutBtn = document.getElementById('logoutBtn');

if (logoutBtn) {
    const logoutUrl = logoutBtn.dataset.logoutUrl;  // Pega a URL do data attribute
    
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        fetch(logoutUrl, {  // <-- USA A VARIÁVEL AQUI
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                if (window.Notificacao) {
                    Notificacao.aviso(data.mensagem);
                }
                
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            }
        })
        .catch(error => {
            console.error('Erro no logout:', error);
            window.location.href = logoutUrl;  // fallback
        });
    });
}