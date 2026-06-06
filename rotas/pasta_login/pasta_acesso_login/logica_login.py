""" LÓGICA DO LOGIN  - INICIO """
from flask import Blueprint, render_template, request, url_for, session, jsonify
from utils.database.conexao_global import ini_conexao
# VALIDAÇÃO DE LOGIN
from rotas.pasta_login.pasta_acesso_login.validacoes.validar_usuario import validar_usuario_bd

bp_login = Blueprint('login', __name__)

@bp_login.route('/', methods=['GET', 'POST'])
def validar_login():
    """ INICIO DA VALIDAÇÃO """
    if request.method == 'POST':
        nome_ou_email = request.form.get('nome_ou_email')
        senha = request.form.get('senha')

        # VALIDAÇÃO 1
        if not nome_ou_email or not senha:
            # RETORNO COM JSON
            return jsonify({
                'success': False,
                'message': 'Preencha todos os campos!',
                'type': 'aviso'
            }), 400

        # PRIMEIRO: VERIFICA SE O USUÁRIO EXISTE E SE O EMAIL FOI CONFIRMADO
        conexao, cursor = ini_conexao()
        
            # ← ADICIONA is_master NA CONSULTA
        cursor.execute('SELECT id, nome, email_verificado, is_master FROM cadastre_se WHERE (nome = %s OR email = %s)',
                           (nome_ou_email, nome_ou_email))
        usuario = cursor.fetchone()
            
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado',
                'type': 'erro'
            }), 404
            
        # VERIFICA SE EMAIL FOI CONFIRMADO
        if usuario[2] != 1:  # email_verificado = 0
            return jsonify({
                'success': False,
                'message': 'Email não confirmado! Verifique sua caixa de entrada.',
                'type': 'aviso',
                'user_id': usuario[0]
            }), 403

        # SEGUNDO: VALIDA SENHA
        resultado = validar_usuario_bd(conexao, nome_ou_email, senha)

        if resultado:
            # SETAR NA SESSÃO
            session.permanent = True
            session['user_id'] = usuario[0]      # id
            session['user_nome'] = usuario[1]    # nome
            session['is_master'] = usuario[3] if len(usuario) > 3 else 0  # ← ADICIONA ESTA LINHA

            return jsonify({
                'success': True,
                'message': 'Logado com sucesso!',
                'type': 'sucesso',
                'redirect': url_for('pos_login.iniposlogin')
            })
        
        else:
            return jsonify({
                'success': False,
                'message': 'Senha incorreta',
                'type': 'erro'
            }), 401

    return render_template('pasta_login/pasta_acesso_login/tela_logica_login.html')