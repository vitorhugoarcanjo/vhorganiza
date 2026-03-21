from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from rotas.middleware.autenticacao import login_required

import os, sqlite3
from datetime import date

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_insert_transacao = Blueprint('nova_transacao', __name__)

def get_proxima_sequencia(cursor, user_id):
    """ Retorna a próxima sequência para o usuário """
    cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]

@bp_insert_transacao.route('/', methods=['GET', 'POST'])
@login_required
def initransacao():
    hoje = date.today().isoformat()
    
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            tipo = request.form.get('tipo')
            valor_total = float(request.form.get('valor_total'))
            descricao = request.form.get('descricao')
            data_emissao = request.form.get('data_emissao', hoje)
            data_vencimento = request.form.get('data_vencimento', hoje)
            
            # Trata parcelas
            parcelas_str = request.form.get('total_parcelas', '1')
            if not parcelas_str or parcelas_str == '':
                total_parcelas = 1
            else:
                total_parcelas = int(parcelas_str)
                if total_parcelas < 1:
                    total_parcelas = 1
                if total_parcelas > 60:
                    total_parcelas = 60
            
            status = 'recebido' if tipo == 'receita' else 'aberto'

            conexao = sqlite3.connect(caminho_banco)
            cursor = conexao.cursor()
            
            sequencia = get_proxima_sequencia(cursor, user_id)
            
            cursor.execute('''
                INSERT INTO transacoes (user_id, sequencia_transacoes, tipo, valor_total, descricao, data_emissao, data_vencimento, total_parcelas, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, sequencia, tipo, valor_total, descricao, data_emissao, data_vencimento, total_parcelas, status))
            
            conexao.commit()
            conexao.close()

            flash('Transação cadastrada com sucesso!', 'success')
            return redirect(url_for('financas.inifinancas'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return redirect(url_for('nova_transacao.initransacao'))
        
    return render_template('pasta_financas/crud/insert_transacao.html', hoje=hoje)