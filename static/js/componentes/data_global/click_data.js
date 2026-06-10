// ==========================================================================
// CLICK DATA - EFEITO RIPPLE PARA BOTÕES DE FILTRO DE DATA
// ==========================================================================
// Compatível com: Finanças, Tarefas, Dashboard (todas as telas com filtro data)
// ==========================================================================

(function() {
    'use strict';
    
    function criarRipple(evento) {
        const botao = evento.currentTarget;
        
        // Remove ripple antigo se existir
        const rippleAntigo = botao.querySelector('.ripple');
        if (rippleAntigo) {
            rippleAntigo.remove();
        }
        
        // Cria o elemento da onda
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        
        // Calcula a posição do clique
        const rect = botao.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = evento.clientX - rect.left - size / 2;
        const y = evento.clientY - rect.top - size / 2;
        
        // Aplica estilo dinâmico
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        // Adiciona ao botão
        botao.appendChild(ripple);
        
        // Remove após animação
        ripple.addEventListener('animationend', () => {
            ripple.remove();
        });
    }
    
    function initRippleData() {
        // Seleciona botões de data em todas as telas
        const botoesData = document.querySelectorAll(
            '.btn-pure, ' +           // Botões de filtro data
            '.btn-success-pure, ' +   // Botão HOJE
            '.btn-info-pure'          // Botão I/F - MÊS
        );
        
        botoesData.forEach(botao => {
            // Garante que o botão tem position relative
            if (getComputedStyle(botao).position !== 'relative') {
                botao.style.position = 'relative';
            }
            botao.style.overflow = 'hidden';
            
            // Remove listener antigo para evitar duplicação
            botao.removeEventListener('click', criarRipple);
            botao.addEventListener('click', criarRipple);
        });
    }
    
    // Inicializa quando a página carrega
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRippleData);
    } else {
        initRippleData();
    }
    
    // 🔥 IMPORTANTE: Reaplica após HTMX atualizar a tabela
    document.body.addEventListener('htmx:afterSwap', function(evento) {
        initRippleData();
    });
    
    document.body.addEventListener('htmx:afterSettle', function(evento) {
        initRippleData();
    });
    
    // Para telas que usam navegação tradicional (sem HTMX)
    document.body.addEventListener('turbo:load', initRippleData);
})();