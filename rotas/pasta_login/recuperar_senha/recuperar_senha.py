from flask import Blueprint, request, redirect, render_template, url_for, flash, session
import os
import sqlite3
from datetime import datetime

from rotas.pasta_login.pasta_cadastre_se.autenticador_email.email_utils import (
    gerar_codigo,
    enviar_email_recuperacao,
    salvar_codigo_recuperacao,
    verificar_codigo_recuperacao
)
from rotas.pasta_login.pasta_cadastre_se.validacoes.criptografia_snh import criptografar_senha

bp_recuperar = Blueprint('recuperar', __name__)
caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')


@bp_recuperar.route('/', methods=['GET', 'POST'])
def solicitar_recuperacao():
    """ Tela para solicitar recuperação de senha """
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Verifica se o email existe
        with sqlite3.connect(caminho_banco) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cadastre_se WHERE email = ?", (email,))
            usuario = cursor.fetchone()
            
            if not usuario:
                flash('Email não cadastrado!', 'danger')
                return redirect(url_for('recuperar.solicitar_recuperacao'))
        
        # Gera e envia código
        codigo = gerar_codigo()
        sucesso, mensagem = enviar_email_recuperacao(email, codigo)
        
        if sucesso:
            salvar_codigo_recuperacao(email, codigo)
            flash('Código enviado para seu email!', 'success')
            return redirect(url_for('recuperar.validar_codigo', email=email))
        else:
            flash(mensagem, 'danger')
            return redirect(url_for('recuperar.solicitar_recuperacao'))
    
    return render_template('pasta_login/recuperar_senha/solicitar.html')


@bp_recuperar.route('/validar/<email>', methods=['GET', 'POST'])
def validar_codigo(email):
    """ Tela para validar o código de recuperação """
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        
        sucesso, mensagem, user_id = verificar_codigo_recuperacao(email, codigo)
        
        if sucesso:
            session['reset_user_id'] = user_id
            session['reset_email'] = email
            flash(mensagem, 'success')
            return redirect(url_for('recuperar.nova_senha'))
        else:
            flash(mensagem, 'danger')
            return redirect(url_for('recuperar.validar_codigo', email=email))
    
    return render_template('pasta_login/recuperar_senha/validar_codigo.html', email=email)


@bp_recuperar.route('/nova-senha', methods=['GET', 'POST'])
def nova_senha():
    """ Tela para definir nova senha """
    # Verifica se a sessão tem os dados de recuperação
    if 'reset_user_id' not in session:
        flash('Acesso inválido. Solicite novamente a recuperação.', 'danger')
        return redirect(url_for('recuperar.solicitar_recuperacao'))
    
    if request.method == 'POST':
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações
        if not senha or not confirmar_senha:
            flash('Preencha todos os campos!', 'warning')
            return redirect(url_for('recuperar.nova_senha'))
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('recuperar.nova_senha'))
        
        if len(senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres!', 'warning')
            return redirect(url_for('recuperar.nova_senha'))
        
        # Criptografa e salva a nova senha
        senha_criptografada = criptografar_senha(senha)
        
        with sqlite3.connect(caminho_banco) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cadastre_se 
                SET senha = ? 
                WHERE id = ?
            """, (senha_criptografada, session['reset_user_id']))
            conn.commit()
        
        # Limpa a sessão
        session.pop('reset_user_id', None)
        session.pop('reset_email', None)
        
        flash('Senha alterada com sucesso! Faça login.', 'success')
        return redirect(url_for('login.validar_login'))
    
    return render_template('pasta_login/recuperar_senha/nova_senha.html')