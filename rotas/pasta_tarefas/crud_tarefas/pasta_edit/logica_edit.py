# rotas/pasta_tarefas/crud_tarefas/pasta_edit/logica_edit.py
from flask import Blueprint, render_template, request, session, jsonify
import json
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.services_auditoria import AuditoriaService
from utils.database.conexao_global import ini_conexao


bp_tela_edit = Blueprint('editar_tarefa', __name__)


@bp_tela_edit.route('/editar_tarefa/<int:tarefa_seq>', methods=['GET', 'POST'])
@login_required
def iniedittarefa(tarefa_seq):
    user_id = session['user_id']

    conexao, cursor = ini_conexao()

    cursor.execute("""
        SELECT t.titulo, t.descricao, t.status, t.data_inicio, t.data_final, 
               t.categoria_id, t.prioridade, c.nome as categoria_nome, c.cor as categoria_cor
        FROM tarefas t
        LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id
        WHERE t.tarefa_sequencia = %s AND t.user_id = %s
    """, (tarefa_seq, user_id))
    tarefa = cursor.fetchone()

    cursor.execute("SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = %s", (user_id,))
    todas_categorias = cursor.fetchall()

    # ========== GET ==========
    if request.method == 'GET':
        return render_template(
            'pasta_tarefas/crud_tarefas/tela_edit.html',
            tarefa=tarefa,
            tarefa_seq=tarefa_seq,
            todas_categorias=todas_categorias
        )

    # ========== POST (AJAX) ==========
    try:
        titulo = request.form.get('titulo', '')
        descricao = request.form.get('descricao', '')
        status = request.form.get('status', '')
        data_inicio = request.form.get('data_inicio', '') or None  # 🔥 CORRIGIDO
        data_final = request.form.get('data_final', '') or None    # 🔥 CORRIGIDO
        categoria_id = request.form.get('categoria_id', '')
        prioridade = request.form.get('prioridade', '')

        if categoria_id == '':
            categoria_id = None
        else:
            categoria_id = int(categoria_id)

        # BUSCA DADOS ANTES
        cursor.execute("""
            SELECT titulo, descricao, status, prioridade 
            FROM tarefas 
            WHERE tarefa_sequencia = %s AND user_id = %s
        """, (tarefa_seq, user_id))
        dados_antes = cursor.fetchone()

        # UPDATE
        cursor.execute('''
            UPDATE tarefas 
            SET titulo = %s, descricao = %s, status = %s, data_inicio = %s, 
                data_final = %s, categoria_id = %s, prioridade = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE tarefa_sequencia = %s AND user_id = %s
        ''', (titulo, descricao, status, data_inicio, data_final, categoria_id, prioridade, tarefa_seq, user_id))
        
        # ===== AUDITORIA =====
        alteracoes = []
        
        status_map = {'pendente': '⏰ Pendente', 'em andamento': '⏳ Andamento', 'concluido': '✅ Concluído'}
        prioridade_map = {'baixa': '🟢 Baixa', 'media': '🟡 Média', 'alta': '🔴 Alta'}

        if dados_antes[0] != titulo:
            alteracoes.append({
                'campo': 'título',
                'antes': dados_antes[0],
                'depois': titulo
            })

        if dados_antes[1] != descricao:
            alteracoes.append({
                'campo': 'descrição',
                'antes': dados_antes[1][:100] + "..." if dados_antes[1] and len(dados_antes[1]) > 100 else dados_antes[1],
                'depois': descricao[:100] + "..." if descricao and len(descricao) > 100 else descricao
            })

        if dados_antes[2] != status:
            alteracoes.append({
                'campo': 'status',
                'antes': status_map.get(dados_antes[2], dados_antes[2]),
                'depois': status_map.get(status, status)
            })

        if dados_antes[3] != prioridade:
            alteracoes.append({
                'campo': 'prioridade',
                'antes': prioridade_map.get(dados_antes[3], dados_antes[3]),
                'depois': prioridade_map.get(prioridade, prioridade)
            })

        if alteracoes:
            AuditoriaService.registrar(
                tarefa_id=tarefa_seq,
                acao='editada',
                campo_alterado='múltiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False, default=str),
                conexao=conexao
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': 'Tarefa atualizada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500