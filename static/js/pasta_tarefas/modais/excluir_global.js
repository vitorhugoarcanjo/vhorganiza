document.addEventListener("DOMContentLoaded", () => {

    let modalCallback = null;
    let bloqueioAcao = false;

    const modal = document.getElementById("modalConfirmacao");

    if (!modal) return; // 🔥 protege crash

    const btnCancelar = document.getElementById("btnCancelar");
    const btnConfirmar = document.getElementById("btnConfirmar");

    function abrirModal({ titulo, texto, onConfirm }) {
        document.getElementById("modalTitulo").innerText = titulo;
        document.getElementById("modalTexto").innerText = texto;

        modal.style.display = "flex";
        modalCallback = onConfirm;

        btnConfirmar.innerText = "Confirmar";
        bloqueioAcao = false;
    }

    function fecharModal() {
        modal.style.display = "none";
        modalCallback = null;
    }

    btnCancelar.addEventListener("click", fecharModal);

    btnConfirmar.addEventListener("click", async () => {
        if (bloqueioAcao) return;

        bloqueioAcao = true;
        btnConfirmar.innerText = "Processando...";

        if (modalCallback) await modalCallback();

        fecharModal();
    });

    modal.addEventListener("click", fecharModal);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") fecharModal();
    });

    window.abrirModal = abrirModal;
});