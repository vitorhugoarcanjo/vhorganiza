from flask import Blueprint, redirect, url_for, session, flash
import sqlite3
import os
from datetime import date

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_quitar = Blueprint('quitar_transacao', __name__)

@bp_quitar.route('/<int:sequencia>')
def iniquitacao(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes 
            SET status = 'quitado', 
                data_quitamento = ? 
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (hoje, sequencia, user_id))
        conn.commit()
    
    flash('Despesa quitada com sucesso!', 'success')
    return redirect(url_for('financas.inifinancas'))