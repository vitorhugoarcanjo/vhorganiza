(function() {
    'use strict';

    if (window.__PARCELAS_EDIT_RODANDO) return;
    window.__PARCELAS_EDIT_RODANDO = true;

    document.addEventListener('DOMContentLoaded', function() {
        const totalParcelasInput = document.getElementById('totalParcelas');
        const parcelasConfigArea = document.getElementById('parcelasConfigArea');
        const parcelasWrapper = document.getElementById('parcelasWrapper');
        const intervaloDias = document.getElementById('intervaloDias');
        const primeiroVencimento = document.getElementById('primeiroVencimento');
        const btnDistribuir = document.getElementById('btnDistribuir');
        const valorTotalInput = document.getElementById('valor_total');
        const dataVencimentoGroup = document.getElementById('dataVencimentoGroup');
        const dataEmissao = document.querySelector('input[name="data_emissao"]');
        const parcelasBody = document.getElementById('parcelasBody');
        
        const totalOriginalSpan = document.getElementById('totalOriginal');
        const somaParcelasSpan = document.getElementById('somaParcelas');
        const diferencaValorSpan = document.getElementById('diferencaValor');
        const diferencaItem = document.getElementById('diferencaItem');

        const MAX_PARCELAS = 100;
        const MAX_INTERVALO = 365;

        // ==========================================================
        // CARREGA PARCELAS EXISTENTES DO CAMPO OCULTO
        // ==========================================================
        let parcelasExistentes = [];
        const parcelasFilhasData = document.getElementById('parcelasFilhasData');
        
        if (parcelasFilhasData && parcelasFilhasData.value && parcelasFilhasData.value !== '[]') {
            try {
                parcelasExistentes = JSON.parse(parcelasFilhasData.value);
                console.log('✅ Parcelas carregadas:', parcelasExistentes.length);
                
                if (parcelasExistentes.length > 0) {
                    console.log('📦 Primeira parcela:', parcelasExistentes[0]);
                }
            } catch(e) {
                console.error('❌ Erro ao carregar parcelas:', e);
            }
        }




        // ==========================================================
        // FUNÇÃO PARA CONVERTER DATA BRASILEIRA PARA ISO
        // Entrada: "29/05/2026" → Saída: "2026-05-29"
        // ==========================================================
        function converterDataParaISO(dataStr) {
            if (!dataStr) return '';
            // Se já estiver no formato ISO (YYYY-MM-DD), retorna
            if (dataStr.match(/^\d{4}-\d{2}-\d{2}$/)) return dataStr;
            // Converte de DD/MM/YYYY para YYYY-MM-DD
            const partes = dataStr.split('/');
            if (partes.length === 3) {
                return `${partes[2]}-${partes[1]}-${partes[0]}`;
            }
            return dataStr;
        }

        function formatarMoeda(valor) {
            return valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function parseMoeda(valorStr) {
            if (!valorStr) return 0;
            let limpo = valorStr.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
            return parseFloat(limpo) || 0;
        }

        function getValorTotal() {
            return parseMoeda(valorTotalInput.value);
        }

        function getDataBase() {
            return primeiroVencimento.value || dataEmissao.value || new Date().toISOString().split('T')[0];
        }

        function somarParcelas() {
            let soma = 0;
            document.querySelectorAll('.parcela-input-valor').forEach(input => {
                soma += parseMoeda(input.value);
            });
            return soma;
        }

        // ==========================================================
        // INICIALIZAÇÃO - CARREGA PARCELAS EXISTENTES PRIMEIRO
        // ==========================================================
        // Carrega parcelas existentes ANTES de toggleParcelas
        if (parcelasExistentes.length > 0) {
            carregarParcelasExistentesNaEdicao();
        } else {
            toggleParcelas();
        }
        atualizarTotalizador();

        function calcularDataProxima(dataBase, diasIncremento) {
            const data = new Date(dataBase);
            data.setDate(data.getDate() + diasIncremento);
            return data.toISOString().split('T')[0];
        }

        function atualizarTotalizador() {
            const totalOriginal = getValorTotal();
            const somaParcelas = somarParcelas();
            const diferenca = somaParcelas - totalOriginal;
            
            totalOriginalSpan.innerHTML = `R$ ${formatarMoeda(totalOriginal)}`;
            somaParcelasSpan.innerHTML = `R$ ${formatarMoeda(somaParcelas)}`;
            
            if (Math.abs(diferenca) < 0.01) {
                diferencaValorSpan.innerHTML = `R$ 0,00 (ok)`;
                diferencaItem.classList.add('zerado');
            } else {
                diferencaValorSpan.innerHTML = `R$ ${formatarMoeda(Math.abs(diferenca))} ${diferenca > 0 ? 'sobrando' : 'faltando'}`;
                diferencaItem.classList.remove('zerado');
            }
        }

        function renderizarParcelas(total, intervalo, dataPrimeira, valoresParcela, forcarDadosExistentes = false) {
            parcelasBody.innerHTML = '';
            
            for (let i = 1; i <= total; i++) {
                let dataVencimento;
                let valorParcelaItem;
                
                // 🔥 PRIORIZA OS DADOS EXISTENTES se disponíveis
                if (!forcarDadosExistentes && parcelasExistentes.length > 0 && i <= parcelasExistentes.length) {
                    const p = parcelasExistentes[i-1];
                    // p é um OBJETO ou ARRAY? No seu caso é um objeto
                    // Se for objeto: p.data_vencimento, p.valor
                    // Se for array: p[2] = data, p[3] = valor
                    let dataOriginal = p.data_vencimento || p[2];
                    let valorRaw = p.valor || p[3];
                    
                    // Converte data
                    dataVencimento = converterDataParaISO(dataOriginal);
                    
                    // Converte valor
                    if (typeof valorRaw === 'string') {
                        valorRaw = parseMoeda(valorRaw);
                    }
                    valorParcelaItem = valorRaw;
                } else if (valoresParcela && valoresParcela.length > 0 && i <= valoresParcela.length) {
                    // Usa valores passados (distribuição)
                    dataVencimento = i === 1 ? dataPrimeira : calcularDataProxima(dataPrimeira, (i-1) * intervalo);
                    valorParcelaItem = valoresParcela[i-1];
                } else {
                    // Calcula novo
                    dataVencimento = i === 1 ? dataPrimeira : calcularDataProxima(dataPrimeira, (i-1) * intervalo);
                    valorParcelaItem = getValorTotal() / total;
                }
                
                const isFirstParcela = (i === 1);
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="parcela-numero">${i}/${total}</td>
                    <td>
                        <input type="date" class="parcela-input-data" 
                            value="${dataVencimento}" 
                            data-parcela="${i}"
                            ${isFirstParcela ? 'readonly style="background: var(--hover-fino); cursor: not-allowed;"' : ''}>
                    </td>
                    <td>
                        <input type="text" class="parcela-input-valor money-input" 
                            value="${formatarMoeda(parseFloat(valorParcelaItem))}" 
                            data-parcela="${i}">
                    </td>
                `;
                parcelasBody.appendChild(row);
            }
            
            document.querySelectorAll('.parcela-input-data:not([readonly])').forEach(input => {
                input.addEventListener('change', () => atualizarTotalizador());
            });
            
            document.querySelectorAll('.parcela-input-valor').forEach(input => {
                input.addEventListener('input', () => atualizarTotalizador());
                if (typeof window.formatarInputMoeda === 'function') {
                    window.formatarInputMoeda(input);
                }
            });
            
            atualizarTotalizador();
        }



        function gerarParcelas() {
            let total = parseInt(totalParcelasInput.value) || 1;
            if (total > MAX_PARCELAS) total = MAX_PARCELAS;
            if (total < 1) total = 1;
            
            const intervalo = parseInt(intervaloDias.value) || 30;
            const dataPrimeira = getDataBase();
            const valorTotal = getValorTotal();
            const valorParcela = total > 0 ? valorTotal / total : 0;
            
            // 🔥 SE JÁ EXISTEM PARCELAS, PASSA OS VALORES EXISTENTES
            if (parcelasExistentes.length > 0 && total === parcelasExistentes.length) {
                // Extrai os valores das parcelas existentes
                const valoresExistentes = parcelasExistentes.map(p => p.valor || p[3]);
                renderizarParcelas(total, intervalo, dataPrimeira, valoresExistentes, true);
            } else {
                renderizarParcelas(total, intervalo, dataPrimeira, null, false);
            }
        }


        // 🔥 FUNÇÃO ESPECÍFICA PARA CARREGAR PARCELAS NA EDIÇÃO
        function carregarParcelasExistentesNaEdicao() {
            if (parcelasExistentes.length === 0) return;
            
            const total = parcelasExistentes.length;
            const intervalo = 30; // pode vir do backend
            const dataPrimeira = converterDataParaISO(parcelasExistentes[0].data_vencimento || parcelasExistentes[0][2]);
            const valoresExistentes = parcelasExistentes.map(p => p.valor || p[3]);
            
            // Atualiza o campo Nº Parcelas
            totalParcelasInput.value = total;
            
            // Atualiza configurações
            intervaloDias.value = intervalo;
            primeiroVencimento.value = dataPrimeira;
            
            // Mostra as áreas
            dataVencimentoGroup.style.display = 'none';
            parcelasConfigArea.style.display = 'block';
            parcelasWrapper.style.display = 'block';
            
            // Renderiza com os dados existentes
            renderizarParcelas(total, intervalo, dataPrimeira, valoresExistentes, true);
        }

        function distribuirIgualmente() {
            const total = parseInt(totalParcelasInput.value) || 1;
            const valorTotal = getValorTotal();
            const valorParcela = total > 0 ? valorTotal / total : 0;
            
            document.querySelectorAll('.parcela-input-valor').forEach(input => {
                input.value = formatarMoeda(valorParcela);
            });
            atualizarTotalizador();
        }

        function toggleParcelas() {
            let total = parseInt(totalParcelasInput.value) || 1;
            
            if (total > MAX_PARCELAS) total = MAX_PARCELAS;
            if (total < 1) total = 1;
            
            if (total > 1) {
                dataVencimentoGroup.style.display = 'none';
                parcelasConfigArea.style.display = 'block';
                parcelasWrapper.style.display = 'block';
                gerarParcelas();
            } else {
                dataVencimentoGroup.style.display = 'block';
                parcelasConfigArea.style.display = 'none';
                parcelasWrapper.style.display = 'none';
                parcelasBody.innerHTML = '</table><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
                atualizarTotalizador();
            }
        }

        // ==========================================================
        // EVENTOS
        // ==========================================================
        totalParcelasInput.addEventListener('input', function() {
            let valor = parseInt(this.value) || 1;
            this.style.borderColor = valor > MAX_PARCELAS ? '#ef4444' : '';
            toggleParcelas();
        });
        
        totalParcelasInput.addEventListener('blur', function() {
            let valor = parseInt(this.value) || 1;
            if (valor > MAX_PARCELAS) {
                if (window.Notificacao) Notificacao.aviso(`Máximo de ${MAX_PARCELAS} parcelas permitidas!`);
                this.value = MAX_PARCELAS;
                toggleParcelas();
            } else if (valor < 1) {
                this.value = 1;
                toggleParcelas();
            }
            this.style.borderColor = '';
        });
        
        intervaloDias.addEventListener('input', () => {
            let valor = parseInt(intervaloDias.value) || 30;
            if (valor > MAX_INTERVALO) {
                intervaloDias.value = MAX_INTERVALO;
                if (window.Notificacao) Notificacao.aviso(`Máximo de ${MAX_INTERVALO} dias entre parcelas!`);
            }
            if (valor < 1) intervaloDias.value = 1;
            if (parseInt(totalParcelasInput.value) > 1) gerarParcelas();
        });
        
        primeiroVencimento.addEventListener('change', () => {
            if (parseInt(totalParcelasInput.value) > 1) gerarParcelas();
        });
        
        btnDistribuir.addEventListener('click', distribuirIgualmente);
        
        valorTotalInput.addEventListener('input', () => {
            if (parseInt(totalParcelasInput.value) > 1) distribuirIgualmente();
            atualizarTotalizador();
        });
        
        // ==========================================================
        // TIPO DE TRANSAÇÃO
        // ==========================================================
        const tipoBtns = document.querySelectorAll('.tipo-btn');
        const tipoHidden = document.getElementById('tipoHidden');
        const tipoAtual = tipoHidden.value;
        
        tipoBtns.forEach(btn => {
            const btnTipo = btn.dataset.tipo;
            if (btnTipo === tipoAtual) {
                btn.classList.add('active');
                if (btnTipo === 'receita') btn.style.borderColor = '#22c55e';
                if (btnTipo === 'despesa') btn.style.borderColor = '#ef4444';
            }
            
            btn.addEventListener('click', function() {
                tipoBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                tipoHidden.value = this.dataset.tipo;
            });
        });
        
        // ==========================================================
        // VALIDAÇÃO NO ENVIO
        // ==========================================================
        const form = document.getElementById('form-edit-transacao');
        
        if (form) {
            form.addEventListener('submit', function(e) {
                const totalOriginal = getValorTotal();
                const totalParcelas = parseInt(totalParcelasInput.value) || 1;
                let somaParcelas = 0;
                
                if (totalParcelas > 1) {
                    somaParcelas = somarParcelas();
                    
                    if (Math.abs(somaParcelas - totalOriginal) >= 0.01) {
                        e.preventDefault();
                        const msg = 'A soma das parcelas não confere com o valor total!';
                        if (window.Notificacao) Notificacao.erro(msg);
                        else alert(msg);
                        return false;
                    }
                }
                
                const tipo = tipoHidden.value;
                if (!tipo || tipo === 'vazio') {
                    e.preventDefault();
                    const msg = 'Selecione o tipo da transação (Receita ou Despesa)!';
                    if (window.Notificacao) Notificacao.erro(msg);
                    else alert(msg);
                    return false;
                }
                
                return true;
            });
        }
    });
})();