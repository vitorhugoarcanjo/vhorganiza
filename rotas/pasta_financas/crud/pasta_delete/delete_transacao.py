from flask import Blueprint, redirect, url_for, session, flash
from rotas.middleware.autenticacao import login_required
import sqlite3, os

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_delete = Blueprint('deletar_transacao', __name__)


@bp_delete.route('/<int:sequencia>')
@login_required
def inideletar(sequencia):
    user_id = session['user_id']
    
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE sequencia_transacoes = ? AND user_id = ?", (sequencia, user_id))
        conn.commit()
    
    flash('Transação excluída com sucesso!', 'success')
    return redirect(url_for('financas.inifinancas'))