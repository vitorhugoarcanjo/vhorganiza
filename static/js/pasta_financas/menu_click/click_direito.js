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
        
        const parcelaMatch = descricao.match(/(\d+)\/(\d+)/);
        const numeroParcela = parcelaMatch ? parcelaMatch[1] : null;
        const totalParcelas = parcelaMatch ? parcelaMatch[2] : null;
        const tipo = tipoTexto.includes('Receita') || tipoTexto.includes('📈') ? 'receita' : 'despesa';
        
        return { sequencia, descricao, numeroParcela, totalParcelas, tipo, linha };
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
        const tabela = document.querySelector('.custom-table');
        if (!tabela) return;
        
        window.addEventListener('scroll', () => fecharMenu());
        
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#contextMenu')) fecharMenu();
            if (!e.target.closest('.custom-table tr')) {
                document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
            }
        });
        
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
        
        tabela.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const linha = e.target.closest('tr');
            if (!linha || linha.querySelector('td[colspan]')) return;
            
            document.querySelectorAll('.custom-table tr').forEach(tr => tr.classList.remove('selecionado'));
            linha.classList.add('selecionado');
            
            const data = extrairDadosLinha(linha);
            if (data) mostrarMenu(e.clientX, e.clientY, data);
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCliqueDireito);
    } else {
        initCliqueDireito();
    }
})();