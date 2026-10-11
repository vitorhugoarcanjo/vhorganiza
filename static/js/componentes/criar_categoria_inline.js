// static/js/components/criar_categoria_inline.js
// ==========================================================
// CRIAR CATEGORIA INLINE (modal empilhado, 2 blocos)
// ==========================================================

(function() {
    'use strict';

    var moduloAtivo = null;

    // ==========================================================
    // ABRIR
    // ==========================================================
    window.abrirModalNovaCategoriaInline = function(modulo) {
        moduloAtivo = modulo || 'tarefas';

        var modal = document.getElementById('modalNovaCategoriaInline');
        if (!modal) {
            console.error('❌ modalNovaCategoriaInline não existe no DOM');
            return;
        }

        // Limpa campos
        var nome = document.getElementById('catInlineNome');
        var cor = document.getElementById('catInlineCor');
        var modInput = document.getElementById('catInlineModulo');
        var modHidden = document.getElementById('catInlineModuloHidden');

        if (nome) nome.value = '';
        if (cor) cor.value = '#2563eb';
        if (modInput) modInput.value = moduloAtivo === 'tarefas' ? '🔒 Tarefas' : '🔒 Finanças';
        if (modHidden) modHidden.value = moduloAtivo;

        // Limpa erros
        document.querySelectorAll('.campo-erro').forEach(function(el) {
            el.classList.remove('campo-erro');
        });
        document.querySelectorAll('.msg-erro-campo').forEach(function(el) {
            el.remove();
        });

        // Carrega lista de categorias existentes
        carregarListaCategorias(moduloAtivo);

        modal.classList.add('active');

        // Foco no input
        setTimeout(function() {
            if (nome) nome.focus();
        }, 100);
    };

    // ==========================================================
    // FECHAR
    // ==========================================================
    window.fecharModalNovaCategoriaInline = function() {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal) modal.classList.remove('active');
        moduloAtivo = null;
    };

    // ==========================================================
    // CARREGAR LISTA
    // ==========================================================
    function carregarListaCategorias(modulo) {
        var lista = document.getElementById('catInlineLista');
        var contador = document.getElementById('catInlineContador');

        if (!lista) return;
        lista.innerHTML = '<div style="text-align:center;color:var(--texto-discreto);padding:20px;">Carregando...</div>';

        fetch('/categorias/modal-lista?modulo=' + modulo)
            .then(function(r) { return r.text(); })
            .then(function(html) {
                // 🔥 O HTML que volta JÁ É a lista
                lista.innerHTML = html;

                // Conta itens
                var itens = lista.querySelectorAll('.modal-cat-item');
                if (contador) contador.textContent = itens.length;
            })
            .catch(function(err) {
                console.error('❌ Erro ao carregar categorias:', err);
                lista.innerHTML = '<div style="text-align:center;color:#ef4444;padding:20px;">Erro ao carregar</div>';
            });
    }

    // ==========================================================
    // SALVAR
    // ==========================================================
    window.salvarCategoriaInline = function() {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (!modal || !moduloAtivo) return;

        var nomeInput = document.getElementById('catInlineNome');
        var corInput = document.getElementById('catInlineCor');

        var nome = (nomeInput ? nomeInput.value : '').trim();
        var cor = (corInput ? corInput.value : '#2563eb').trim();

        // Validação front
        if (!nome) {
            if (nomeInput) {
                nomeInput.classList.add('campo-erro');
                var msg = document.createElement('span');
                msg.className = 'msg-erro-campo';
                msg.textContent = 'Nome é obrigatório';
                nomeInput.parentNode.appendChild(msg);
            }
            return;
        }

        // Botão loading
        var btn = modal.querySelector('.btn-success-pure');
        var textoOriginal = btn ? btn.innerHTML : '';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = 'Criando...';
        }

        fetch('/categorias/nova_categoria/salvar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome: nome,
                cor: cor,
                modulo: moduloAtivo
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                // 🔥 Adiciona <option> no <select> do modal de trás
                var selects = document.querySelectorAll('.js-categoria');
                selects.forEach(function(select) {
                    var option = new Option(nome, data.categoria_id, true, true);
                    option.setAttribute('data-cor', cor);
                    select.add(option);
                    select.value = data.categoria_id;
                });

                // Toast
                if (window.Notificacao) {
                    window.Notificacao.sucesso('Categoria "' + nome + '" criada!');
                }

                // Fecha o mini-modal
                window.fecharModalNovaCategoriaInline();
            } else {
                if (data.errors) {
                    data.errors.forEach(function(er) {
                        if (er.campo === 'nome' && nomeInput) {
                            nomeInput.classList.add('campo-erro');
                            var msg = document.createElement('span');
                            msg.className = 'msg-erro-campo';
                            msg.textContent = er.mensagem;
                            nomeInput.parentNode.appendChild(msg);
                        }
                    });
                } else {
                    if (window.Notificacao) {
                        window.Notificacao.erro(data.error || 'Erro ao criar');
                    }
                }
            }
        })
        .catch(function(err) {
            console.error('❌ Erro:', err);
            if (window.Notificacao) window.Notificacao.erro('Erro ao criar categoria');
        })
        .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = textoOriginal;
            }
        });
    };

    // ==========================================================
    // ESC / clique fora
    // ==========================================================
    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Escape') return;

        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal && modal.classList.contains('active')) {
            e.stopPropagation();
            window.fecharModalNovaCategoriaInline();
        }
    }, true);

    document.addEventListener('click', function(e) {
        var modal = document.getElementById('modalNovaCategoriaInline');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            window.fecharModalNovaCategoriaInline();
        }
    });

    console.log('✅ Criar categoria inline (compartilhado) carregado!');
})();