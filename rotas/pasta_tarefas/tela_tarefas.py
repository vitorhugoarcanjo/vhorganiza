from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import date
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao

from datetime import datetime, timedelta, timezone

# FILTROS
from .crud_tarefas.pasta_filtros.tarefas_filtros import (
    filtro_categorias,
    filtro_status,
    filtro_prioridade,
    filtro_descricao
)
from utils.filtros_reutilizaveis.data import filtro_datas

# FORMATACOES - DATA
from .validacoes.formatacoes import *

bp_tela_tarefas = Blueprint('tarefas', __name__)

@bp_tela_tarefas.route('/', methods=['GET', 'POST'])
@login_required
def ini_tarefas():
    # LÓGICA PARA O FILTRO DATA
    data_hoje = date.today()
    data_inicio, data_fim, tipo_data = filtro_datas(data_hoje, prefixo='tarefas')

    # FILTRO CATEGORIAS
    categorias_filtro, categorias_usuario = filtro_categorias(session['user_id'])

    # FILTRO STATUS
    status_filtro = filtro_status()

    # FILTRO PRIORIDADE
    prioridade_filtro = filtro_prioridade()

    # FILTRO DESCRICAO
    descricao_filtro = filtro_descricao()

    # FILTRO ATIVO/INATIVO - CORRIGIDO
    # 1. Tenta pegar da URL (GET)
    mostrar_inativas = request.args.get('mostrar_inativas')
    
    # 2. Se veio do POST, pega do formulário
    if mostrar_inativas is None and request.method == 'POST':
        mostrar_inativas = request.form.get('mostrar_inativas')
    
    # 3. Se ainda não tem, pega da sessão
    if mostrar_inativas is None:
        mostrar_inativas = session.get('mostrar_inativas', '0')
    
    # 4. Salva na sessão para manter
    session['mostrar_inativas'] = mostrar_inativas
    

    conexao = ini_conexao()
    cursor = conexao.cursor()

    query = """SELECT t.tarefa_sequencia, t.titulo, t.descricao, t.status, t.data_inicio, t.data_final, t.data_finalizacao, t.categoria_id, t.prioridade,
                    c.nome as categoria_nome, c.cor as categoria_cor, t.ativo
                FROM tarefas t 
                LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id   
                WHERE t.user_id = ?
                """
    
    params = [session['user_id']]
    
    # QUERY FILTRO DATA
    if data_inicio and data_fim:
        if tipo_data == 'inicio':
            query += " AND t.data_inicio BETWEEN ? AND ?"
            params.extend([data_inicio, data_fim])
        elif tipo_data == 'final':
            query += " AND t.data_final BETWEEN ? AND ?"
            params.extend([data_inicio, data_fim])
        else:  # finalizacao
            # Para data_finalizacao (que tem hora), compara apenas a data
            query += " AND DATE(t.data_finalizacao) BETWEEN ? AND ?"
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

        elif status_filtro == 'pendente_em_andamento':
            query += " AND (t.status = 'pendente' OR t.status = 'em andamento')"

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

            
    # FILTRO ATIVO/INATIVO
    if mostrar_inativas == '1':
        query += " AND t.ativo = 0"      # Só inativas
    elif mostrar_inativas == '2':
        pass                              # Todas (não adiciona filtro)
    else:
        query += " AND t.ativo = 1"      # Só ativas (padrão)


    query += " ORDER BY t.tarefa_sequencia ASC"
    cursor.execute(query, params)
    tarefas = cursor.fetchall()

    tarefas = formatar_tarefas(tarefas)
    return render_template('pasta_tarefas/tela_tarefas.html.jinja', user_nome=session.get('user_nome'),
                           tarefas=tarefas,
                           data_hoje=data_hoje,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           tipo_data=tipo_data,
                           mostrar_inativas=mostrar_inativas,
                           categorias_usuario=categorias_usuario, categorias_filtro=categorias_filtro,
                           status_filtro=status_filtro,
                           prioridade_filtro=prioridade_filtro,
                           descricao_filtro=descricao_filtro
                           )


