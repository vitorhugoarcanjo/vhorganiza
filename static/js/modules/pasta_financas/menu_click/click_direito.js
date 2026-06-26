// Clique com botão direito na tabela - Menu Flutuante
(function() {
    'use strict';
    
    let currentRowData = null;
    
    function fecharMenu() {
        const menu = document.getElementById('contextMenu');
        if (menu) menu.style.display = 'none';
        
        document.querySelectorAll('.custom-table tr').forEach(tr => {
            tr.classList.remove('selecionado');
        });
        
        currentRowData = null;
    }
    
    function extrairDadosLinha(linha) {
        const colunas = linha.querySelectorAll('td');
        if (colunas.length < 2) return null;
        
        const sequencia = colunas[0]?.innerText.trim() || '';
        
        let tipoTexto = '';
        let descricao = '';
        
        for (let i = 0; i < colunas.length; i++) {
            const texto = colunas[i]?.innerText.trim() || '';
            
            if (texto.includes('📈') || texto.includes('📉') || texto.includes('Receita') || texto.includes('Despesa')) {
                tipoTexto = texto;
            }
            
            if (i > 0 && !texto.includes('R$') && !texto.includes('✅') && !texto.includes('🔴') && !texto.includes('💰') && texto.length > 5) {
                if (descricao.length < texto.length && (texto.includes('Parcela') || texto.length > 20)) {
                    descricao = texto;
                } else if (!descricao && texto.length > 10) {
                    descricao = texto;
                }
            }
        }
        
        const tipo = tipoTexto.includes('Receita') || tipoTexto.includes('📈') ? 'receita' : 'despesa';
        return { sequencia, descricao, tipo, linha };
    }
    
    function mostrarMenu(x, y, data) {
        const menu = document.getElementById('contextMenu');
        if (!menu) return;
        
        currentRowData = data;
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.display = 'block';
        
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
    
    function initCliqueDireito() {
        console.log('🔥 INICIANDO MENU CLICK DIREITO...');
        
        const tabela = document.querySelector('.custom-table');
        if (!tabela) {
            console.warn('⚠️ Tabela não encontrada!');
            return;
        }
        console.log('✅ Tabela encontrada!');
        
        // Fecha menu ao scroll
        window.addEventListener('scroll', fecharMenu);
        
        // Fecha menu ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#contextMenu')) fecharMenu();
            if (!e.target.closest('.custom-table tr')) {
                document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
            }
        });
        
        // Eventos do menu
        const menu = document.getElementById('contextMenu');
        if (menu) {
            menu.querySelectorAll('.context-menu-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = item.dataset.action;
                    if (currentRowData) {
                        const dados = {
                            sequencia: currentRowData.sequencia,
                            descricao: currentRowData.descricao
                        };
                        
                        if (action === 'ver_vinculos') {
                            fecharMenu();
                            const event = new CustomEvent('abrirModalVinculos', { detail: dados });
                            document.dispatchEvent(event);
                        }
                    }
                    fecharMenu();
                });
            });
        }
        
        // ✅ REMOVE LISTENER ANTIGO PARA EVITAR DUPLICAÇÃO
        document.removeEventListener('contextmenu', handleContextMenu);
        document.addEventListener('contextmenu', handleContextMenu);
        
        console.log('✅ Menu click direito inicializado!');
    }
    
    // ✅ FUNÇÃO SEPARADA PARA O EVENTO
    function handleContextMenu(e) {
        const linha = e.target.closest('tr');
        if (!linha || linha.querySelector('td[colspan]')) return;
        
        const tabela = e.target.closest('.custom-table');
        if (!tabela) return;
        
        e.preventDefault();
        
        document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
        linha.classList.add('selecionado');
        
        const data = extrairDadosLinha(linha);
        if (data) mostrarMenu(e.clientX, e.clientY, data);
    }
    
    // ==========================================================
    // 🔥 INICIALIZAÇÃO
    // ==========================================================
    
    // Tenta iniciar imediatamente (se a tabela já existir)
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(initCliqueDireito, 100);
    }
    
    // Quando o DOM carregar
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initCliqueDireito, 100);
    });
    
    // 🔥 REINICIA DEPOIS QUE O HTMX ATUALIZAR A TABELA
    document.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'tabela-container') {
            console.log('🔄 Tabela atualizada pelo HTMX, reiniciando menu...');
            setTimeout(initCliqueDireito, 200);
        }
    });
    
    // 🔥 TAMBÉM REINICIA DEPOIS DE QUALQUER REQUISIÇÃO HTMX
    document.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.target && evt.detail.target.id === 'tabela-container') {
            console.log('🔄 Requisição HTMX na tabela, reiniciando menu...');
            setTimeout(initCliqueDireito, 200);
        }
    });
    
})();