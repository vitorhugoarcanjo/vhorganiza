// Modal global para exclusão (padronizado com active class)
(function() {
    function initModal() {
        const modal = document.getElementById("modalConfirmacao");
        if (!modal) return;
        
        window.abrirModal = function({ titulo, texto, onConfirm }) {
            const modalEl = document.getElementById("modalConfirmacao");
            const btnCancelar = document.getElementById("btnCancelar");
            const btnConfirmar = document.getElementById("btnConfirmar");
            const tituloEl = document.getElementById("modalTitulo");
            const textoEl = document.getElementById("modalTexto");

            if (!modalEl || !btnCancelar || !btnConfirmar) return;

            tituloEl.textContent = titulo;
            textoEl.textContent = texto;

            modalEl.classList.add('active');

            const newConfirmBtn = btnConfirmar.cloneNode(true);
            const newCancelBtn = btnCancelar.cloneNode(true);
            
            btnConfirmar.parentNode.replaceChild(newConfirmBtn, btnConfirmar);
            btnCancelar.parentNode.replaceChild(newCancelBtn, btnCancelar);

            let bloqueio = false;

            newConfirmBtn.onclick = async () => {
                if (bloqueio) return;
                bloqueio = true;
                
                const originalText = newConfirmBtn.innerText;
                newConfirmBtn.innerText = "Processando...";

                try {
                    if (onConfirm) await onConfirm();
                    modalEl.classList.remove('active');
                } catch (error) {
                    alert("Erro: " + error.message);
                } finally {
                    newConfirmBtn.innerText = originalText;
                    bloqueio = false;
                }
            };

            newCancelBtn.onclick = () => {
                modalEl.classList.remove('active');
            };

            modalEl.onclick = (e) => {
                if (e.target === modalEl) modalEl.classList.remove('active');
            };
        };
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModal);
    } else {
        initModal();
    }
})();