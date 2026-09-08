from flask import redirect, url_for, session
from rotas.middleware.autenticacao import login_required


@login_required
def limpar_filtros():
    """LIMPA TODOS OS FILTROS E REDIRECIONA PARA A LISTA"""
    return redirect(url_for('orcamentos.ini_orcamento'))