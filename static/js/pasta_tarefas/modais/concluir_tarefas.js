let botaoAtual = null;

document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('formConcluir');
    const overlay = document.getElementById('modalConcluir');

    if (!form || !overlay) return;

    let enviando = false;

    // 🔥 CLICK BOTÃO
    document.querySelectorAll('.btn-concluir').forEach(btn => {
        btn.addEventListener('click', () => {

            botaoAtual = btn;

            const url = btn.getAttribute('data-url');
            form.action = url;

            overlay.classList.add('active');
        });
    });

    // 🔥 SUBMIT
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (enviando) return;
        enviando = true;

        const btnSubmit = form.querySelector('button[type="submit"]');
        const htmlOriginal = btnSubmit.innerHTML;

        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '⏳';

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Erro ao concluir');
            }

            // 🔥 LINHA DA TABELA
            const linha = botaoAtual?.closest('tr');

            if (linha) {

                const celulaStatus = linha.querySelector('td:nth-child(3)');
                const celulaFinalizacao = linha.querySelector('td:nth-child(6)');

                if (celulaStatus) {
                    celulaStatus.innerHTML =
                        `<span class="badge-pure bg-success">✅ Concluída</span>`;
                }

                if (celulaFinalizacao && data.data_finalizacao) {
                    celulaFinalizacao.innerHTML =
                        `<span class="badge-pure bg-success">${data.data_finalizacao}</span>`;
                }

                // remove todos botões de ação da linha
                linha.querySelectorAll('.btn-concluir, .btn-excluir, .btn-acao.edit').forEach(b => b.remove());
            }

            Notificacao.sucesso(data.message);

            fecharModalConcluir();
            form.reset();

        } catch (error) {
            Notificacao.erro(error.message || 'Erro ao concluir');
        }

        btnSubmit.disabled = false;
        btnSubmit.innerHTML = htmlOriginal;
        enviando = false;
    });

});


// 🔥 FUNÇÃO GLOBAL (evita teu erro "not defined")
window.fecharModalConcluir = function () {
    const overlay = document.getElementById('modalConcluir');
    if (overlay) {
        overlay.classList.remove('active');
    }
};