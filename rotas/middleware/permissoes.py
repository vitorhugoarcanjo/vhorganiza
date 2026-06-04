# rotas/middleware/permissoes.py
from functools import wraps
from flask import session, flash, redirect, url_for, request
from utils.database.conexao_global import ini_conexao


def requer_master(f):
    """
    Decorator que permite apenas o usuário master (dono do sistema)
    Use em rotas que só o dono do projeto pode acessar
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se está logado
        if 'user_id' not in session:
            flash('Você precisa fazer login.', 'warning')
            return redirect(url_for('login.validar_login'))
        
        # Verifica se é master
        conexao = ini_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT is_master FROM cadastre_se WHERE id = ?", (session['user_id'],))
        resultado = cursor.fetchone()
        
        if not resultado or not resultado[0]:
            flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
            return redirect(request.referrer or url_for('pos_login.iniposlogin'))
        
        return f(*args, **kwargs)
    return decorated_function


def requer_permissao(permissao_nome):
    """
    Decorator para futuro sistema de permissões
    Por enquanto retorna False para quem não é master
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Por enquanto, só master tem permissão
            if 'user_id' not in session:
                flash('Você precisa fazer login.', 'warning')
                return redirect(url_for('login.validar_login'))
            
            conexao = ini_conexao()
            cursor = conexao.cursor()
            cursor.execute("SELECT is_master FROM cadastre_se WHERE id = ?", (session['user_id'],))
            resultado = cursor.fetchone()
            
            if not resultado or not resultado[0]:
                flash(f'Você não tem permissão para: {permissao_nome}', 'danger')
                return redirect(request.referrer or url_for('pos_login.iniposlogin'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator