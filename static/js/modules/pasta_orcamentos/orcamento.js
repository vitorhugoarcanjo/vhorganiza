// ==========================================================
// ORÇAMENTOS - MAIN (GLOBAL)
// ==========================================================
// 
// 📌 FUNÇÃO: Fecha modais com ESC e clique fora
// 
// 🔧 O QUE FAZ:
//   - Escuta tecla ESC para fechar todos os modais
//   - Escuta clique fora dos modais para fechar
// 
// 🎯 MODAIS GERENCIADOS:
//   - modalNovoOrcamento (NOVO)
//   - modalEditarOrcamento (EDITAR)
//   - modalExcluirOrcamento (EXCLUIR)
//   - modalPreview (PREVIEW)
// 
// ⚠️ ATENÇÃO: As funções window.fechar* devem existir nos modais
// ==========================================================
(function() {
    'use strict';

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (window.fecharModalNovoOrcamento) window.fecharModalNovoOrcamento();
            if (window.fecharModalExcluir) window.fecharModalExcluir();
            if (window.fecharModalEditar) window.fecharModalEditar();
            if (window.fecharPreview) window.fecharPreview();
        }
    });

    document.addEventListener('click', function(e) {
        // Novo
        var modalNovo = document.getElementById('modalNovoOrcamento');
        if (modalNovo && modalNovo.classList.contains('active') && e.target === modalNovo) {
            if (window.fecharModalNovoOrcamento) window.fecharModalNovoOrcamento();
        }
        // Excluir
        var modalExcluir = document.getElementById('modalExcluirOrcamento');
        if (modalExcluir && modalExcluir.classList.contains('active') && e.target === modalExcluir) {
            if (window.fecharModalExcluir) window.fecharModalExcluir();
        }
        // Editar
        var modalEditar = document.getElementById('modalEditarOrcamento');
        if (modalEditar && modalEditar.classList.contains('active') && e.target === modalEditar) {
            if (window.fecharModalEditar) window.fecharModalEditar();
        }
        // Preview
        var modalPreview = document.getElementById('modalPreview');
        if (modalPreview && modalPreview.classList.contains('active') && e.target === modalPreview) {
            if (window.fecharPreview) window.fecharPreview();
        }
    });

    console.log('✅ ORÇAMENTOS - MAIN carregado!');

})();