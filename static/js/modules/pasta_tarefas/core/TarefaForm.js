// static/js/modules/pasta_tarefas/core/TarefaForm.js
// ==========================================================
// TarefaForm - Classe única para os modais Nova e Editar
// ==========================================================

(function() {
    'use strict';

    function TarefaForm(formEl, options) {
        if (!formEl) throw new Error('TarefaForm: formEl obrigatório');

        this.form = formEl;
        this.options = options || {};
        this.mode = this.options.mode || 'create';
        this.onSubmitSuccess = this.options.onSubmitSuccess || null;
        this.onSubmitError = this.options.onSubmitError || null;

        var modal = formEl.closest('.fin-modal-overlay') || formEl.closest('body');

        this.el = {
            titulo:      formEl.querySelector('.js-titulo'),
            descricao:   formEl.querySelector('.js-descricao'),
            status:      formEl.querySelector('.js-status'),
            prioridade:  formEl.querySelector('.js-prioridade'),
            dataInicio:  formEl.querySelector('.js-data-inicio'),
            dataFinal:   formEl.querySelector('.js-data-final'),
            categoria:   formEl.querySelector('.js-categoria'),
        };

        this._bind();
    }

    // ==========================================================
    // EVENTOS
    // ==========================================================
    TarefaForm.prototype._bind = function() {
        var self = this;

        // Auto-ajuste do textarea
        if (this.el.descricao) {
            var ajustar = function() {
                self.el.descricao.style.height = 'auto';
                self.el.descricao.style.height = (self.el.descricao.scrollHeight) + 'px';
            };
            this.el.descricao.addEventListener('input', ajustar);
            setTimeout(ajustar, 50);
        }
    };

    // ==========================================================
    // API PÚBLICA: setData (usado no modo edit)
    // ==========================================================
    TarefaForm.prototype.setData = function(data) {
        if (!data) return;

        if (this.el.titulo)     this.el.titulo.value     = data.titulo || '';
        if (this.el.descricao)  this.el.descricao.value  = data.descricao || '';
        if (this.el.status)     this.el.status.value     = data.status || 'pendente';
        if (this.el.prioridade) this.el.prioridade.value = data.prioridade || 'media';
        if (this.el.dataInicio) this.el.dataInicio.value = data.data_inicio || '';
        if (this.el.dataFinal)  this.el.dataFinal.value  = data.data_final || '';
        if (this.el.categoria)  this.el.categoria.value  = data.categoria_id || '';

        // Atualiza altura do textarea depois de setar valor
        if (this.el.descricao) {
            this.el.descricao.style.height = 'auto';
            this.el.descricao.style.height = (this.el.descricao.scrollHeight) + 'px';
        }
    };

    // ==========================================================
    // API PÚBLICA: getData
    // ==========================================================
    TarefaForm.prototype.getData = function() {
        return {
            titulo:       this.el.titulo     ? this.el.titulo.value.trim()     : '',
            descricao:    this.el.descricao  ? this.el.descricao.value.trim()  : '',
            status:       this.el.status     ? this.el.status.value            : 'pendente',
            prioridade:   this.el.prioridade ? this.el.prioridade.value        : 'media',
            data_inicio:  this.el.dataInicio ? this.el.dataInicio.value        : '',
            data_final:   this.el.dataFinal  ? this.el.dataFinal.value         : '',
            categoria_id: this.el.categoria  ? this.el.categoria.value         : '',
        };
    };

    // ==========================================================
    // API PÚBLICA: reset
    // ==========================================================
    TarefaForm.prototype.reset = function() {
        this.form.reset();

        if (this.el.titulo)     this.el.titulo.value     = '';
        if (this.el.descricao)  this.el.descricao.value  = '';
        if (this.el.status)     this.el.status.value     = 'pendente';
        if (this.el.prioridade) this.el.prioridade.value = 'media';
        if (this.el.dataInicio) this.el.dataInicio.value = '';
        if (this.el.dataFinal)  this.el.dataFinal.value  = '';
        if (this.el.categoria)  this.el.categoria.value  = '';

        if (this.el.descricao) {
            this.el.descricao.style.height = 'auto';
        }
    };

    // ==========================================================
    // API PÚBLICA: submit (SEMPRE JSON)
    // ==========================================================
    TarefaForm.prototype.submit = function(url) {
        var self = this;
        var data = this.getData();

        // ==========================================================
        // VALIDAÇÕES CLIENT-SIDE (AJAX, sem required HTML)
        // ==========================================================
        if (!data.titulo) {
            if (window.Notificacao) window.Notificacao.aviso('Título é obrigatório.');
            return Promise.reject(new Error('titulo vazio'));
        }
        if (data.titulo.length > 200) {
            if (window.Notificacao) window.Notificacao.aviso('Título não pode passar de 200 caracteres.');
            return Promise.reject(new Error('titulo longo'));
        }

        if (!data.descricao) {
            if (window.Notificacao) window.Notificacao.aviso('Descrição é obrigatória.');
            return Promise.reject(new Error('descricao vazia'));
        }

        if (!data.data_inicio) {
            if (window.Notificacao) window.Notificacao.aviso('Data de início é obrigatória.');
            return Promise.reject(new Error('data_inicio vazia'));
        }

        // ==========================================================
        // ENVIO
        // ==========================================================
        var headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        };

        return fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        })
        .then(function(r) { return r.json().then(function(j) { return { ok: r.ok, data: j }; }); })
        .then(function(res) {
            if (!res.ok || res.data.success === false) {
                var msg;
                if (res.data.errors && res.data.errors.length > 0) {
                    msg = res.data.errors[0].mensagem;
                } else {
                    msg = res.data.error || res.data.message || 'Erro ao salvar.';
                }
                if (self.onSubmitError) self.onSubmitError(msg);
                else if (window.Notificacao) window.Notificacao.erro(msg);
                throw new Error(msg);
            }

            if (self.onSubmitSuccess) self.onSubmitSuccess(res.data);
            return res.data;
        });
    };

    // ==========================================================
    // Exposição global
    // ==========================================================
    window.TarefaForm = TarefaForm;

    console.log('✅ TarefaForm carregado!');
})();