# rotas/pasta_tarefas/tela_tarefas.py
@bp_tela_tarefas.route('/detalhes/<int:tarefa_seq>')
@login_required
def detalhes_tarefa(tarefa_seq):
    """Retorna os detalhes de uma tarefa via JSON"""
    conexao = ini_conexao()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT t.tarefa_sequencia, t.titulo, t.descricao, t.status,
                t.data_inicio, t.data_final, t.data_finalizacao,
                t.prioridade, t.motivo_conclusao, c.nome as categoria_nome, c.cor as categoria_cor
        FROM tarefas t 
        LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id
        WHERE t.tarefa_sequencia = ? AND t.user_id = ?
    """, (tarefa_seq, session['user_id']))
    
    tarefa = cursor.fetchone()
    
    if not tarefa:
        return {"error": "Tarefa não encontrada"}, 404
    
    # Formata datas
    from .validacoes.formatacoes import formatar_data
    
    return {
        'id': tarefa[0],
        'titulo': tarefa[1] or 'Sem título',
        'descricao': tarefa[2] or 'Sem descrição',
        'status': tarefa[3],
        'status_label': '✅ Concluída' if tarefa[3] == 'concluido' else '⏳ Em Andamento' if tarefa[3] == 'em andamento' else '⏰ Pendente',
        'data_inicio': formatar_data(tarefa[4]),
        'data_final': formatar_data(tarefa[5]),
        'data_finalizacao': formatar_data(tarefa[6]),
        'prioridade': tarefa[7],
        'motivo_conclusao': tarefa[8],
        'prioridade_label': '🔴 Alta' if tarefa[7] == 'alta' else '🟡 Média' if tarefa[7] == 'media' else '🟢 Baixa',
        'categoria': tarefa[9] or 'Sem categoria',
        'categoria_cor': tarefa[10] or '#6c757d'
    }


# FUNÇÃO DE CONCLUIR TAREFA (COM AUDITORIA)
@bp_tela_tarefas.route('/concluir/<int:tarefa_seq>', methods=['POST'])
@login_required
def concluir_tarefa(tarefa_seq):
    motivo = request.form.get('motivo_conclusao', '').strip()

    fuso = timezone(timedelta(hours=-4))
    agora = datetime.now(fuso).strftime("%Y-%m-%d %H:%M:%S")
    
    conexao = ini_conexao()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT titulo, descricao, status 
        FROM tarefas 
        WHERE tarefa_sequencia = ? AND user_id = ?
    """, (tarefa_seq, session['user_id']))

    tarefa_antes = cursor.fetchone()

    if not tarefa_antes:
        return jsonify({
            'success': False,
            'error': 'Tarefa não encontrada.'
        })

    cursor.execute("""
        UPDATE tarefas 
        SET status = 'concluido', 
            data_finalizacao = ?,
            updated_at = ?,
            motivo_conclusao = ?
        WHERE tarefa_sequencia = ? AND user_id = ?
    """, (
        agora,
        agora,
        motivo if motivo else None,
        tarefa_seq,
        session['user_id']
    ))
    
    data_finalizacao = agora

    
    AuditoriaService.registrar(
        tarefa_id=tarefa_seq,
        acao='concluir_tarefa',
        campo_alterado='status_e_motivo',
        valor_antigo=f"Status: {tarefa_antes[2]}",
        valor_novo=f"Status: concluido | Motivo: {motivo if motivo else 'Sem observações'}",
        conexao=conexao
    )

    conexao.commit()

    return jsonify({
        'success': True,
        'message': f'Tarefa "{tarefa_antes[0]}" concluída com sucesso!',
        'data_finalizacao': data_finalizacao
    })


# FUNÇÃO PARA EXCLUIR TAREFA (AGORA É INATIVAR - COM AUDITORIA)
@bp_tela_tarefas.route('/excluir/<int:tarefa_seq>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_seq):
    conexao = ini_conexao()
    cursor = conexao.cursor()
    
    # Busca dados antes
    cursor.execute("""
        SELECT titulo 
        FROM tarefas 
        WHERE tarefa_sequencia = ? AND user_id = ? AND ativo = 1
    """, (tarefa_seq, session['user_id']))
    
    tarefa = cursor.fetchone()
    
    if not tarefa:
        return jsonify({
            'success': False,
            'error': 'Tarefa não encontrada ou já inativada.'
        })

    # INATIVA
    cursor.execute('''
        UPDATE tarefas 
        SET ativo = 0, 
            excluido_em = datetime('now', 'localtime'),
            excluido_por = ?,
            updated_at = datetime('now', 'localtime')
        WHERE tarefa_sequencia = ? AND user_id = ?
    ''', (session['user_id'], tarefa_seq, session['user_id']))
    
    # Auditoria
    AuditoriaService.registrar(
        tarefa_id=tarefa_seq,
        acao='inativacao',
        valor_novo=f"Tarefa '{tarefa[0] or 'Sem título'}' inativada",
        conexao=conexao
    )

    conexao.commit()

    return jsonify({
        'success': True,
        'message': f'Tarefa "{tarefa[0]}" inativada com sucesso!'
    })
    

# FUNÇÃO PARA LIMPAR SESSION DE CONSULTA
@bp_tela_tarefas.route('/limpar_filtros')
@login_required
def limpar_filtros():
    """ Limpa todos os filtros da sessão """

    prefixo = 'tarefas'

    # FILTROS GERAIS
    session.pop('status_filtro', None)
    session.pop('prioridade_filtro', None)
    session.pop('descricao_filtro', None)
    session.pop('mostrar_inativas', None)

    # FILTROS DE DATA (COM PREFIXO)
    session.pop(f'{prefixo}_data_inicio_intervalo', None)
    session.pop(f'{prefixo}_data_fim_intervalo', None)
    session.pop(f'{prefixo}_modo', None)
    session.pop(f'{prefixo}_mes_corrente', None)
    session.pop(f'{prefixo}_dia_corrente', None)
    session.pop(f'{prefixo}_dia_referencia', None)
    session.pop(f'{prefixo}_tipo_data', None)

    return redirect(url_for('tarefas.ini_tarefas'))