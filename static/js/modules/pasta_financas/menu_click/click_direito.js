// static/js/modules/pasta_financas/menu_click/click_direito.js
// ==========================================================
// CLIQUE DIREITO - MENU FLUTUANTE (2099)
// Listeners ÚNICOS no document — funciona sempre com HTMX
// ==========================================================

(function() {
    'use strict';

    let currentRowData = null;

    // ==========================================================
    // FECHAR MENU
    // ==========================================================
    function fecharMenu() {
        const menu = document.getElementById('contextMenu');
        if (menu) menu.style.display = 'none';

        document.querySelectorAll('.custom-table tr').forEach(tr => {
            tr.classList.remove('selecionado');
        });

        currentRowData = null;
    }

    // ==========================================================
    // EXTRAIR DADOS DA LINHA CLICADA
    // ==========================================================
    function extrairDadosLinha(linha) {
        const colunas = linha.querySelectorAll('td');
        if (colunas.length < 2) return null;

        const sequencia = colunas[0]?.innerText.trim() || '';

        let tipoTexto = '';
        let descricao = '';

        for (let i = 0; i < colunas.length; i++) {
            const texto = colunas[i]?.innerText.trim() || '';

            if (texto.includes('📈') || texto.includes('📉') ||
                texto.includes('Receita') || texto.includes('Despesa')) {
                tipoTexto = texto;
            }

            if (i > 0 && !texto.includes('R$') && !texto.includes('✅') &&
                !texto.includes('🔴') && !texto.includes('💰') && texto.length > 5) {
                if (descricao.length < texto.length &&
                    (texto.includes('Parcela') || texto.length > 20)) {
                    descricao = texto;
                } else if (!descricao && texto.length > 10) {
                    descricao = texto;
                }
            }
        }

        const tipo = tipoTexto.includes('Receita') || tipoTexto.includes('📈') ? 'receita' : 'despesa';
        return { sequencia, descricao, tipo, linha };
    }

    // ==========================================================
    // MOSTRAR MENU NA POSIÇÃO DO CLIQUE
    // ==========================================================
    function mostrarMenu(x, y, data) {
        const menu = document.getElementById('contextMenu');
        if (!menu) return;

        currentRowData = data;
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.display = 'block';

        // Ajusta se passar da tela
        setTimeout(() => {
            const rect = menu.getBoundingClientRect();
            if (rect.right > window.innerWidth) {
                menu.style.left = (window.innerWidth - rect.width - 10) + 'px';
            }
            if (rect.bottom > window.innerHeight) {
                menu.style.top = (window.innerHeight - rect.height - 10) + 'px';
            }
        }, 10);
    }

    // ==========================================================
    // CLIQUE DIREITO (event delegation — registra 1x)
    // ==========================================================
    document.addEventListener('contextmenu', function(e) {
        const linha = e.target.closest('.custom-table tbody tr');
        if (!linha) return;
        if (linha.querySelector('td[colspan]')) return;   // ignora "nenhum registro"

        e.preventDefault();

        document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
        linha.classList.add('selecionado');

        const data = extrairDadosLinha(linha);
        if (data) mostrarMenu(e.clientX, e.clientY, data);
    });

    // ==========================================================
    // FECHAR MENU (click fora + scroll + ESC)
    // ==========================================================
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#contextMenu')) fecharMenu();
        if (!e.target.closest('.custom-table tr')) {
            document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
        }
    });

    window.addEventListener('scroll', fecharMenu, { passive: true });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') fecharMenu();
    });

    // ==========================================================
    // AÇÃO DO MENU ("Ver vínculos")
    // ==========================================================
    document.addEventListener('click', function(e) {
        const item = e.target.closest('#contextMenu .context-menu-item');
        if (!item) return;

        e.stopPropagation();
        const action = item.dataset.action;

        if (action === 'ver_vinculos' && currentRowData) {
            const dados = {
                sequencia: currentRowData.sequencia,
                descricao: currentRowData.descricao
            };
            fecharMenu();
            document.dispatchEvent(new CustomEvent('abrirModalVinculos', { detail: dados }));
        }
    });

    console.log('✅ Menu click direito (2099) carregado!');

})();