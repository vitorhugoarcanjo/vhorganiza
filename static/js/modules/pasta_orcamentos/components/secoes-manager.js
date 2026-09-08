// ==========================================================
// SEÇÕES - GERENCIADOR (GLOBAL - REUTILIZÁVEL)
// ==========================================================
// 
// 📌 FUNÇÃO: Gerencia o CRUD de seções (adicionar, editar, remover)
// 
// 🔧 COMO USAR:
//   var gerenciador = window.criarGerenciadorSecoes({
//       containerId: 'novo-secoes-container',
//       previewContainerId: 'secaoPreviewContainer',
//       contadorId: 'novoSecoesCount',
//       modalSecaoId: 'modalNovaSecaoNovo',
//       formSecaoId: 'formNovaSecaoNovo',
//       tituloId: 'novaSecaoTituloNovo',
//       conteudoId: 'novaSecaoConteudoNovo',
//       camposEspecificosId: 'camposEspecificosNovo',
//       tipoBtnsSelector: '#modalNovaSecaoNovo .orc-tipo-btn',
//       modalTituloId: 'modalSecaoTituloNovo',
//       btnTextoId: 'btnAdicionarTextoNovo'
//   });
//   gerenciador.carregarSecoes([]);
//   gerenciador.abrirModalSecao();
// 
// 📝 MÉTODOS PÚBLICOS:
//   - carregarSecoes(secoes)        → Carrega seções existentes
//   - getEstrutura()                → Retorna array de seções
//   - renderizar()                  → Renderiza a lista
//   - adicionarSecao(secao)         → Adiciona uma seção
//   - removerSecao(index)           → Remove uma seção
//   - editarSecao(index)            → Abre modal para editar
//   - finalizarEdicao(secao)        → Salva a edição
//   - abrirModalSecao()             → Abre modal de nova seção
//   - fecharModalSecao()            → Fecha modal de seção
//   - selecionarTipo(btn)           → Seleciona o tipo
//   - atualizarPreview()            → Atualiza o preview
//   - formatarValor(input)          → Formata valor monetário
// 
// 📍 ONDE É USADO:
//   - modal_novo_orcamento.js (gerencia as seções do NOVO)
//   - modal_editar_orcamento.js (gerencia as seções do EDITAR)
// 
// 🚀 PARA ADICIONAR UM NOVO TIPO DE SEÇÃO:
//   1. Vá em secoes-types.js e adicione o tipo com template
//   2. Volte aqui e em mostrarCamposEspecificos adicione os campos
//   3. Em atualizarPreview adicione a leitura dos campos
//   4. Em finalizarEdicao adicione o salvamento dos campos
//   5. Em editarSecao adicione o carregamento dos campos
// 
// ⚠️ ATENÇÃO: IDs são passados via opcoes para cada modal
// ==========================================================
(function() {
    'use strict';

    function GerenciadorSecoes(opcoes) {
        var self = this;
        
        this.estrutura = [];
        this.editandoIndex = null;
        this.tipoSelecionado = 'secao';
        
        this.containerId = opcoes.containerId || 'secoes-container';
        this.previewContainerId = opcoes.previewContainerId || 'secaoPreviewContainer';
        this.contadorId = opcoes.contadorId || 'secoesCount';
        this.modalSecaoId = opcoes.modalSecaoId || 'modalNovaSecao';
        this.formSecaoId = opcoes.formSecaoId || 'formNovaSecao';
        
        this.ids = {
            titulo: opcoes.tituloId || 'novaSecaoTitulo',
            conteudo: opcoes.conteudoId || 'novaSecaoConteudo',
            camposEspecificos: opcoes.camposEspecificosId || 'camposEspecificos',
            tipoBtns: opcoes.tipoBtnsSelector || '#modalNovaSecao .orc-tipo-btn',
            modalTitulo: opcoes.modalTituloId || 'modalSecaoTitulo',
            btnTexto: opcoes.btnTextoId || 'btnAdicionarTexto'
        };
        
        this.tiposSemConteudo = ['valor', 'observacao', 'tabela', 'lista'];
        
        this.atualizarVisibilidadeConteudo = function(tipo) {
            var textareaConteudo = document.getElementById(self.ids.conteudo);
            if (!textareaConteudo) return;
            textareaConteudo.style.display = self.tiposSemConteudo.includes(tipo) ? 'none' : 'block';
        };
        
        this.getContainer = function() {
            return document.getElementById(self.containerId);
        };
        
        this.getPreviewContainer = function() {
            return document.getElementById(self.previewContainerId);
        };
        
        this.atualizarContador = function() {
            if (window.SecoesRender) {
                window.SecoesRender.atualizarContador(self.getContainer(), self.estrutura);
            }
        };
        
        this.renderizar = function() {
            var container = self.getContainer();
            if (container && window.SecoesRender) {
                window.SecoesRender.renderizar(container, self.estrutura, {
                    onEdit: self.editarSecao.bind(self),
                    onRemove: self.removerSecao.bind(self),
                    onTituloChange: function(i, v) { self.estrutura[i].titulo = v; }
                });
                self.atualizarContador();
            }
        };
        
        this.carregarSecoes = function(secoes) {
            self.estrutura = secoes || [];
            self.renderizar();
        };
        
        this.getEstrutura = function() {
            return self.estrutura;
        };
        
        this.adicionarSecao = function(secao) {
            self.estrutura.push(secao);
            self.renderizar();
            self.fecharModalSecao();
            if (window.Notificacao) window.Notificacao.sucesso('Seção adicionada!');
        };
        
        this.removerSecao = function(index) {
            var titulo = self.estrutura[index]?.titulo || 'Seção';
            if (confirm('Remover a seção "' + titulo + '"?')) {
                self.estrutura.splice(index, 1);
                self.renderizar();
                if (window.Notificacao) window.Notificacao.aviso('Seção removida!');
            }
        };
        
        this.editarSecao = function(index) {
            self.editandoIndex = index;
            var secao = self.estrutura[index];
            
            document.getElementById(self.ids.titulo).value = secao.titulo || '';
            
            var textareaConteudo = document.getElementById(self.ids.conteudo);
            if (secao.tipo === 'valor' || secao.tipo === 'lista' || secao.tipo === 'numerada' || secao.tipo === 'tabela') {
                textareaConteudo.value = '';
            } else {
                textareaConteudo.value = secao.conteudo || '';
            }
            
            self.atualizarVisibilidadeConteudo(secao.tipo);
            
            document.querySelectorAll(self.ids.tipoBtns).forEach(function(btn) {
                btn.classList.remove('active');
                if (btn.dataset.tipo === secao.tipo) btn.classList.add('active');
            });
            self.tipoSelecionado = secao.tipo || 'secao';
            self.mostrarCamposEspecificos(self.tipoSelecionado);
            
            if (self.tipoSelecionado === 'valor') {
                setTimeout(function() {
                    var v = document.getElementById('secaoValor');
                    var c = document.getElementById('secaoValorConteudo');
                    var d = document.getElementById('secaoValorDescricao');
                    if (v) v.value = secao.valor || '0,00';
                    if (c) c.value = secao.conteudo || '';
                    if (d) d.value = secao.descricao_valor || '';
                }, 50);
            } else if (self.tipoSelecionado === 'lista' || self.tipoSelecionado === 'numerada') {
                setTimeout(function() {
                    var i = document.getElementById('secaoListaItens');
                    if (i && secao.itens) i.value = secao.itens.join('\n');
                }, 50);
            } else if (self.tipoSelecionado === 'tabela') {
                setTimeout(function() {
                    var c = document.getElementById('secaoTabelaColunas');
                    var l = document.getElementById('secaoTabelaLinhas');
                    if (c && secao.colunas) c.value = secao.colunas.join(', ');
                    if (l && secao.linhas) {
                        l.value = secao.linhas.map(function(linha) {
                            return linha.join(' | ');
                        }).join('\n');
                    }
                }, 50);
            }
            
            var previewContainer = self.getPreviewContainer();
            if (previewContainer && window.SecoesPreview) {
                previewContainer.innerHTML = window.SecoesPreview.previewSecao(secao);
            }
            
            document.getElementById(self.ids.modalTitulo).innerHTML = '<i class="bi bi-pencil"></i> Editar Seção';
            document.getElementById(self.ids.btnTexto).textContent = 'Atualizar';
            document.getElementById(self.modalSecaoId).classList.add('active');
        };
        
        this.finalizarEdicao = function(secao) {
            if (secao.tipo === 'valor') {
                var v = document.getElementById('secaoValor');
                var c = document.getElementById('secaoValorConteudo');
                var d = document.getElementById('secaoValorDescricao');
                if (v) secao.valor = v.value || '0,00';
                if (c) secao.conteudo = c.value;
                if (d) secao.descricao_valor = d.value;
            }
            
            if (self.editandoIndex !== null) {
                self.estrutura[self.editandoIndex] = secao;
                self.editandoIndex = null;
                if (window.Notificacao) window.Notificacao.sucesso('Seção atualizada!');
            } else {
                self.estrutura.push(secao);
                if (window.Notificacao) window.Notificacao.sucesso('Seção adicionada!');
            }
            self.renderizar();
            self.fecharModalSecao();
        };
        
        this.abrirModalSecao = function() {
            self.editandoIndex = null;
            document.getElementById(self.ids.titulo).value = '';
            document.getElementById(self.ids.conteudo).value = '';
            self.atualizarVisibilidadeConteudo('secao');
            
            document.querySelectorAll(self.ids.tipoBtns).forEach(function(btn) { btn.classList.remove('active'); });
            document.querySelector(self.ids.tipoBtns + '[data-tipo="secao"]')?.classList.add('active');
            self.tipoSelecionado = 'secao';
            document.getElementById(self.ids.camposEspecificos).className = 'orc-campos-especificos';
            document.getElementById(self.ids.camposEspecificos).innerHTML = '';
            
            var previewContainer = self.getPreviewContainer();
            if (previewContainer && window.SecoesPreview) {
                previewContainer.innerHTML = '<div class="orc-secao-preview-empty">A seção aparecerá aqui</div>';
            }
            
            document.getElementById(self.ids.modalTitulo).innerHTML = '<i class="bi bi-plus-circle"></i> Nova Seção';
            document.getElementById(self.ids.btnTexto).textContent = 'Adicionar';
            document.getElementById(self.modalSecaoId).classList.add('active');
        };
        
        this.fecharModalSecao = function() {
            document.getElementById(self.modalSecaoId).classList.remove('active');
        };
        
        this.selecionarTipo = function(btn) {
            document.querySelectorAll(self.ids.tipoBtns).forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            self.tipoSelecionado = btn.dataset.tipo;
            self.atualizarVisibilidadeConteudo(self.tipoSelecionado);
            self.mostrarCamposEspecificos(self.tipoSelecionado);
            self.atualizarPreview();
        };
        
        this.mostrarCamposEspecificos = function(tipo) {
            var container = document.getElementById(self.ids.camposEspecificos);
            if (!container) return;
            
            var html = '';
            if (tipo === 'tabela') {
                html = `
                    <div class="orc-campo-group">
                        <label>Colunas</label>
                        <input type="text" id="secaoTabelaColunas" placeholder="Coluna1, Coluna2, Coluna3" oninput="window.atualizarPreviewSecao()">
                    </div>
                    <div class="orc-campo-group">
                        <label>Linhas</label>
                        <textarea id="secaoTabelaLinhas" rows="3" placeholder="Linha1 | Valor1 | Valor2" oninput="window.atualizarPreviewSecao()"></textarea>
                    </div>
                `;
            } else if (tipo === 'lista' || tipo === 'numerada') {
                html = `
                    <div class="orc-campo-group">
                        <label>Itens</label>
                        <textarea id="secaoListaItens" rows="4" placeholder="Item 1&#10;Item 2&#10;Item 3" oninput="window.atualizarPreviewSecao()"></textarea>
                    </div>
                `;
            } else if (tipo === 'destaque') {
                html = `
                    <div class="orc-campo-group">
                        <label>Cor</label>
                        <select id="secaoDestaqueCor" onchange="window.atualizarPreviewSecao()">
                            <option value="azul">🔵 Azul</option>
                            <option value="verde">🟢 Verde</option>
                            <option value="vermelho">🔴 Vermelho</option>
                            <option value="amarelo">🟡 Amarelo</option>
                        </select>
                    </div>
                `;
            } else if (tipo === 'valor') {
                // 🔥 SÓ RENDERIZA OS CAMPOS ESPECÍFICOS DO VALOR
                // O TEXTAREA GENÉRICO NÃO É RENDERIZADO AQUI
                html = `
                    <div class="orc-campos-valor">
                        <div class="orc-campo-group orc-campo-valor-descricao" style="grid-column: 1 / 3;">
                            <label><i class="bi bi-list-ul"></i> Itens do Valor</label>
                            <textarea id="secaoValorConteudo" rows="6" 
                                    placeholder="Ex: Dados Gerais: R$ 50,00&#10;Histórico: R$ 350,00" 
                                    oninput="window.atualizarPreviewSecao()"
                                    style="min-height: 120px; font-size: 0.85rem;"></textarea>
                        </div>
                        <div class="orc-campo-group orc-campo-valor" style="grid-column: 1 / 2;">
                            <label><i class="bi bi-currency-dollar"></i> Valor (R$)</label>
                            <div class="orc-input-valor-wrapper">
                                <span class="orc-input-valor-prefixo">R$</span>
                                <input type="text" id="secaoValor" 
                                    placeholder="1.500,00" 
                                    oninput="formatarValor(this); window.atualizarPreviewSecao()" 
                                    value="0,00">
                            </div>
                        </div>
                        <div class="orc-campo-group orc-campo-valor-descricao-final" style="grid-column: 2 / 3;">
                            <label><i class="bi bi-info-circle"></i> Descrição</label>
                            <input type="text" id="secaoValorDescricao" 
                                placeholder="Ex: VALOR TOTAL" 
                                oninput="window.atualizarPreviewSecao()"
                                style="font-size: 0.9rem;">
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
            container.className = html ? 'orc-campos-especificos visible' : 'orc-campos-especificos';
        };
        
        this.atualizarPreview = function() {
            var titulo = document.getElementById(self.ids.titulo).value;
            var conteudo = document.getElementById(self.ids.conteudo).value;
            var tipo = self.tipoSelecionado || 'secao';
            
            var dados = {
                tipo: tipo,
                titulo: titulo,
                conteudo: conteudo,
                colunas: document.getElementById('secaoTabelaColunas')?.value.split(',').map(function(c) { return c.trim(); }) || [],
                linhas: document.getElementById('secaoTabelaLinhas')?.value.split('\n').filter(function(l) { return l.trim(); }).map(function(l) { return l.split('|').map(function(c) { return c.trim(); }); }) || [],
                itens: document.getElementById('secaoListaItens')?.value.split('\n').filter(function(i) { return i.trim(); }) || [],
                cor: document.getElementById('secaoDestaqueCor')?.value || 'azul',
                descricao_valor: document.getElementById('secaoValorDescricao')?.value || ''
            };
            
            if (tipo === 'valor') {
                var v = document.getElementById('secaoValor');
                var c = document.getElementById('secaoValorConteudo');
                if (c) dados.conteudo = c.value;
                if (v) dados.valor = v.value || '0,00';
            }
            
            var previewContainer = self.getPreviewContainer();
            if (previewContainer && window.SecoesPreview) {
                previewContainer.innerHTML = window.SecoesPreview.previewSecao(dados);
            }
        };
        
        this.formatarValor = function(input) {
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
        
        this.configurarFormSubmit = function() {
            document.getElementById(self.formSecaoId)?.addEventListener('submit', function(e) {
                e.preventDefault();
                
                var secao = {
                    tipo: self.tipoSelecionado,
                    titulo: document.getElementById(self.ids.titulo).value,
                    conteudo: document.getElementById(self.ids.conteudo).value,
                    colunas: document.getElementById('secaoTabelaColunas')?.value.split(',').map(function(c) { return c.trim(); }) || [],
                    linhas: document.getElementById('secaoTabelaLinhas')?.value.split('\n').filter(function(l) { return l.trim(); }).map(function(l) { return l.split('|').map(function(c) { return c.trim(); }); }) || [],
                    itens: document.getElementById('secaoListaItens')?.value.split('\n').filter(function(i) { return i.trim(); }) || [],
                    cor: document.getElementById('secaoDestaqueCor')?.value || 'azul',
                    descricao: document.getElementById('secaoValorDescricao')?.value || ''
                };
                
                if (self.tipoSelecionado === 'valor') {
                    var v = document.getElementById('secaoValor');
                    if (v) secao.conteudo = v.value;
                }
                
                self.finalizarEdicao(secao);
            });
        };
    }
    
    window.criarGerenciadorSecoes = function(opcoes) {
        return new GerenciadorSecoes(opcoes);
    };
    
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
    
    // 🔥 FUNÇÃO GLOBAL QUE SERÁ SOBRESCRITA PELOS MODAIS
    window.atualizarPreviewSecao = function() {
        console.warn('atualizarPreviewSecao chamado - sobrescreva no modal');
    };

    console.log('✅ SECOES-MANAGER carregado!');

})();