# email_utils.py
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import sqlite3
import os

from rotas.pasta_login.pasta_cadastre_se.autenticador_email.config_email import EmailConfig

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

def gerar_codigo():
    """ Gera código de 6 dígitos aleatório """
    return ''.join(random.choices(string.digits, k=EmailConfig.CODIGO_TAMANHO))

def enviar_email_confirmacao(email_destino, codigo):
    """ Envia email com código de confirmação """
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Confirme seu cadastro - Gestão Financeira'
        msg['From'] = EmailConfig.MAIL_DEFAULT_SENDER
        msg['To'] = email_destino
        
        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Bem-vindo à Gestão Financeira!</h2>
            <p>Para confirmar seu cadastro, utilize o código abaixo:</p>
            <div style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px;">
                {codigo}
            </div>
            <p>Este código expira em {EmailConfig.CODIGO_EXPIRACAO_MINUTOS} minutos.</p>
            <p>Se não foi você quem solicitou, ignore este email.</p>
            <hr>
            <small>Gestão Financeira - Organize suas finanças</small>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo, 'html'))
        
        with smtplib.SMTP(EmailConfig.MAIL_SERVER, EmailConfig.MAIL_PORT) as server:
            server.starttls()
            server.login(EmailConfig.MAIL_USERNAME, EmailConfig.MAIL_PASSWORD)
            server.send_message(msg)
        
        return True, "Email enviado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao enviar email: {str(e)}"

def salvar_codigo_verificacao(user_id, codigo):
    """ Salva o código de verificação no banco """
    expiracao = datetime.now() + timedelta(minutes=EmailConfig.CODIGO_EXPIRACAO_MINUTOS)
    
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE cadastre_se   -- <-- MUDOU: cadastre_se, não usuarios
            SET codigo_verificacao = ?, 
                codigo_expiracao = ?,
                tentativas_verificacao = 0
            WHERE id = ?
        """, (codigo, expiracao, user_id))
        conexao.commit()

def verificar_codigo(user_id, codigo_digitado):
    """ Verifica se o código está correto e não expirou """
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT codigo_verificacao, codigo_expiracao, tentativas_verificacao
            FROM cadastre_se   -- <-- MUDOU: cadastre_se, não usuarios
            WHERE id = ?
        """, (user_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return False, "Usuário não encontrado"
        
        codigo_salvo, expiracao_str, tentativas = resultado
        expiracao = datetime.strptime(expiracao_str, '%Y-%m-%d %H:%M:%S.%f') if expiracao_str else None
        
        # Verifica tentativas
        if tentativas >= EmailConfig.MAX_TENTATIVAS:
            return False, "Muitas tentativas. Solicite um novo código."
        
        # Verifica expiração
        if expiracao and datetime.now() > expiracao:
            return False, "Código expirado. Solicite um novo."
        
        # Verifica código
        if codigo_salvo != codigo_digitado:
            # Incrementa tentativas
            cursor.execute("UPDATE cadastre_se SET tentativas_verificacao = tentativas_verificacao + 1 WHERE id = ?", (user_id,))
            conexao.commit()
            return False, f"Código inválido. Você tem mais {EmailConfig.MAX_TENTATIVAS - tentativas - 1} tentativas."
        
        # Código correto: ativa a conta
        cursor.execute("""
            UPDATE cadastre_se   -- <-- MUDOU: cadastre_se, não usuarios
            SET email_verificado = 1, 
                codigo_verificacao = NULL, 
                codigo_expiracao = NULL,
                tentativas_verificacao = 0
            WHERE id = ?
        """, (user_id,))
        conexao.commit()
        
        return True, "Email verificado com sucesso!"
    

    
# ==================== FUNÇÕES DE RECUPERAÇÃO DE SENHA ====================

def enviar_email_recuperacao(email_destino, codigo):
    """ Envia email com código de recuperação de senha """
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Recuperação de Senha - Gestão Financeira'
        msg['From'] = EmailConfig.MAIL_DEFAULT_SENDER
        msg['To'] = email_destino
        
        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Recuperação de Senha</h2>
            <p>Você solicitou a recuperação de senha. Utilize o código abaixo:</p>
            <div style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px;">
                {codigo}
            </div>
            <p>Este código expira em {EmailConfig.CODIGO_EXPIRACAO_MINUTOS} minutos.</p>
            <p>Se não foi você quem solicitou, ignore este email.</p>
            <hr>
            <small>Gestão Financeira - Organize suas finanças</small>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo, 'html'))
        
        with smtplib.SMTP(EmailConfig.MAIL_SERVER, EmailConfig.MAIL_PORT) as server:
            server.starttls()
            server.login(EmailConfig.MAIL_USERNAME, EmailConfig.MAIL_PASSWORD)
            server.send_message(msg)
        
        return True, "Email enviado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao enviar email: {str(e)}"

def salvar_codigo_recuperacao(email, codigo):
    """ Salva o código de recuperação no banco """
    expiracao = datetime.now() + timedelta(minutes=EmailConfig.CODIGO_EXPIRACAO_MINUTOS)
    
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE cadastre_se
            SET codigo_recuperacao = ?, 
                codigo_recuperacao_expiracao = ?,
                tentativas_recuperacao = 0
            WHERE email = ?
        """, (codigo, expiracao, email))
        conexao.commit()

def verificar_codigo_recuperacao(email, codigo_digitado):
    """ Verifica se o código de recuperação está correto """
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, codigo_recuperacao, codigo_recuperacao_expiracao, tentativas_recuperacao
            FROM cadastre_se WHERE email = ?
        """, (email,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return False, "Email não encontrado", None
        
        user_id, codigo_salvo, expiracao_str, tentativas = resultado
        expiracao = datetime.strptime(expiracao_str, '%Y-%m-%d %H:%M:%S.%f') if expiracao_str else None
        
        if tentativas >= EmailConfig.MAX_TENTATIVAS:
            return False, "Muitas tentativas. Solicite um novo código.", None
        
        if expiracao and datetime.now() > expiracao:
            return False, "Código expirado. Solicite um novo.", None
        
        if codigo_salvo != codigo_digitado:
            cursor.execute("UPDATE cadastre_se SET tentativas_recuperacao = tentativas_recuperacao + 1 WHERE email = ?", (email,))
            conexao.commit()
            return False, f"Código inválido. Você tem mais {EmailConfig.MAX_TENTATIVAS - tentativas - 1} tentativas.", None
        
        # Código correto
        cursor.execute("""
            UPDATE cadastre_se 
            SET codigo_recuperacao = NULL, 
                codigo_recuperacao_expiracao = NULL,
                tentativas_recuperacao = 0
            WHERE email = ?
        """, (email,))
        conexao.commit()
        
        return True, "Código válido!", user_id