# rotas/pasta_tarefas/crud_tarefas/pasta_insert/tela_insert.py
from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
import os, sqlite3
import json
from datetime import datetime
from rotas.auditoria_geral.services_auditoria import AuditoriaService

bp_insert_tarefas = Blueprint('insert_tarefas', __name__)

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

@bp_insert_tarefas.route('/', methods=['GET', 'POST'])
def ini_insert():
    if request.method == 'POST':
        user_id = session['user_id']
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        status = request.form.get('status')
        data_inicio = request.form.get('data_inicio')
        data_final = request.form.get('data_final')
        categoria_tarefa = request.form.get('categoria_id')
        prioridade_tarefa = request.form.get('prioridade')

        if categoria_tarefa == '':
            categoria_tarefa = None
        else:
            categoria_tarefa = int(categoria_tarefa) if categoria_tarefa else None

        if data_inicio == '':
            return render_template('pasta_tarefas/crud_tarefas/tela_insert.html.jinja', titulo=titulo, descricao=descricao, status=status, data_final=data_final, categoria_tarefa=categoria_tarefa, prioridade=prioridade_tarefa)


        try:
            conexao_banco = sqlite3.connect(caminho_banco)
            cursor = conexao_banco.cursor()

            # pegar próxima sequência POR USUÁRIO
            cursor.execute(
                "SELECT IFNULL(MAX(tarefa_sequencia), 0) + 1 FROM tarefas WHERE user_id = ?",
                (user_id,)
            )
            tarefa_sequencia = cursor.fetchone()[0]

            # INSERT
            cursor.execute('''
                INSERT INTO tarefas (user_id, titulo, descricao, status, data_inicio, data_final, 
                                     categoria_id, prioridade, tarefa_sequencia, ativo) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, titulo or '', descricao or '', status or 'pendente', 
                  data_inicio, data_final, categoria_tarefa, prioridade_tarefa, tarefa_sequencia))

            conexao_banco.commit()
            conexao_banco.close()

            # ===== AUDITORIA: REGISTRA COMO JSON (igual ao EDIT) =====
            status_map = {'pendente': '⏰ Pendente', 'em andamento': '⏳ Andamento', 'concluido': '✅ Concluído'}
            prioridade_map = {'baixa': '🟢 Baixa', 'media': '🟡 Média', 'alta': '🔴 Alta'}
            

            # Formata data_inicio
            data_inicio_fmt = ''
            if data_inicio:
                data_inicio_fmt = f"{data_inicio[8:10]}/{data_inicio[5:7]}/{data_inicio[0:4]}"
            
            # Formata data_final
            data_final_fmt = ''
            if data_final:
                data_final_fmt = f"{data_final[8:10]}/{data_final[5:7]}/{data_final[0:4]}"
            
            # Busca nome da categoria
            categoria_nome = ''
            if categoria_tarefa:
                try:
                    conn = sqlite3.connect(caminho_banco)
                    c_cursor = conn.cursor()
                    c_cursor.execute("SELECT nome FROM categorias_tarefas WHERE id = ?", (categoria_tarefa,))
                    cat = c_cursor.fetchone()
                    conn.close()
                    if cat:
                        categoria_nome = cat[0]
                except:
                    pass
            
            # Cria lista de alterações (igual ao EDIT)
            alteracoes = [
                {'campo': 'título', 'antes': None, 'depois': titulo or 'Sem título'},
                {'campo': 'descrição', 'antes': None, 'depois': (descricao[:100] + '...') if descricao and len(descricao) > 100 else (descricao or '-')},
                {'campo': 'status', 'antes': None, 'depois': status_map.get(status, status)},
                {'campo': 'prioridade', 'antes': None, 'depois': prioridade_map.get(prioridade_tarefa, prioridade_tarefa)}
            ]
            
            if data_inicio_fmt:
                alteracoes.append({'campo': 'data início', 'antes': None, 'depois': data_inicio_fmt})
            
            if data_final_fmt:
                alteracoes.append({'campo': 'data final', 'antes': None, 'depois': data_final_fmt})
            
            if categoria_nome:
                alteracoes.append({'campo': 'categoria', 'antes': None, 'depois': categoria_nome})
            
            # Registra como JSON
            AuditoriaService.registrar(
                tarefa_id=tarefa_sequencia,
                acao='criada',
                campo_alterado='todos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False)
            )

            return jsonify({
                'success': True,
                'message': f'Tarefa "{titulo}" cadastrada com sucesso!'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute('SELECT id, nome, cor FROM categorias_tarefas WHERE user_id = ?', (session['user_id'],))
    categorias = cursor.fetchall()
    conexao.close()

    return render_template('pasta_tarefas/crud_tarefas/tela_insert.html.jinja', categorias=categorias)