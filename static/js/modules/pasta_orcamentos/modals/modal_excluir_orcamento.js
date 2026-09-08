// ==========================================================
// ORÇAMENTOS - MODAL EXCLUIR
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // ABRIR / FECHAR
    // ==========================================================
    function abrirModalExcluir(id, titulo) {
        const modal = document.getElementById('modalExcluirOrcamento');
        if (modal) {
            document.getElementById('nomeOrcamentoExcluir').textContent = titulo;
            document.getElementById('btnConfirmarExcluir').dataset.id = id;
            modal.classList.add('active');
        }
    }

    function fecharModalExcluir() {
        const modal = document.getElementById('modalExcluirOrcamento');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // EXPORTA
    window.abrirModalExcluir = abrirModalExcluir;
    window.fecharModalExcluir = fecharModalExcluir;

    // ==========================================================
    // CONFIRMAR EXCLUSÃO
    // ==========================================================
    document.getElementById('btnConfirmarExcluir')?.addEventListener('click', async function() {
        const id = this.dataset.id;
        if (!id) return;
        
        this.disabled = true;
        this.innerHTML = '<i class="bi bi-spinner bi-spin"></i> Excluindo...';
        
        try {
            const response = await fetch(`/orcamentos/${id}/excluir`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.Notificacao.sucesso(data.message);
                fecharModalExcluir();
                setTimeout(() => {
                    window.location.reload();
                }, 300);
            } else {
                window.Notificacao.erro(data.message);
            }
        } catch (error) {
            window.Notificacao.erro('Erro ao excluir');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="bi bi-trash"></i> Excluir';
        }
    });

})();