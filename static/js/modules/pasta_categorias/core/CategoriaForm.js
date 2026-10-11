// static/js/modules/pasta_categorias/core/CategoriaForm.js
// ==========================================================
// CLASSE COMPARTILHADA — CREATE + EDIT
// ==========================================================

(function() {
    'use strict';

    function CategoriaForm(mode) {
        this.mode = mode;   // 'create' | 'edit'
        this.form = null;
        this.id = null;
        this.fields = {};
    }

    CategoriaForm.prototype.init = function() {
        var self = this;

        if (this.mode === 'create') {
            this.form = document.getElementById('formNovaCategoria');
            this.fields = {
                nome:   document.getElementById('novaCategoriaNome'),
                cor:    document.getElementById('novaCategoriaCor'),
                modulo: document.getElementById('novaCategoriaModulo')
            };
            if (this.form) {
                this.form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    self.submit('/categorias/nova_categoria/salvar');
                });
            }
        } else {
            this.form = document.getElementById('formEditarCategoria');
            this.id = document.getElementById('editarCategoriaId') ? document.getElementById('editarCategoriaId').value : null;
            this.fields = {
                nome: document.getElementById('editarCategoriaNome'),
                cor:  document.getElementById('editarCategoriaCor')
            };
            if (this.form) {
                this.form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    self.submit('/categorias/edit_categorias/salvar/' + self.id);
                });
            }
        }
    };

    CategoriaForm.prototype.getData = function() {
        var data = {};
        for (var key in this.fields) {
            if (this.fields[key]) {
                data[key] = this.fields[key].value;
            }
        }
        return data;
    };

    CategoriaForm.prototype.setData = function(data) {
        for (var key in this.fields) {
            if (this.fields[key] && data[key] !== undefined) {
                this.fields[key].value = data[key];
            }
        }
    };

    CategoriaForm.prototype.submit = function(url) {
        var self = this;
        var data = this.getData();

        // Limpa erros
        limparErrosForm();

        // Botão loading
        var btn = this.form.querySelector('button[type="submit"]');
        var textoOriginal = btn ? btn.innerHTML : '';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = 'Salvando...';
        }

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (resp.success) {
                window.Notificacao.sucesso(resp.message || 'Categoria salva!');

                if (self.mode === 'create') {
                    fecharModalNovaCategoria();
                } else {
                    fecharModalEditarCategoria();
                }

                // 🔥 Recarrega a tabela (com header HX-Request)
                if (window.htmx) {
                    window.htmx.ajax('GET', '/categorias/', {
                        target: '#tabela-container',
                        swap: 'outerHTML',
                        headers: { 'HX-Request': 'true' }
                    });
                } else {
                    window.location.reload();
                }
            } else {
                if (resp.errors) {
                    mostrarErrosForm(resp.errors);
                } else {
                    window.Notificacao.erro(resp.error || 'Erro ao salvar');
                }
            }
        })
        .catch(function(err) {
            console.error('❌ Erro:', err);
            window.Notificacao.erro('Erro ao salvar categoria');
        })
        .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = textoOriginal;
            }
        });
    };

    // ==========================================================
    // HELPERS DE VALIDAÇÃO CAMPO-A-CAMPO
    // ==========================================================
    var MAPA_IDS = {
        'nome':   'novaCategoriaNome',
        'cor':    'novaCategoriaCor',
        'modulo': 'novaCategoriaModulo'
    };

    var MAPA_IDS_EDIT = {
        'nome': 'editarCategoriaNome',
        'cor':  'editarCategoriaCor'
    };

    function mostrarErrosForm(errors) {
        var mapa = document.getElementById('formEditarCategoria') ? MAPA_IDS_EDIT : MAPA_IDS;

        errors.forEach(function(er) {
            var inputId = mapa[er.campo];
            if (!inputId) return;
            var input = document.getElementById(inputId);
            if (!input) return;

            input.classList.add('campo-erro');

            var msg = document.createElement('span');
            msg.className = 'msg-erro-campo';
            msg.textContent = er.mensagem;
            input.parentNode.appendChild(msg);
        });
    }

    function limparErrosForm() {
        document.querySelectorAll('.campo-erro').forEach(function(el) {
            el.classList.remove('campo-erro');
        });
        document.querySelectorAll('.msg-erro-campo').forEach(function(el) {
            el.remove();
        });
    }

    // Expõe
    window.CategoriaForm = CategoriaForm;
    window.mostrarErrosForm = mostrarErrosForm;
    window.limparErrosForm = limparErrosForm;

    console.log('✅ CategoriaForm carregado!');
})();