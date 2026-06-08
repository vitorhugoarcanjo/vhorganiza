from flask import Blueprint, request, redirect, render_template, url_for, flash
from utils.database.conexao_global import ini_conexao
from .autenticador_email.email_utils import gerar_codigo, enviar_email_confirmacao, salvar_codigo_verificacao, verificar_codigo

from .validacoes.criptografia_snh import criptografar_senha
from .validacoes.validar_usuario import (
    validar_email_formato,
    validar_email_unico,
    validar_senha_tamanho,
    validar_campos_obrigatorios,
    validar_confirmacao_senha,
    validar_e_limpar_telefone
)

bp_cadastre_se = Blueprint('cadastre_se', __name__)

@bp_cadastre_se.route('/', methods=['GET', 'POST'])
def tela_cadastre_se():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')


        # VALIDA TELEFONE
        telefone_limpo = validar_e_limpar_telefone(telefone)
        if not telefone_limpo:
            flash('Telefone inválido!', 'danger')
            return redirect(url_for('cadastre_se.tela_cadastre_se'))


        # SENHA CRIPTOGRAFADA
        senha_criptografada = criptografar_senha(senha)

        conexao, cursor = ini_conexao()

        if not all([
            validar_campos_obrigatorios(nome, telefone, email, senha, confirmar_senha),
            validar_confirmacao_senha(senha, confirmar_senha),
            validar_email_formato(email),
            validar_senha_tamanho(senha),
            validar_email_unico(conexao, email)
        ]):
            return redirect(url_for('cadastre_se.tela_cadastre_se'))


        # SE PASSOU NAS VALIDAÇÕES: FAZ INSERT
        try:
            cursor.execute('INSERT INTO cadastre_se (nome, telefone, email, senha) VALUES (%s, %s, %s, %s) RETURNING id', 
                        (nome, telefone_limpo, email, senha_criptografada))
            user_id = cursor.fetchone()[0]  # ← CORRIGIDO!
            conexao.commit()
            
            # GERA CÓDIGO E ENVIA EMAIL
            codigo = gerar_codigo()
            sucesso, mensagem = enviar_email_confirmacao(email, codigo)
            
            if sucesso:
                # SALVA CÓDIGO NO BANCO
                salvar_codigo_verificacao(user_id, codigo)
                flash('Cadastro realizado! Verifique seu email para confirmar.', 'success')
                return redirect(url_for('cadastre_se.confirmar_email', user_id=user_id))
            else:
                # SE ERRO NO EMAIL, APAGA O USUÁRIO
                cursor.execute('DELETE FROM cadastre_se WHERE id = %s', (user_id,))
                conexao.commit()
                flash(f'Erro ao enviar email: {mensagem}', 'danger')
                return redirect(url_for('cadastre_se.tela_cadastre_se'))

        except Exception as e:
            flash('Erro ao cadastrar: ' + str(e), 'danger')
            return redirect(url_for('cadastre_se.tela_cadastre_se'))
        
    return render_template('pasta_login/pasta_cadastre_se/tela_cadastre_se.html')


@bp_cadastre_se.route('/confirmar-email/<int:user_id>')
def confirmar_email(user_id):
    """ Tela para digitar o código de confirmação """
    return render_template('pasta_login/pasta_cadastre_se/confirmar_email.html.jinja', user_id=user_id)


@bp_cadastre_se.route('/validar-codigo', methods=['POST'])
def validar_codigo():
    """ Valida o código digitado pelo usuário """
    user_id = request.form.get('user_id')
    codigo = request.form.get('codigo')
    
    sucesso, mensagem = verificar_codigo(user_id, codigo)
    
    if sucesso:
        flash(mensagem, 'success')
        return redirect(url_for('login.validar_login'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('cadastre_se.confirmar_email', user_id=user_id))


@bp_cadastre_se.route('/reenviar-codigo/<int:user_id>')
def reenviar_codigo(user_id):
    """ Reenvia o código de confirmação """
    conexao, cursor = ini_conexao()
    cursor.execute("SELECT email FROM cadastre_se WHERE id = %s", (user_id,))
    resultado = cursor.fetchone()
    
    if not resultado:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('cadastre_se.tela_cadastre_se'))
    
    email = resultado[0]
    
    codigo = gerar_codigo()
    sucesso, mensagem = enviar_email_confirmacao(email, codigo)
    
    if sucesso:
        salvar_codigo_verificacao(user_id, codigo)
        flash('Novo código enviado com sucesso!', 'success')
    else:
        flash(mensagem, 'danger')
    
    return redirect(url_for('cadastre_se.confirmar_email', user_id=user_id))