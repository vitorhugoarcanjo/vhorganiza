function verDetalhes(tarefaId) {
    const modal = document.getElementById('modalDetalhesTarefa');
    const conteudo = document.getElementById('conteudoDetalhes');
    
    conteudo.innerHTML = `
        <div style="text-align: center; padding: 30px; color: var(--texto-mutado);">
            <div class="spinner-pure"></div>
            <p style="margin-top: 10px; font-size: var(--fs-micro);">Carregando dados da tarefa...</p>
        </div>
    `;
    
    modal.classList.add('active');
    
    fetch(`/tarefas/detalhes/${tarefaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                conteudo.innerHTML = `<div class="badge-pure bg-danger" style="width: 100%; padding: 10px;">${data.error}</div>`;
                return;
            }
            
            const statusIcon = data.status === 'concluido' ? '✅' : (data.status === 'em andamento' ? '⏳' : '⏰');
            document.getElementById('modalTitulo').innerHTML = `${statusIcon} ${data.titulo}`;
            
            conteudo.innerHTML = `
                <div class="modal-field full-width" style="margin-bottom: 12px;">
                    <div class="field-label" style="color: var(--cor-marca); font-weight: 600;">📝 Descrição Detalhada</div>
                    <div class="field-value-scroll" style="font-size: var(--fs-pequeno);">${data.descricao || '<span style="opacity: 0.5;">Sem descrição.</span>'}</div>
                </div>
                
                <div class="modal-grid" style="font-size: var(--fs-pequeno);">
                    <div class="modal-field">
                        <div class="field-label">📊 Status</div>
                        <div class="field-value"><span class="badge-pure ${data.status === 'concluido' ? 'bg-success' : (data.status === 'em andamento' ? 'bg-warning text-dark' : 'bg-danger')}">${data.status_label}</span></div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">⚡ Prioridade</div>
                        <div class="field-value"><span class="badge-pure ${data.prioridade === 'alta' ? 'bg-danger' : (data.prioridade === 'media' ? 'bg-warning text-dark' : 'bg-success')}">${data.prioridade_label}</span></div>
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
                        <div class="field-label">📅 Data Início</div>
                        <div class="field-value">${data.data_inicio}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">⏰ Data Prazo</div>
                        <div class="field-value">${data.data_final}</div>
                    </div>

                    <div class="modal-field">
                        <div class="field-label">✅ Data Conclusão</div>
                        <div class="field-value">${data.data_finalizacao !== '-' ? data.data_finalizacao : '<span style="opacity: 0.5;">Não concluída</span>'}</div>
                    </div>
                </div>

                <div class="modal-field full-width">
                    <div class="field-label">💬 Motivo da Conclusão</div>
                    <div class="field-value" style="font-style: italic; color: var(--texto-discreto);">
                        ${data.motivo_conclusao ? data.motivo_conclusao : '<span style="opacity: 0.5;">Sem observações.</span>'}
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro:', error);
            conteudo.innerHTML = `<div class="badge-pure bg-danger" style="width: 100%; padding: 10px;">Erro ao carregar detalhes</div>`;
        });
}

function fecharModalDetalhes(event) {
    if (!event || event.target.classList.contains('modal-overlay')) {
        document.getElementById('modalDetalhesTarefa').classList.remove('active');
    }
}