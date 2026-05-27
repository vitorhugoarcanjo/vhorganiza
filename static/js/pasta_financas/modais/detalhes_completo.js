function verDetalhesTransacao(transacaoId) {
    const modal = document.getElementById('modalDetalhesTransacao');
    const conteudo = document.getElementById('conteudoDetalhesTransacao');
    
    conteudo.innerHTML = `
        <div style="text-align: center; padding: 30px; color: var(--texto-mutado);">
            <div class="spinner-pure"></div>
            <p style="margin-top: 10px; font-size: var(--fs-micro);">Carregando dados da transação...</p>
        </div>
    `;
    
    modal.classList.add('active');
    
    fetch(`/financas/detalhes/${transacaoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                conteudo.innerHTML = `<div class="badge-pure bg-danger" style="width: 100%; padding: 10px;">${data.error}</div>`;
                return;
            }
            
            const tipoIcon = data.tipo === 'receita' ? '📈' : '📉';
            document.getElementById('modalTituloTransacao').innerHTML = `${tipoIcon} ${data.descricao.substring(0, 50)}`;
            
            conteudo.innerHTML = `
                <div class="modal-field full-width" style="margin-bottom: 12px;">
                    <div class="field-label" style="color: var(--cor-marca); font-weight: 600;">💰 Descrição</div>
                    <div class="field-value-scroll" style="font-size: var(--fs-pequeno);">${data.descricao}</div>
                </div>
                
                <div class="modal-grid" style="font-size: var(--fs-pequeno);">
                    <div class="modal-field">
                        <div class="field-label">📊 Tipo</div>
                        <div class="field-value"><span class="badge-pure ${data.tipo === 'receita' ? 'bg-success' : 'bg-warning text-dark'}">${data.tipo_label}</span></div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">💰 Valor</div>
                        <div class="field-value" style="font-weight: bold; font-size: 1.1rem;">${data.valor}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">📊 Status</div>
                        <div class="field-value"><span class="badge-pure ${data.status === 'aberto' ? 'bg-danger' : 'bg-success'}">${data.status_label}</span></div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">🏷️ Categoria</div>
                        <div class="field-value">
                            <span class="badge-pure" style="background-color: ${data.categoria_cor || 'var(--border-sutil)'}; color: white;">
                                ${data.categoria}
                            </span>
                        </div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">📅 Data Emissão</div>
                        <div class="field-value">${data.data_emissao}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">⏰ Data Vencimento</div>
                        <div class="field-value">${data.data_vencimento}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">✅ Data Quitação</div>
                        <div class="field-value">${data.data_quitamento}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">📦 Parcela</div>
                        <div class="field-value">${data.parcela_label}</div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro:', error);
            conteudo.innerHTML = `<div class="badge-pure bg-danger" style="width: 100%; padding: 10px;">Erro ao carregar detalhes</div>`;
        });
}

function fecharModalDetalhesTransacao(event) {
    if (!event || event.target.classList.contains('modal-overlay')) {
        document.getElementById('modalDetalhesTransacao').classList.remove('active');
    }
}

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('modalDetalhesTransacao');
        if (modal && modal.classList.contains('active')) {
            fecharModalDetalhesTransacao(null);
        }
    }
});