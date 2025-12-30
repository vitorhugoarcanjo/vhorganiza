from flask import Blueprint, render_template, redirect, request, flash, url_for, session
import os, sqlite3


# VALIDAÇÃO DE LOGIN
from rotas.pasta_login.pasta_acesso_login.validacoes.validar_usuario import validar_usuario_bd

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_login = Blueprint('login', __name__)



@bp_login.route('/', methods=['GET', 'POST'])
def validar_login():
    if request.method == 'POST':
        nome_ou_email = request.form.get('nome_ou_email')
        senha = request.form.get('senha')

        # VALIDAÇÃO 1
        if not nome_ou_email or not senha:
            flash('Preencha todos os campos!', 'warning')
            return redirect(url_for('login.validar_login'))



        resultado = validar_usuario_bd(caminho_banco, nome_ou_email, senha)

        # SE O CADASTRO FOR ENCONTRADO, VAI PARA A PRÓXIMA PÁGINA
        if resultado:
            
            # BUSCAR ID E NOME DO USUÁRIO
            conexao_banco = sqlite3.connect(caminho_banco)
            cursor = conexao_banco.cursor()
            cursor.execute('SELECT id, nome FROM cadastre_se WHERE (nome = ? OR email = ?)', (nome_ou_email, nome_ou_email))
            usuario = cursor.fetchone()
            conexao_banco.close()

            # SETAR NA SESSÃO
            session.permanent = True
            session['user_id'] = usuario[0] # ID do usuário
            session['user_nome'] = usuario[1] # Nome do usuário

            flash('Logado com sucesso!', 'success')
            return redirect(url_for('pos_login.iniposlogin'))

        else:
            flash('Usuário ou senha incorretos!', 'error')
            return redirect(url_for('login.validar_login'))


    return render_template('pasta_login/pasta_acesso_login/tela_logica_login.html')
