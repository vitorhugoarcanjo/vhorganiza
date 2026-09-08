// ==========================================================
// SEÇÕES - FORM COMPARTILHADO (NOVO + EDITAR)
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // FUNÇÕES GLOBAIS DO FORM (CHAMADAS PELO HTML COMPARTILHADO)
    // ==========================================================
    
    // Abrir modal de seção (qualquer contexto)
    window.abrirModalNovaSecao = function(secao = null, index = null) {
        // Detecta qual gerenciador está ativo
        var gerenciador = window._gerenciadorNovo || window._gerenciadorEditar;
        if (!gerenciador) {
            window.Notificacao.erro('Sistema não inicializado');
            return;
        }
        gerenciador.abrirModalSecao(secao, index);
    };

    // Fechar modal de seção
    window.fecharModalNovaSecao = function() {
        var gerenciador = window._gerenciadorNovo || window._gerenciadorEditar;
        if (gerenciador) gerenciador.fecharModalSecao();
    };

    // Selecionar tipo de seção
    window.selecionarTipo = function(btn) {
        var gerenciador = window._gerenciadorNovo || window._gerenciadorEditar;
        if (gerenciador) gerenciador.selecionarTipo(btn);
    };

    // Atualizar preview da seção
    window.atualizarPreviewSecao = function() {
        var gerenciador = window._gerenciadorNovo || window._gerenciadorEditar;
        if (gerenciador) gerenciador.atualizarPreview();
    };

    // Formatar valor
    window.formatarValor = function(input) {
        var valor = input.value.replace(/\D/g, '');
        if (valor === '') {
            input.value = '0,00';
            return;
        }
        var numero = parseInt(valor) / 100;
        var formatado = numero.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        input.value = formatado;
    };

    // ==========================================================
    // CONFIGURAR FORM (CHAMADO PELO GERENCIADOR)
    // ==========================================================
    function configurarFormSubmit(gerenciador) {
        var form = document.getElementById('formNovaSecao');
        if (!form) return;
        
        // Remove listeners antigos
        var novoForm = form.cloneNode(true);
        form.parentNode.replaceChild(novoForm, form);
        
        novoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var tipoBtn = document.querySelector('#modalNovaSecao .orc-tipo-btn.active');
            var tipo = tipoBtn ? tipoBtn.dataset.tipo : 'secao';
            var titulo = document.getElementById('novaSecaoTitulo').value;
            var conteudo = document.getElementById('novaSecaoConteudo').value;
            
            var dados = { tipo, titulo, conteudo };
            
            // Coletar campos específicos
            if (tipo === 'tabela') {
                dados.colunas = document.getElementById('campoTabelaColunas')?.value.split(',').map(function(c) { return c.trim(); }) || [];
                dados.linhas = document.getElementById('campoTabelaLinhas')?.value.split('\n').filter(function(l) { return l.trim(); }).map(function(l) { return l.split('|').map(function(c) { return c.trim(); }); }) || [];
            } else if (tipo === 'lista' || tipo === 'numerada') {
                dados.itens = document.getElementById('campoListaItens')?.value.split('\n').filter(function(i) { return i.trim(); }) || [];
            } else if (tipo === 'valor') {
                dados.valor = document.getElementById('secaoValor')?.value || '0,00';
                dados.descricao_valor = document.getElementById('secaoValorDescricao')?.value || '';
                // O conteúdo já vem do textarea principal
            } else if (tipo === 'destaque') {
                dados.cor = document.getElementById('secaoDestaqueCor')?.value || 'azul';
            }
            
            // Salva a seção
            if (gerenciador.secaoEditando !== null && gerenciador.indexEditando !== null) {
                gerenciador.atualizarSecao(gerenciador.indexEditando, dados);
            } else {
                gerenciador.adicionarSecao(dados);
            }
            
            gerenciador.fecharModalSecao();
        });
    }

    // ==========================================================
    // EXPORTA
    // ==========================================================
    window.SecoesForm = {
        configurarFormSubmit: configurarFormSubmit
    };

    console.log('✅ SECOES-FORM carregado!');

})();