function quitarTransacao(sequencia, botao) {
    
    const htmlOriginal = botao.innerHTML;
    botao.disabled = true;
    botao.style.opacity = '0.5';
    botao.innerHTML = '⏳';

    fetch('/quitar_transacao/' + sequencia, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        
        if (data.success) {
            
            
            const linha = botao.closest('tr');
            
            // Atualiza o status na tabela (coluna 5)
            const celulaStatus = linha.querySelector('td:nth-child(5)');
            const tipoCelula = linha.querySelector('td:nth-child(2)');
            const ehReceita = tipoCelula.innerText.includes('Receita');
            
            let novoTipo = '';
            if (ehReceita) {
                celulaStatus.innerHTML = '<span class="badge-pure bg-success">💰 Recebido</span>';
                novoTipo = 'receita';
            } else {
                celulaStatus.innerHTML = '<span class="badge-pure bg-success">✅ Quitado</span>';
                novoTipo = 'despesa';
            }
            
            // Pega a célula de ações (última coluna)
            const celulaAcoes = linha.querySelector('td:last-child');
            
            // Remove botão de quitar
            botao.remove();
            
            // Remove botões de editar e excluir
            const btnEditar = celulaAcoes.querySelector('.edit');
            const btnExcluir = celulaAcoes.querySelector('.delete');
            if (btnEditar) btnEditar.remove();
            if (btnExcluir) btnExcluir.remove();
            
            // 🔥 ADICIONA O BOTÃO DE ESTORNAR
            const btnEstornar = document.createElement('button');
            btnEstornar.type = 'button';
            btnEstornar.className = 'btn-acao undo btn-estornar';
            btnEstornar.setAttribute('data-id', sequencia);
            btnEstornar.setAttribute('data-desc', data.descricao || 'Transação');
            btnEstornar.setAttribute('data-tipo', novoTipo);
            btnEstornar.title = 'Estornar';
            btnEstornar.innerHTML = '<i class="bi bi-arrow-return-left"></i>';
            
            // Adiciona o evento de click no botão estornar
            btnEstornar.addEventListener('click', function(e) {
                e.preventDefault();
                
                const id = this.dataset.id;
                const desc = this.dataset.desc;
                const tipo = this.dataset.tipo;
                const tipoTexto = tipo === 'despesa' ? 'DESPESA' : 'RECEITA';
                
                if (typeof window.abrirModalEstornar === 'undefined') {
                    alert('Erro: Sistema de estorno não carregado. Recarregue a página.');
                    return;
                }
                
                window.abrirModalEstornar({
                    titulo: `⚠️ Estornar ${tipoTexto}`,
                    texto: `Deseja realmente ESTORNAR a transação?\n\n"${desc}"\n\nEla voltará para o status ABERTO.`,
                    data: { id, btn: this, descricao: desc, tipo },
                    
                    onConfirm: async (data) => {
                        const { id, btn } = data;
                        
                        try {
                            btn.disabled = true;
                            btn.style.opacity = '0.5';
                            btn.innerHTML = '⏳';
                            
                            const response = await fetch(`/estornar_transacao/${id}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-Requested-With': 'XMLHttpRequest'
                                }
                            });
                            
                            const result = await response.json();
                            
                            if (result.success) {
                                const linha = btn.closest('tr');
                                if (linha) {
                                    linha.style.transition = 'opacity 0.3s';
                                    linha.style.opacity = '0';
                                    setTimeout(() => linha.remove(), 300);
                                }
                                
                                Notificacao.sucesso(result.message || 'Transação estornada!');
                                // 🔥 Recarrega só os dados, não a página inteira
                                setTimeout(() => location.reload(), 1000);
                            } else {
                                throw new Error(result.error || 'Erro ao estornar');
                            }
                        } catch (error) {
                            btn.disabled = false;
                            btn.style.opacity = '1';
                            btn.innerHTML = '<i class="bi bi-arrow-return-left"></i>';
                            Notificacao.erro(error.message);
                        }
                    }
                });
            });
            
            // Insere o botão estornar na célula de ações
            celulaAcoes.appendChild(btnEstornar);
            
            // Atualiza os totalizadores
            if (typeof calcularTotaisFinancas === 'function') {
                calcularTotaisFinancas();
            }
            
            Notificacao.sucesso('Transação quitada com sucesso!');
            
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