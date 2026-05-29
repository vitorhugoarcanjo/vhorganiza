function quitarTransacao(sequencia, botao) {
    const htmlOriginal = botao.innerHTML;

    botao.disabled = true;
    botao.style.opacity = '0.5';
    botao.innerHTML = '⏳';

    fetch('/quitar_transacao/' + sequencia, {
        method: 'POST',  // 👈 ADICIONA ISSO
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const linha = botao.closest('tr');
            
            // Atualiza o status na tabela (coluna 5 = índice 5)
            const celulaStatus = linha.querySelector('td:nth-child(5)');
            
            // Detecta se é receita ou despesa pelo tipo
            const tipoCelula = linha.querySelector('td:nth-child(2)');
            const ehReceita = tipoCelula.innerText.includes('Receita');
            
            if (ehReceita) {
                celulaStatus.innerHTML = '<span class="badge-pure bg-success">💰 Recebido</span>';
                Notificacao.sucesso('Receita recebida com sucesso!');
            } else {
                celulaStatus.innerHTML = '<span class="badge-pure bg-success">✅ Quitado</span>';
                Notificacao.sucesso('Despesa quitada com sucesso!');
            }
            
            // Remove o botão de quitar da linha
            botao.remove();
            
            // Opcional: esconde também os botões Editar/Excluir
            const botoesAcao = linha.querySelectorAll('.edit, .delete');
            botoesAcao.forEach(btn => btn.remove());
            
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