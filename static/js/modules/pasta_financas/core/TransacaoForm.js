// ==========================================================
// TransacaoForm - Classe única para os modais Nova e Editar
// ==========================================================
// Uso:
//   var form = new TransacaoForm(formEl, { mode: 'create'|'edit', onSubmitSuccess: fn });
//   form.setData({ ... });   // popula tudo (inclusive parcelas)
//   form.reset();            // limpa
//
// Nenhum #id global. Tudo escopado por form.querySelector('.js-*')
// ==========================================================

(function() {
    'use strict';

    function TransacaoForm(formEl, options) {
        if (!formEl) throw new Error('TransacaoForm: formEl obrigatório');

        this.form = formEl;
        this.options = options || {};
        this.mode = this.options.mode || 'create';
        this.onSubmitSuccess = this.options.onSubmitSuccess || null;
        this.onSubmitError = this.options.onSubmitError || null;

        // Elementos internos (escopados — sem colisão)
        this.el = {
            tipoHidden:        formEl.querySelector('.js-tipo-hidden'),
            tipoBtns:          formEl.querySelectorAll('.js-tipo-btn'),
            descricao:         formEl.querySelector('.js-descricao'),
            categoria:         formEl.querySelector('.js-categoria'),
            valorTotal:        formEl.querySelector('.js-valor-total'),
            totalParcelas:     formEl.querySelector('.js-total-parcelas'),
            dataEmissao:       formEl.querySelector('.js-data-emissao'),
            dataVencimento:    formEl.querySelector('.js-data-vencimento'),
            primeiroVenc:      formEl.querySelector('.js-primeiro-vencimento'),
            intervaloDias:     formEl.querySelector('.js-intervalo-dias'),
            parcelasConfig:    formEl.querySelector('.js-parcelas-config'),
            parcelasWrapper:   formEl.querySelector('.js-parcelas-wrapper'),
            parcelasBody:      formEl.querySelector('.js-parcelas-body'),
            btnDistribuir:     formEl.querySelector('.js-btn-distribuir')
        };

        // Estado interno das parcelas em modo edit (fonte da verdade do front)
        this._parcelasCarregadas = null;

        this._bind();
    }

    // ==========================================================
    // EVENTOS
    // ==========================================================
    TransacaoForm.prototype._bind = function() {
        var self = this;

        // Tipo (receita / despesa)
        this.el.tipoBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                self.el.tipoBtns.forEach(function(b) { b.classList.remove('active'); });
                btn.classList.add('active');
                var tipo = btn.dataset.tipo;
                if (self.el.tipoHidden) self.el.tipoHidden.value = (tipo === 'vazio') ? '' : tipo;
            });
        });

        // Máscara monetária + recálculo
        if (this.el.valorTotal) {
            this.el.valorTotal.addEventListener('input', function(e) {
                if (window.FormatadoresFinancas) {
                    e.target.value = window.FormatadoresFinancas.mascaraMoeda(e.target);
                }
                self._recalcularSeVazio();
            });
        }

        // Nº de parcelas
        if (this.el.totalParcelas) {
            this.el.totalParcelas.addEventListener('input', function() {
                self._onTotalParcelasChange();
            });
        }

        // Primeiro vencimento
        if (this.el.primeiroVenc) {
            this.el.primeiroVenc.addEventListener('change', function() {
                self._onTotalParcelasChange();
            });
        }

        // Botão "Distribuir igualmente"
        if (this.el.btnDistribuir) {
            this.el.btnDistribuir.addEventListener('click', function() {
                self.distribuirIgualmente();
            });
        }
    };

    TransacaoForm.prototype._onTotalParcelasChange = function() {
        // Se o usuário mudou o total de parcelas manualmente, descarta o cache
        // das parcelas do banco e regenera do zero
        this._parcelasCarregadas = null;
        this._renderParcelasDoZero();
    };

    TransacaoForm.prototype._recalcularSeVazio = function() {
        // Se não há parcelas renderizadas ainda (create vazio), nada a fazer
        if (!this.el.parcelasBody) return;
    };

    // ==========================================================
    // API PÚBLICA: setData (usado no modo edit)
    // ==========================================================
    TransacaoForm.prototype.setData = function(data) {
        if (!data) return;

        var self = this;

        // Campos simples
        if (this.el.descricao)    this.el.descricao.value = data.descricao || '';

        if (this.el.valorTotal) {
            this.el.valorTotal.value = parseFloat(data.valor_total || 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2, maximumFractionDigits: 2
            });
        }

        if (this.el.dataEmissao)    this.el.dataEmissao.value = data.data_vencimento || '';
        if (this.el.dataVencimento) this.el.dataVencimento.value = data.data_vencimento || '';
        if (this.el.primeiroVenc)   this.el.primeiroVenc.value = data.data_vencimento || '';
        if (this.el.categoria)      this.el.categoria.value = data.categoria_id || '';
        if (this.el.totalParcelas)  this.el.totalParcelas.value = data.total_parcelas || 1;
        if (this.el.tipoHidden)     this.el.tipoHidden.value = data.tipo || '';

        // Botões de tipo
        this.el.tipoBtns.forEach(function(btn) {
            btn.classList.remove('active');
            if (btn.dataset.tipo === data.tipo) btn.classList.add('active');
        });

        // Parcelas (se vierem)
        var parcelas = (data.parcelas || []).map(function(p, i) {
            return {
                numero: p.numero_parcela || (i + 1),
                data_vencimento: p.data_vencimento || '',
                valor: p.valor || 0
            };
        });

        this._parcelasCarregadas = (parcelas.length > 0) ? parcelas : null;

        // Decide: renderiza do banco ou gera do zero
        if (this._parcelasCarregadas && this._parcelasCarregadas.length > 1) {
            this._renderParcelas(this._parcelasCarregadas);
        } else {
            this._renderParcelasDoZero();
        }
    };

    // ==========================================================
    // API PÚBLICA: getData (serializa pro POST)
    // ==========================================================
    TransacaoForm.prototype.getData = function() {
        var tipo = this.el.tipoHidden ? this.el.tipoHidden.value : '';
        var valorTotal = this.el.valorTotal && window.FormatadoresFinancas
            ? window.FormatadoresFinancas.paraFloat(this.el.valorTotal.value)
            : 0;
        var totalParcelas = this.el.totalParcelas ? (parseInt(this.el.totalParcelas.value) || 1) : 1;

        var parcelas = [];
        if (this.el.parcelasBody) {
            this.el.parcelasBody.querySelectorAll('tr').forEach(function(row, idx) {
                var v = row.querySelector('.js-parcela-valor');
                var d = row.querySelector('.js-parcela-data');
                if (v && d) {
                    parcelas.push({
                        numero: idx + 1,
                        valor: window.FormatadoresFinancas
                            ? window.FormatadoresFinancas.paraFloat(v.value)
                            : parseFloat(v.value) || 0,
                        vencimento: d.value
                    });
                }
            });
        }

        return {
            tipo: tipo,
            descricao: this.el.descricao ? this.el.descricao.value.trim() : '',
            categoria_id: this.el.categoria ? this.el.categoria.value : '',
            valor_total: valorTotal,
            data_emissao: this.el.dataEmissao ? this.el.dataEmissao.value : '',
            data_vencimento: this.el.dataVencimento ? this.el.dataVencimento.value : '',
            primeiroVencimento: this.el.primeiroVenc ? this.el.primeiroVenc.value : '',
            intervaloDias: this.el.intervaloDias ? (parseInt(this.el.intervaloDias.value) || 30) : 30,
            total_parcelas: totalParcelas,
            parcelas: parcelas
        };
    };

    // ==========================================================
    // API PÚBLICA: reset
    // ==========================================================
    TransacaoForm.prototype.reset = function() {
        this.form.reset();
        this._parcelasCarregadas = null;

        if (this.el.tipoHidden) this.el.tipoHidden.value = '';
        this.el.tipoBtns.forEach(function(b) { b.classList.remove('active'); });

        if (this.el.valorTotal) this.el.valorTotal.value = '0,00';
        if (this.el.totalParcelas) this.el.totalParcelas.value = '1';
        if (this.el.parcelasConfig) this.el.parcelasConfig.style.display = 'none';
        if (this.el.parcelasWrapper) this.el.parcelasWrapper.style.display = 'none';
        if (this.el.parcelasBody) {
            this.el.parcelasBody.innerHTML =
                '<tr><td colspan="3" class="parcelas-vazio">Selecione mais de 1 parcela</td></tr>';
        }
    };

    // ==========================================================
    // API PÚBLICA: submit
    // ==========================================================
    TransacaoForm.prototype.submit = function(url) {
        var self = this;
        var data = this.getData();

        // Validação básica
        if (!data.tipo) {
            if (window.Notificacao) window.Notificacao.aviso('Selecione o tipo (Receita ou Despesa).');
            return Promise.reject(new Error('tipo vazio'));
        }
        if (!data.descricao) {
            if (window.Notificacao) window.Notificacao.aviso('Descrição é obrigatória.');
            return Promise.reject(new Error('descricao vazia'));
        }
        if (data.valor_total <= 0) {
            if (window.Notificacao) window.Notificacao.aviso('Informe um valor maior que zero.');
            return Promise.reject(new Error('valor invalido'));
        }

        var body = this.mode === 'create'
            ? this._toFormData(data)
            : JSON.stringify(data);

        var headers = { 'X-Requested-With': 'XMLHttpRequest' };
        if (this.mode !== 'create') headers['Content-Type'] = 'application/json';

        return fetch(url, {
            method: 'POST',
            headers: headers,
            body: body
        })
        .then(function(r) { return r.json().then(function(j) { return { ok: r.ok, data: j }; }); })
        .then(function(res) {
            if (!res.ok || res.data.success === false) {
                var msg = res.data.error || res.data.message || 'Erro ao salvar.';
                if (self.onSubmitError) self.onSubmitError(msg);
                else if (window.Notificacao) window.Notificacao.erro(msg);
                throw new Error(msg);
            }
            if (self.onSubmitSuccess) self.onSubmitSuccess(res.data);
            return res.data;
        });
    };

    // ==========================================================
    // RENDERIZAÇÃO DE PARCELAS
    // ==========================================================
    TransacaoForm.prototype._renderParcelas = function(lista) {
        if (!this.el.parcelasBody) return;

        if (this.el.parcelasConfig) this.el.parcelasConfig.style.display = 'block';
        if (this.el.parcelasWrapper) this.el.parcelasWrapper.style.display = 'block';

        var html = '';
        lista.forEach(function(p, index) {
            var num = p.numero || (index + 1);
            var dataVenc = p.data_vencimento || '';
            var val = typeof p.valor === 'number'
                ? p.valor.toFixed(2).replace('.', ',')
                : (p.valor || '0,00');

            html += '<tr>' +
                '<td class="parcelas-td-num"><span class="badge-parcela-num">' + num + '</span></td>' +
                '<td><input type="text" class="form-control form-control-sm parcela-valor js-parcela-valor" value="' + val + '"></td>' +
                '<td><input type="date" class="form-control form-control-sm parcela-data js-parcela-data" value="' + dataVenc + '"></td>' +
                '</tr>';
        });
        this.el.parcelasBody.innerHTML = html;
    };

    TransacaoForm.prototype._renderParcelasDoZero = function() {
        if (!this.el.totalParcelas || !this.el.parcelasBody) return;

        var numParcelas = parseInt(this.el.totalParcelas.value) || 1;

        if (numParcelas <= 1) {
            if (this.el.parcelasConfig) this.el.parcelasConfig.style.display = 'none';
            if (this.el.parcelasWrapper) this.el.parcelasWrapper.style.display = 'none';
            this.el.parcelasBody.innerHTML =
                '<tr><td colspan="3" class="parcelas-vazio">Selecione mais de 1 parcela</td></tr>';
            return;
        }

        // Se tem cache do banco e o número bate, usa o cache
        if (this._parcelasCarregadas && this._parcelasCarregadas.length === numParcelas) {
            this._renderParcelas(this._parcelasCarregadas);
            return;
        }

        // Senão gera do zero
        if (this.el.parcelasConfig) this.el.parcelasConfig.style.display = 'block';
        if (this.el.parcelasWrapper) this.el.parcelasWrapper.style.display = 'block';

        var valorTotal = 0;
        if (this.el.valorTotal) {
            valorTotal = window.FormatadoresFinancas
                ? window.FormatadoresFinancas.paraFloat(this.el.valorTotal.value)
                : 0;
        }

        var valorBase = Math.floor((valorTotal / numParcelas) * 100) / 100;
        var resto = parseFloat((valorTotal - (valorBase * numParcelas)).toFixed(2));

        var primeiroVenc = this.el.primeiroVenc ? this.el.primeiroVenc.value : '';
        var intervalo = this.el.intervaloDias ? (parseInt(this.el.intervaloDias.value) || 30) : 30;

        var html = '';
        var dataAtual = primeiroVenc ? new Date(primeiroVenc + 'T00:00:00') : new Date();

        for (var i = 1; i <= numParcelas; i++) {
            var valorParcela = (i === 1) ? (valorBase + resto) : valorBase;

            var ano = dataAtual.getFullYear();
            var mes = String(dataAtual.getMonth() + 1).padStart(2, '0');
            var dia = String(dataAtual.getDate()).padStart(2, '0');
            var dataFmt = ano + '-' + mes + '-' + dia;

            html += '<tr>' +
                '<td class="parcelas-td-num"><span class="badge-parcela-num">' + i + '</span></td>' +
                '<td><input type="text" class="form-control form-control-sm parcela-valor js-parcela-valor" value="' + valorParcela.toFixed(2).replace('.', ',') + '"></td>' +
                '<td><input type="date" class="form-control form-control-sm parcela-data js-parcela-data" value="' + dataFmt + '"></td>' +
                '</tr>';

            dataAtual.setDate(dataAtual.getDate() + intervalo);
        }
        this.el.parcelasBody.innerHTML = html;
    };

    // ==========================================================
    // API PÚBLICA: distribuirIgualmente
    // ==========================================================
    TransacaoForm.prototype.distribuirIgualmente = function() {
        var rows = this.el.parcelasBody ? this.el.parcelasBody.querySelectorAll('tr') : [];
        if (rows.length === 0) return;

        var valorTotal = window.FormatadoresFinancas
            ? window.FormatadoresFinancas.paraFloat(this.el.valorTotal.value)
            : 0;
        var n = rows.length;
        var valorBase = Math.floor((valorTotal / n) * 100) / 100;
        var resto = parseFloat((valorTotal - (valorBase * n)).toFixed(2));

        rows.forEach(function(row, idx) {
            var input = row.querySelector('.js-parcela-valor');
            if (!input) return;
            var v = (idx === 0) ? (valorBase + resto) : valorBase;
            input.value = v.toFixed(2).replace('.', ',');
        });
    };

    // ==========================================================
    // HELPER: FormData para o backend no modo create
    // ==========================================================
    TransacaoForm.prototype._toFormData = function(data) {
        var fd = new FormData();
        fd.append('tipo', data.tipo);
        fd.append('descricao', data.descricao);
        fd.append('categoria_id', data.categoria_id || '');
        fd.append('valor_total', data.valor_total);
        fd.append('data_emissao', data.data_emissao);
        fd.append('data_vencimento', data.data_vencimento);
        fd.append('total_parcelas', data.total_parcelas);
        fd.append('intervaloDias', data.intervaloDias);
        fd.append('primeiroVencimento', data.primeiroVencimento);

        // Parcelas dinâmicas (formato esperado pelo backend: parcela_valor_1, parcela_valor_2...)
        (data.parcelas || []).forEach(function(p, i) {
            fd.append('parcela_valor_' + (i + 1), p.valor);
        });

        return fd;
    };

    // ==========================================================
    // Exposição global
    // ==========================================================
    window.TransacaoForm = TransacaoForm;

    console.log('✅ TransacaoForm carregado!');
})();