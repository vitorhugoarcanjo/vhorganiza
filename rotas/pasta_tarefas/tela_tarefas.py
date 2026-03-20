from flask import Blueprint, render_template, session, redirect, url_for, flash
import os, sqlite3
from datetime import date
from rotas.middleware.autenticacao import login_required

# FILTROS
from .crud_tarefas.pasta_filtros.tarefas_filtros import *

# FORMATACOES - DATA
from .validacoes.formatacoes import *

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_tela_tarefas = Blueprint('tarefas', __name__)

@bp_tela_tarefas.route('/', methods=['GET', 'POST'])
@login_required
def ini_tarefas():
    # LÓGICA PARA O FILTRO DATA
    data_hoje = date.today()
    data_inicio, data_fim = filtro_datas(data_hoje)

    # FILTRO CATEGORIAS
    categorias_filtro, categorias_usuario = filtro_categorias(session['user_id'])

    # FILTRO STATUS
    status_filtro = filtro_status()

    # FILTRO PRIORIDADE
    prioridade_filtro = filtro_prioridade()

    # FILTRO DESCRICAO
    descricao_filtro = filtro_descricao()

    with sqlite3.connect(caminho_banco) as conexao_banco:
        cursor = conexao_banco.cursor()

        query = """SELECT t.tarefa_sequencia, t.descricao, t.status, t.data_inicio, t.data_final, t.categoria_id, t.prioridade,
                       c.nome as categoria_nome, c.cor as categoria_cor
                    FROM tarefas t 
                    LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id   
                    WHERE t.user_id = ?
                    """
        
        params = [session['user_id']]
        
        # QUERY DATA INICIO E FIM
        if data_inicio and data_fim:
            query += " AND t.data_inicio BETWEEN ? AND ?"
            params.extend([data_inicio, data_fim])


        # QUERY FILTRO CATEGORIAS
        if categorias_filtro:
            categorias_conditions = []
            params_temp = []
            
            for cat in categorias_filtro:
                if cat == 'null':
                    # Busca tarefas SEM categoria (campo vazio ou NULL)
                    categorias_conditions.append("(t.categoria_id IS NULL OR t.categoria_id = '')")
                else:
                    categorias_conditions.append("t.categoria_id = ?")
                    params_temp.append(cat)
            
            if categorias_conditions:
                query += " AND (" + " OR ".join(categorias_conditions) + ")"
                params.extend(params_temp)


        # QUERY FILTRO STATUS
        if status_filtro:
            if status_filtro == 'vazio':
                query += " AND (t.status is NULL OR t.status = '')"

            elif status_filtro == 'concluido_em_andamento':
                query += " AND (t.status = 'concluido' OR t.status = 'em andamento')"

            else:
                query += " AND t.status = ?"
                params.append(status_filtro)
        

        # QUERY FILTRO PRIORIDADE
        if prioridade_filtro:
            if prioridade_filtro == 'vazio':
                query += " AND (t.prioridade IS NULL OR t.prioridade = '')"
            else:
                query += " AND t.prioridade = ?"
                params.append(prioridade_filtro)


        # QUERY FILTRO DESCRIÇÃO
        if descricao_filtro:
            query += " AND t.descricao LIKE ?"
            params.append(f"%{descricao_filtro}%")

                
        query += " ORDER BY t.tarefa_sequencia ASC"
        cursor.execute(query, params)
        tarefas = cursor.fetchall()

        tarefas = formatar_tarefas(tarefas)
    return render_template('pasta_tarefas/tela_tarefas.html.jinja', user_nome=session.get('user_nome'),
                           tarefas=tarefas,
                           data_hoje=data_hoje,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           categorias_usuario=categorias_usuario, categorias_filtro=categorias_filtro,
                           status_filtro=status_filtro,
                           prioridade_filtro=prioridade_filtro,
                           descricao_filtro=descricao_filtro
                           )


# FUNÇÃO DE CONCLUIR TAREFA
@bp_tela_tarefas.route('/concluir/<int:tarefa_seq>', methods=['POST'])
@login_required
def concluir_tarefa(tarefa_seq):
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()
        
        cursor.execute('UPDATE tarefas SET status = ? WHERE tarefa_sequencia = ? AND user_id = ?', ('concluido', tarefa_seq, session['user_id']))
        conexao.commit()

        flash('Tarefa concluída com sucesso!', 'success')
        return redirect(url_for('tarefas.ini_tarefas'))




# FUNÇÃO PARA EXCLUIR TAREFA
@bp_tela_tarefas.route('/excluir/<int:tarefa_seq>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_seq):
    with sqlite3.connect(caminho_banco) as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM tarefas WHERE tarefa_sequencia = ? AND user_id = ?', (tarefa_seq, session['user_id'] ))

        conexao.commit()

        flash('Tarefa excluída com sucesso!', 'success')
        return redirect(url_for('tarefas.ini_tarefas'))


# FUNÇÃO PARA LIMPAR SESSION DE CONSULTA
@bp_tela_tarefas.route('/limpar_filtros')
@login_required
def limpar_filtros():
    """ Limpa todos os filtros da sessão """
    
    # Remove todas as variáveis de filtro da sessão
    session.pop('status_filtro', None)
    session.pop('prioridade_filtro', None)
    session.pop('descricao_filtro', None)  # <-- ADICIONADO
    session.pop('data_inicio_intervalo', None)
    session.pop('data_fim_intervalo', None)
    session.pop('modo', None)
    session.pop('mes_corrente', None)
    session.pop('dia_corrente', None)
    session.pop('dia_referencia', None)
    
    return redirect(url_for('tarefas.ini_tarefas'))