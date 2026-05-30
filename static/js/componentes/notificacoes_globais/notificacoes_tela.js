if (window.Notificacao) {
    console.warn("Notificacao já existe - evitando duplicação");
} else {

    window.Notificacao = {
        
        _container: null,
        
        _criarContainer() {
            if (this._container) return this._container;
            
            this._container = document.createElement('div');
            this._container.className = 'notificacao-container';
            document.body.appendChild(this._container);
            
            return this._container;
        },
        
        _criarItem(mensagem, tipo) {
            const icones = {
                sucesso: '✅',
                erro: '❌',
                aviso: '⚠️'
            };
            
            const item = document.createElement('div');
            item.className = `notificacao-item ${tipo}`;
            item.innerHTML = `
                <span class="notificacao-icone">${icones[tipo]}</span>
                <span class="notificacao-mensagem">${mensagem}</span>
                <button class="notificacao-fechar" onclick="this.parentElement.remove()">✕</button>
            `;
            
            return item;
        },
        
        _mostrar(mensagem, tipo, duracao = 3000) {
            const container = this._criarContainer();
            const item = this._criarItem(mensagem, tipo);
            
            container.appendChild(item);
            
            if (duracao > 0) {
                setTimeout(() => {
                    item.classList.add('saindo');
                    setTimeout(() => item.remove(), 300);
                }, duracao);
            }
            
            return item;
        },
        
        sucesso(mensagem, duracao = 3000) {
            return this._mostrar(mensagem, 'sucesso', duracao);
        },
        
        erro(mensagem, duracao = 5000) {
            return this._mostrar(mensagem, 'erro', duracao);
        },
        
        aviso(mensagem, duracao = 4000) {
            return this._mostrar(mensagem, 'aviso', duracao);
        }
    };

}