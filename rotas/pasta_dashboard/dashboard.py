from flask import Blueprint, render_template, session, request, redirect, url_for
from rotas.middleware.autenticacao import login_required
from utils.filtros_reutilizaveis.data import filtro_datas
from datetime import date
import sqlite3, os

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_dashboard = Blueprint('dashboard', __name__)


@bp_dashboard.route('/', methods=['GET', 'POST'])
@login_required
def inidashboard():
    data_hoje = date.today()
    user_id = session['user_id']

    # ===== FILTRO DE DATA (MESMA FUNÇÃO DO FINANÇAS) =====
    data_inicio, data_fim, tipo_data = filtro_datas(data_hoje, prefixo='dashboard')
    
    # 🔥 CORREÇÃO: Se tipo_data for 'inicio' (padrão do tarefas), muda para 'emissao'
    if tipo_data == 'inicio':
        tipo_data = 'emissao'
        session['dashboard_tipo_data'] = 'emissao'
    else:
        session['dashboard_tipo_data'] = tipo_data

    # ===== PROCESSAMENTO DOS FILTROS (POST) =====
    if request.method == 'POST':
        # O filtro_datas já processou o tipo_filtro, só precisamos redirecionar
        return redirect(url_for('dashboard.inidashboard'))

    # ===== CONSULTA AO BANCO =====
    conexao_banco = sqlite3.connect(caminho_banco)
    cursor = conexao_banco.cursor()

    # Query base
    query_receitas = 'SELECT SUM(valor_total) FROM transacoes WHERE user_id = ? AND tipo = ?'
    query_despesas = 'SELECT SUM(valor_total) FROM transacoes WHERE user_id = ? AND tipo = ?'
    params_receitas = [user_id, 'receita']
    params_despesas = [user_id, 'despesa']

    # 🔥 FILTRO DE DATA (mesma lógica do finanças)
    if data_inicio and data_fim:
        if tipo_data == 'emissao':
            query_receitas += ' AND DATE(data_emissao) BETWEEN ? AND ?'
            query_despesas += ' AND DATE(data_emissao) BETWEEN ? AND ?'
            params_receitas.extend([data_inicio, data_fim])
            params_despesas.extend([data_inicio, data_fim])
        elif tipo_data == 'vencimento':
            query_receitas += ' AND DATE(data_vencimento) BETWEEN ? AND ?'
            query_despesas += ' AND DATE(data_vencimento) BETWEEN ? AND ?'
            params_receitas.extend([data_inicio, data_fim])
            params_despesas.extend([data_inicio, data_fim])

    # Executa consultas
    cursor.execute(query_receitas, params_receitas)
    total_receitas = cursor.fetchone()[0] or 0

    cursor.execute(query_despesas, params_despesas)
    total_despesas = cursor.fetchone()[0] or 0

    saldo = total_receitas - total_despesas

    conexao_banco.close()

    return render_template('pasta_dashboard/tela_dashboard.html',
                          total_receitas=total_receitas,
                          total_despesas=total_despesas,
                          saldo=saldo,
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          tipo_data=tipo_data)


# ===== LIMPAR FILTROS =====
@bp_dashboard.route('/limpar_filtros')
@login_required
def limpar_filtros():
    """ Limpa todos os filtros da sessão do dashboard """
    
    prefixo = 'dashboard'

    # LIMPA FILTROS GERAIS
    session.pop('dashboard_tipo_data', None)

    # LIMPA FILTROS DE DATA (COM PREFIXO)
    session.pop(f'{prefixo}_data_inicio_intervalo', None)
    session.pop(f'{prefixo}_data_fim_intervalo', None)
    session.pop(f'{prefixo}_modo', None)
    session.pop(f'{prefixo}_mes_corrente', None)
    session.pop(f'{prefixo}_dia_corrente', None)
    session.pop(f'{prefixo}_dia_referencia', None)
    session.pop(f'{prefixo}_tipo_data', None)

    return redirect(url_for('dashboard.inidashboard'))