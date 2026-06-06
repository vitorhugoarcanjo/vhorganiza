from flask import flash
import re

def validar_campos_obrigatorios(nome, telefone, email, senha, confirmar_senha):
# ---------------- VALIDAÇÕES GERAL ---------------- #
    if not nome or not telefone or not email or not senha or not confirmar_senha:
        flash('Falta campos obrigatórios para se cadastrar!', 'warning')
        return False
    return True
# ---------------- VALIDAÇÕES GERAL ---------------- #


# ---------------- VALIDAÇÕES SENHA ---------------- #
def validar_senha_tamanho(senha):
    if len(senha) < 6:
        flash('Senha deve ter no mínimo 6 caracteres', 'error')
        return False
    return True



def validar_confirmacao_senha(senha, confirmar_senha):
    if senha != confirmar_senha:
        flash('As senhas não coincidem!', 'error')
        return False
    return True
# ---------------- VALIDAÇÕES SENHA ---------------- #


# ---------------- VALIDAÇÕES NO E-MAIL ---------------- #
def validar_email_formato(email):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        flash('E-mail inválido!', 'error')
        return False
    return True

def validar_email_unico(conexao, email):
    cursor = conexao.cursor()

    cursor.execute('SELECT id FROM cadastre_se WHERE email = %s', (email,))
    resultado = cursor.fetchone()

    if resultado:
        flash('E-mail já cadastrado!', 'error')
        return False
    return True
# ---------------- VALIDAÇÕES NO E-MAIL ---------------- #


# ---------------- VALIDAÇÕES NO TELEFONE ---------------- #
def validar_e_limpar_telefone(telefone):
    """VALIDA TELEFONE E RETORNO APENAS NÚMEROS"""

    # REMOVE TUDO QUE NÃO É NÚMERO
    telefone_limpo = re.sub(r'\D', '', telefone)

    # VÁLIDA SE TEM 10 OU 11 DÍGITOS (COM DDD)
    if len(telefone_limpo) not in [10, 11]:
        flash('Telefone deve ter 10 ou 11 dígitos (com DDD)!', 'error')
        return None
    
    return telefone_limpo
# ---------------- VALIDAÇÕES NO TELEFONE ---------------- #
