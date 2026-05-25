from flask import Blueprint, redirect, render_template, url_for, request, session, flash
from rotas.middleware.autenticacao import login_required
import sqlite3, os

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_edit_transacao = Blueprint('edit_transacoes', __name__)

@bp_edit_transacao.route('/<int:sequencia>', methods=['GET', 'POST'])
@login_required
def inieditar(sequencia):
    user_id = session['user_id']

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # =========================
    # GET
    # =========================
    if request.method == 'GET':

        cursor.execute("""
            SELECT 
                t.sequencia_transacoes,   -- 0
                t.id,                     -- 1
                t.tipo,                   -- 2
                t.valor_total,            -- 3
                t.descricao,              -- 4
                t.data_emissao,           -- 5
                t.categoria_id,           -- 6
                c.nome,                   -- 7
                c.cor,                    -- 8
                t.status,                 -- 9
                t.data_vencimento         -- 10
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ?
        """, (sequencia, user_id))

        transacao = cursor.fetchone()

        # categorias pro select
        cursor.execute("""
            SELECT id, nome, cor
            FROM categorias_financas
            WHERE user_id = ?
        """, (user_id,))

        categorias = cursor.fetchall()

        conexao.close()

        if not transacao:
            flash('Transação não encontrada!', 'danger')
            return redirect(url_for('financas.inifinancas'))

        return render_template(
            'pasta_financas/crud/edit_transacao.html',
            transacao=transacao,
            categorias=categorias,
            sequencia=sequencia
        )

    # =========================
    # POST
    # =========================
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor_total') or 0)
    tipo = request.form.get('tipo')
    data_emissao = request.form.get('data_emissao')
    data_vencimento = request.form.get('data_vencimento')
    categoria_id = request.form.get('categoria_id') or None
    status = request.form.get('status')

    cursor.execute("""
        UPDATE transacoes 
        SET descricao = ?, 
            valor_total = ?, 
            tipo = ?, 
            data_emissao = ?,
            data_vencimento = ?,
            categoria_id = ?,
            status = ?
        WHERE sequencia_transacoes = ? AND user_id = ?
    """, (
        descricao, valor, tipo,
        data_emissao, data_vencimento,
        categoria_id, status,
        sequencia, user_id
    ))

    conexao.commit()
    conexao.close()

    flash('Transação atualizada com sucesso!', 'success')
    return redirect(url_for('financas.inifinancas'))