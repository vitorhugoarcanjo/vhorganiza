// Ver Vínculos - Toda a lógica aqui
(function() {
    'use strict';
    
    function formatarMoeda(valor) {
        return parseFloat(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    
    function mostrarModalVinculos(descricao, vinculos, tipo) {
        const modal = document.getElementById('modalVinculos');
        const modalDescricao = document.getElementById('modalDescricao');
        const modalLista = document.getElementById('modalListaVinculos');
        
        if (!modal) return;
        
        modalDescricao.innerHTML = `<strong>📌 ${descricao}</strong>`;
        
        if (vinculos && vinculos.length > 0) {
            let html = '';
            vinculos.forEach(v => {
                let statusIcon = '';
                let statusClass = '';
                let statusText = '';
                
                if (v.status === 'quitado') {
                    statusIcon = '✅';
                    statusClass = 'status-quitado';
                    statusText = 'Quitado';
                } else if (v.status === 'recebido') {
                    statusIcon = '💰';
                    statusClass = 'status-recebido';
                    statusText = 'Recebido';
                } else {
                    statusIcon = '🔴';
                    statusClass = 'status-aberto';
                    statusText = 'Aberto';
                }
                
                html += `
                    <div class="item-vinculo">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="parcela-num">📅 Parcela ${v.numero_parcela}/${v.total_parcelas}</span>
                            <span class="${statusClass}">${statusIcon} ${statusText}</span>
                        </div>
                        <span class="parcela-valor ${tipo === 'receita' ? 'receita' : 'despesa'}">
                            ${tipo === 'receita' ? '+' : '-'} R$ ${formatarMoeda(v.valor)}
                        </span>
                        <span class="parcela-data">📆 Vencimento: ${v.data_vencimento || '—'}</span>
                    </div>
                `;
            });
            modalLista.innerHTML = html;
        } else {
            modalLista.innerHTML = '<div class="sem-vinculo">ℹ️ Nenhum vínculo encontrado para esta transação.</div>';
        }
        
        modal.style.display = 'flex';
    }
    
    function fecharModal() {
        const modal = document.getElementById('modalVinculos');
        if (modal) modal.style.display = 'none';
    }
    
    function verVinculos(sequencia, descricao) {
        console.log("🔍 Buscando vínculos para sequência:", sequencia);
        
        fetch(`/api/financas/vinculos/${sequencia}`)
            .then(response => response.json())
            .then(data => {
                console.log("📦 Resposta do backend:", data);
                if (data.success) {
                    mostrarModalVinculos(data.descricao || descricao, data.vinculos || [], data.tipo);
                } else {
                    mostrarModalVinculos(descricao, [], 'despesa');
                }
            })
            .catch((error) => {
                console.error("❌ Erro:", error);
                mostrarModalVinculos(descricao, [], 'despesa');
            });
    }
    
    function init() {
        document.addEventListener('abrirModalVinculos', (e) => {
            const dados = e.detail;
            verVinculos(dados.sequencia, dados.descricao);
        });
        
        const modal = document.getElementById('modalVinculos');
        if (modal) {
            modal.querySelectorAll('.modal-vinculos-close, .btn-modal-fechar').forEach(btn => {
                btn.addEventListener('click', fecharModal);
            });
            window.addEventListener('click', (e) => {
                if (e.target === modal) fecharModal();
            });
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();