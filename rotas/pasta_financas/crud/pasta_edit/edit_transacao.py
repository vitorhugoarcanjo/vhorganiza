from flask import Blueprint, redirect, render_template, url_for, request, session, flash
from rotas.middleware.autenticacao import login_required
import sqlite3, os

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_edit_transacao = Blueprint('edit_transacoes', __name__)


@bp_edit_transacao.route('/<int:sequencia>', methods=['GET', 'POST'])
@login_required
def inieditar(sequencia):
    user_id = session['user_id']
    
    if request.method == 'GET':
        conexao_banco = sqlite3.connect(caminho_banco)
        cursor = conexao_banco.cursor()

        # Busca pela sequência e user_id
        cursor.execute('''
            SELECT sequencia_transacoes, id, tipo, valor_total, descricao, data_emissao, 
                   categoria, status, data_vencimento
            FROM transacoes 
            WHERE sequencia_transacoes = ? AND user_id = ?
        ''', (sequencia, user_id))
        transacao = cursor.fetchone()
        conexao_banco.close()

        if not transacao:
            flash('Transação não encontrada!', 'danger')
            return redirect(url_for('financas.inifinancas'))

        return render_template('pasta_financas/crud/edit_transacao.html', 
                               transacao=transacao, 
                               sequencia=sequencia)
    
    if request.method == 'POST':
        # Pega os dados do formulário
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor_total'))
        tipo = request.form.get('tipo')
        data_emissao = request.form.get('data_emissao')
        data_vencimento = request.form.get('data_vencimento')
        categoria = request.form.get('categoria')
        status = request.form.get('status')

        conexao_banco = sqlite3.connect(caminho_banco)
        cursor = conexao_banco.cursor()

        # Atualiza pela sequência
        cursor.execute('''
            UPDATE transacoes 
            SET descricao = ?, 
                valor_total = ?, 
                tipo = ?, 
                data_emissao = ?,
                data_vencimento = ?,
                categoria = ?,
                status = ?
            WHERE sequencia_transacoes = ? AND user_id = ?
        ''', (descricao, valor, tipo, data_emissao, data_vencimento, categoria, status, sequencia, user_id))

        conexao_banco.commit()
        conexao_banco.close()

        flash('Transação atualizada com sucesso!', 'success')
        return redirect(url_for('financas.inifinancas'))