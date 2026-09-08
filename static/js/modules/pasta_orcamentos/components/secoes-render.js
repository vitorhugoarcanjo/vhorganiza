// ==========================================================
// SEÇÕES - RENDERIZAÇÃO (GLOBAL)
// ==========================================================
// 
// 📌 FUNÇÃO: Renderiza a lista de seções com DRAG & DROP
// 
// 🔧 COMO USAR:
//   - Chamar SecoesRender.renderizar(container, estrutura, callbacks)
//   - Chamar SecoesRender.atualizarContador(container, estrutura)
// 
// 📝 PARÂMETROS:
//   - container:    Elemento DOM onde as seções serão renderizadas
//   - estrutura:    Array de objetos (as seções)
//   - callbacks:    { onEdit, onRemove, onTituloChange }
// 
// 🎯 O QUE FAZ:
//   - Se não houver seções → mostra mensagem "Nenhuma seção adicionada"
//   - Se houver seções → renderiza cada uma com drag handle, badge e título
//   - Adiciona eventos para editar, remover e alterar título
//   - Inicializa Sortable (Drag & Drop) com alça de arraste
// 
// 📍 ONDE É USADO:
//   - secoes-manager.js (através de gerenciador.renderizar())
//   - modal_novo_orcamento.js (através do gerenciador)
//   - modal_editar_orcamento.js (através do gerenciador)
// 
// 🏷️ CLASSES CSS UTILIZADAS:
//   - .orc-secoes-vazio      → Mensagem de vazio
//   - .orc-secao-item        → Cada item da lista
//   - .orc-secao-drag-handle → Alça de arraste
//   - .orc-secao-tipo-badge  → Badge do tipo
//   - .orc-secao-item-titulo → Título editável
//   - .orc-btn-editar        → Botão de editar
//   - .orc-btn-remover       → Botão de remover
// 
// ⚠️ ATENÇÃO: O SortableJS deve ser carregado antes deste arquivo
// ==========================================================
(function() {
    'use strict';

    function renderizarSecoes(container, estrutura, callbacks) {
        if (!container) return;
        
        callbacks = callbacks || {};
        var onEdit = callbacks.onEdit || null;
        var onRemove = callbacks.onRemove || null;
        var onTituloChange = callbacks.onTituloChange || null;
        
        if (!estrutura || estrutura.length === 0) {
            container.innerHTML = `
                <div class="orc-secoes-vazio">
                    <i class="bi bi-inbox"></i>
                    <p>Nenhuma seção adicionada</p>
                    <small>Clique em "Adicionar Seção" para começar</small>
                </div>
            `;
            return;
        }
        
        var tipos = window.SecoesTypes ? window.SecoesTypes.TIPOS_SECAO : {};
        var html = '';
        
        estrutura.forEach(function(secao, index) {
            var tipo = secao.tipo || 'secao';
            var tipoInfo = tipos[tipo] || { icone: '📄', nome: tipo, cor: '#6b7280' };
            var icone = tipoInfo.icone || '📄';
            var nome = tipoInfo.nome || tipo;
            var cor = tipoInfo.cor || '#6b7280';
            var titulo = secao.titulo || '';
            var conteudo = secao.conteudo || '';
            
            html += `
                <div class="orc-secao-item" data-index="${index}">
                    <div class="orc-secao-item-header">
                        <div class="orc-secao-item-header-left">
                            <span class="orc-secao-drag-handle"><i class="bi bi-grip-vertical"></i></span>
                            <span class="orc-secao-tipo-badge" style="background: ${cor}20; color: ${cor};">${icone} ${nome}</span>
                            <input type="text" class="orc-secao-item-titulo" value="${titulo.replace(/"/g, '&quot;')}" data-index="${index}" placeholder="Título da seção">
                        </div>
                        <div class="orc-secao-item-actions">
                            <button type="button" class="orc-btn-editar" data-index="${index}" title="Editar"><i class="bi bi-pencil"></i></button>
                            <button type="button" class="orc-btn-remover" data-index="${index}" title="Remover"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>
                    <div class="orc-secao-item-conteudo">${conteudo || '<span class="orc-empty">(vazio)</span>'}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        container.querySelectorAll('.orc-secao-item-titulo').forEach(function(input) {
            input.addEventListener('change', function() {
                var index = parseInt(this.dataset.index);
                if (onTituloChange) onTituloChange(index, this.value);
            });
        });
        
        container.querySelectorAll('.orc-btn-editar').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var index = parseInt(this.dataset.index);
                if (onEdit) onEdit(index);
            });
        });
        
        container.querySelectorAll('.orc-btn-remover').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var index = parseInt(this.dataset.index);
                if (onRemove) onRemove(index);
            });
        });
        
        if (typeof Sortable !== 'undefined') {
            new Sortable(container, {
                handle: '.orc-secao-drag-handle',
                animation: 150,
                ghostClass: 'dragging',
                onEnd: function(evt) {
                    var item = estrutura.splice(evt.oldIndex, 1)[0];
                    estrutura.splice(evt.newIndex, 0, item);
                    renderizarSecoes(container, estrutura, callbacks);
                }
            });
        }
    }

    // 🔥 FUNÇÃO GLOBAL PARA ATUALIZAR CONTADOR
    function atualizarContador(container, estrutura) {
        // Procura pelo ID específico
        var el = document.getElementById('novoSecoesCount') || document.getElementById('secoesCount');
        
        if (!el && container) {
            el = container.closest('.orc-modal-novo-secoes')?.querySelector('.orc-secoes-count') ||
                 container.closest('.orc-modal-editor-secoes')?.querySelector('.orc-secoes-count');
        }
        
        if (el) {
            var total = estrutura ? estrutura.length : 0;
            el.textContent = total + ' seção' + (total !== 1 ? 'ões' : '');
        }
    }

    window.SecoesRender = {
        renderizar: renderizarSecoes,
        atualizarContador: atualizarContador
    };

    console.log('✅ SECOES-RENDER carregado!');

})();