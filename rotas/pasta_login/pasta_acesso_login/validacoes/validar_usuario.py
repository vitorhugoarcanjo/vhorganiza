""" ARQUIVO DE VALIDAÇÃO - ENTRAR """
from rotas.pasta_login.pasta_cadastre_se.validacoes.criptografia_snh import verificar_senha

def validar_usuario_bd(conexao, nome_ou_email, senha):
    """ VERIFICA SENHA E EMAIL/NOME """
    cursor = conexao.cursor()

    cursor.execute('SELECT nome, senha FROM cadastre_se WHERE (nome = %s OR email = %s)',
                   (nome_ou_email, nome_ou_email))
    usuario = cursor.fetchone()

    if usuario and verificar_senha(usuario[1], senha):  # ← VERIFICA SENHA CRIPTOGRAFADA
        return True
    return False
