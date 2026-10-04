// static/js/modules/pasta_tarefas/acoes_e_modais/pasta_detalhes/detalhes_tarefa.js
// ==========================================================
// DETALHES DA TAREFA — fetch JSON → modal
// ==========================================================

(function() {
    'use strict';

    // ==========================================================
    // Ver detalhes
    // ==========================================================
    window.verDetalhesTarefa = function(seq) {
        fetch('/tarefas/detalhes/' + seq, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            const modal = document.getElementById('modalDetalhesTarefa');
            const conteudo = document.getElementById('conteudoDetalhes');
            if (!modal || !conteudo) return;

            // 🔥 Layout igual Finanças: grid + fields com labels
            conteudo.innerHTML =
                '<div class="modal-detalhes-grid">' +

                    '<div class="modal-detalhes-field full-width">' +
                        '<div class="field-detalhes-label">📝 Título</div>' +
                        '<div class="field-detalhes-value">' + (data.titulo || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field full-width">' +
                        '<div class="field-detalhes-label">📄 Descrição</div>' +
                        '<div class="field-detalhes-value field-detalhes-value-scroll">' + (data.descricao || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">📊 Status</div>' +
                        '<div class="field-detalhes-value">' + (data.status_label || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">🎯 Prioridade</div>' +
                        '<div class="field-detalhes-value">' + (data.prioridade_label || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">🏷️ Categoria</div>' +
                        '<div class="field-detalhes-value">' + (data.categoria || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">📅 Início</div>' +
                        '<div class="field-detalhes-value">' + (data.data_inicio || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">⏰ Prazo</div>' +
                        '<div class="field-detalhes-value">' + (data.data_final || '-') + '</div>' +
                    '</div>' +

                    '<div class="modal-detalhes-field">' +
                        '<div class="field-detalhes-label">✅ Finalizada em</div>' +
                        '<div class="field-detalhes-value">' + (data.data_finalizacao || '-') + '</div>' +
                    '</div>' +

                    (data.motivo_conclusao ?
                        '<div class="modal-detalhes-field full-width">' +
                            '<div class="field-detalhes-label">💬 Motivo da conclusão</div>' +
                            '<div class="field-detalhes-value field-detalhes-value-scroll">' + data.motivo_conclusao + '</div>' +
                        '</div>'
                        : '') +

                '</div>';

            modal.classList.add('active');
        })
        .catch(function(err) {
            console.error(err);
            if (window.Notificacao) window.Notificacao.erro('Erro ao buscar detalhes.');
        });
    };

    // ==========================================================
    // Fechar modal
    // ==========================================================
    window.fecharModalDetalhes = function(event) {
        if (event && event.target) {
            const modal = document.getElementById('modalDetalhesTarefa');
            if (modal && event.target !== modal) return;
        }
        const modal = document.getElementById('modalDetalhesTarefa');
        if (modal) modal.classList.remove('active');
    };

    console.log('✅ Sistema de detalhes Tarefas (JSON) carregado!');
})();