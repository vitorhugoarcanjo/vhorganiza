// Script Javascript para interceptar o envio e animar o botão -->
document.getElementById('formLogin').addEventListener('submit', function(e) {
    const btn = document.getElementById('btnAcessar');  // ← mudei de btnCadastrar para btnAcessar
    const txtBotao = document.getElementById('txtBotao');
    const spinner = document.getElementById('spinnerCarregando');
    const txtCarregando = document.getElementById('txtCarregando');

    // 1. Desativa o botão na hora para evitar múltiplos cliques acidentais
    btn.disabled = true;

    // 2. Oculta a palavra "Cadastrar" original
    txtBotao.classList.add('d-none');

    // 3. Torna o círculo giratório e o novo texto visíveis
    spinner.classList.remove('d-none');
    txtCarregando.classList.remove('d-none');
});