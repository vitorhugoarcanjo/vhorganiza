(function() {
    'use strict';

    if (window.__PARCELAS_PROFISSIONAL) return;
    window.__PARCELAS_PROFISSIONAL = true;

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

        // ==========================================================
        // CONSTANTES
        // ==========================================================
        const MAX_PARCELAS = 100;
        const MAX_INTERVALO = 365;
        const VALOR_MAXIMO = 10000000; // 10 milhões

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

        function calcularDataProxima(dataBase, diasIncremento) {
            const data = new Date(dataBase);
            data.setDate(data.getDate() + diasIncremento);
            return data.toISOString().split('T')[0];
        }

        function atualizarTotalizador() {
            const totalOriginal = getValorTotal();
            const somaParcelas = somarParcelas();
            const diferenca = somaParcelas - totalOriginal;
            const totalParcelas = parseInt(totalParcelasInput.value) || 1;
            
            totalOriginalSpan.innerHTML = `R$ ${formatarMoeda(totalOriginal)}`;
            somaParcelasSpan.innerHTML = `R$ ${formatarMoeda(somaParcelas)}`;
            
            // 🔥 PEGA O ELEMENTO PAI DO SOMA PARCELAS (o .total-item.soma-parcelas)
            const somaParcelasItem = document.querySelector('.total-item.soma-parcelas');
            
            if (totalParcelas > 1) {
                // Mostra Soma Parcelas
                if (somaParcelasItem) somaParcelasItem.style.display = 'flex';
                
                // Mostra Diferença
                diferencaItem.style.display = 'flex';
                
                if (Math.abs(diferenca) < 0.01) {
                    diferencaValorSpan.innerHTML = `R$ 0,00 (ok)`;
                    diferencaItem.classList.add('zerado');
                } else {
                    diferencaValorSpan.innerHTML = `R$ ${formatarMoeda(Math.abs(diferenca))} ${diferenca > 0 ? 'sobrando' : 'faltando'}`;
                    diferencaItem.classList.remove('zerado');
                }
            } else {
                // 🔥 ESCONDE SOMA PARCELAS
                if (somaParcelasItem) somaParcelasItem.style.display = 'none';
                
                // 🔥 ESCONDE DIFERENÇA
                diferencaItem.style.display = 'none';
            }
        }


        // 🔥 NOVA FUNÇÃO: Arredondar para 2 casas decimais
        function arredondar(valor) {
            return Math.round(valor * 100) / 100;
        }


        // 🔥 MODIFICAR a função distribuirIgualmente
        function distribuirIgualmente() {
            const total = parseInt(totalParcelasInput.value) || 1;
            let valorTotal = getValorTotal();
            
            if (total <= 0) return;
            
            // Calcula valor base com 2 casas
            let valorBase = arredondar(valorTotal / total);
            let soma = arredondar(valorBase * total);
            let diferenca = arredondar(valorTotal - soma);
            
            // Ajusta a última parcela para compensar arredondamento
            const valores = Array(total).fill(valorBase);
            if (Math.abs(diferenca) > 0.009) {
                valores[total - 1] = arredondar(valores[total - 1] + diferenca);
            }
            
            // Aplica os valores
            document.querySelectorAll('.parcela-input-valor').forEach((input, idx) => {
                input.value = formatarMoeda(valores[idx]);
            });
            atualizarTotalizador();
        }

        // 🔥 função gerarParcelas
        function gerarParcelas() {
            let total = parseInt(totalParcelasInput.value) || 1;
            if (total > MAX_PARCELAS) total = MAX_PARCELAS;
            if (total < 1) total = 1;
            
            const intervalo = parseInt(intervaloDias.value) || 30;
            const dataPrimeira = getDataBase();
            let valorTotal = getValorTotal();
            
            // Calcula valor por parcela com arredondamento correto
            let valorBase = arredondar(valorTotal / total);
            let soma = arredondar(valorBase * total);
            let diferenca = arredondar(valorTotal - soma);
            
            const valores = Array(total).fill(valorBase);
            if (Math.abs(diferenca) > 0.009) {
                valores[total - 1] = arredondar(valores[total - 1] + diferenca);
            }
            
            renderizarParcelas(total, intervalo, dataPrimeira, valores);
        }


        // 🔥 MODIFICAR a função renderizarParcelas (recebe array de valores agora)
        function renderizarParcelas(total, intervalo, dataPrimeira, valoresParcela) {
            parcelasBody.innerHTML = '';
            
            for (let i = 1; i <= total; i++) {
                const dataVencimento = i === 1 ? dataPrimeira : calcularDataProxima(dataPrimeira, (i - 1) * intervalo);
                const valorParcela = valoresParcela[i - 1];
                
                const row = document.createElement('tr');
                const isFirstParcela = (i === 1);
                
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
                            value="${formatarMoeda(valorParcela)}" 
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
                parcelasBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--texto-mutado);">Selecione mais de 1 parcela</td></tr>';
                atualizarTotalizador();
            }
        }

        // Eventos
        totalParcelasInput.addEventListener('input', function() {
            let valor = parseInt(this.value) || 1;
            if (valor > MAX_PARCELAS) {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '';
            }
            toggleParcelas();
        });
        
        totalParcelasInput.addEventListener('blur', function() {
            let valor = parseInt(this.value) || 1;
            if (valor > MAX_PARCELAS) {
                if (typeof Notificacao !== 'undefined') Notificacao.aviso(`Máximo de ${MAX_PARCELAS} parcelas permitidas!`);
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
                if (typeof Notificacao !== 'undefined') Notificacao.aviso(`Máximo de ${MAX_INTERVALO} dias entre parcelas!`);
            }
            if (valor < 1) intervaloDias.value = 1;
            if (parseInt(totalParcelasInput.value) > 1) gerarParcelas();
        });
        
        primeiroVencimento.addEventListener('change', () => {
            if (parseInt(totalParcelasInput.value) > 1) gerarParcelas();
        });
        
        btnDistribuir.addEventListener('click', distribuirIgualmente);
        
        valorTotalInput.addEventListener('input', function() {
            const valor = getValorTotal();
            if (valor > VALOR_MAXIMO) {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '';
            }
            if (parseInt(totalParcelasInput.value) > 1) distribuirIgualmente();
            atualizarTotalizador();
        });
        
        // Tipo de transação
        const tipoBtns = document.querySelectorAll('.tipo-btn');
        const tipoHidden = document.getElementById('tipoHidden');
        
        tipoBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                tipoBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                tipoHidden.value = this.dataset.tipo;
            });
        });
        
        // Validação no envio
        const form = document.getElementById('form-transacao');

        if (form) {
            form.addEventListener('submit', function(e) {
                const totalOriginal = getValorTotal();
                const totalParcelas = parseInt(totalParcelasInput.value) || 1;
                let somaParcelas = 0;
                let erro = false;
                let mensagemErro = '';
                
                // Valida valor máximo
                if (totalOriginal > VALOR_MAXIMO) {
                    erro = true;
                    mensagemErro = `Valor máximo permitido é R$ ${formatarMoeda(VALOR_MAXIMO)}!`;
                }
                
                // Valida soma das parcelas
                if (totalParcelas > 1 && !erro) {
                    somaParcelas = somarParcelas();
                    
                    if (Math.abs(somaParcelas - totalOriginal) >= 0.01) {
                        erro = true;
                        mensagemErro = 'A soma das parcelas não confere com o valor total!';
                    }
                }
                
                // Valida tipo
                const tipo = tipoHidden.value;
                if (!tipo || tipo === 'vazio') {
                    erro = true;
                    mensagemErro = 'Selecione o tipo da transação (Receita ou Despesa)!';
                }
                
                if (erro) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    if (typeof Notificacao !== 'undefined') {
                        Notificacao.erro(mensagemErro);
                    } else {
                        alert(mensagemErro);
                    }
                    return false;
                }
                
                return true;
            });
        }
        
        // Inicialização
        toggleParcelas();
        atualizarTotalizador();
    });
})();