function quitarTransacao(sequencia, botao) {
    const htmlOriginal = botao.innerHTML;

    botao.disabled = true;
    botao.style.opacity = '0.5';
    botao.innerHTML = '⏳';

    fetch('/quitar_transacao/' + sequencia, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const linha = botao.closest('tr');
            const celulaStatus = linha.querySelector('td:nth-child(5)');
            celulaStatus.innerHTML = '<span class="badge-pure bg-success">✅ Quitado</span>';
            botao.remove();
            
            // 🔥 NOTIFICAÇÃO PROFISSIONAL
            Notificacao.sucesso('Despesa quitada com sucesso!');
        } else {
            botao.disabled = false;
            botao.style.opacity = '1';
            botao.innerHTML = htmlOriginal;
            Notificacao.erro(data.error || 'Erro ao quitar transação');
        }
    })
    .catch(error => {
        botao.disabled = false;
        botao.style.opacity = '1';
        botao.innerHTML = htmlOriginal;
        Notificacao.erro('Erro de conexão. Tente novamente.');
    });
}