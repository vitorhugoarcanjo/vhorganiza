// static/js/modules/pasta_pre_login/btn_cadastrar.js
// ==========================================================

(function () {
    const form = document.getElementById('formCadastro');
    if (!form) return;

    form.addEventListener('submit', function () {
        const btn          = document.getElementById('btnCadastrar');
        const txtBotao     = document.getElementById('txtBotao');
        const spinner      = document.getElementById('spinnerCarregando');
        const txtCarregando = document.getElementById('txtCarregando');

        btn.disabled = true;
        txtBotao.classList.add('d-none');
        spinner.classList.remove('d-none');
        txtCarregando.classList.remove('d-none');
    });
})();