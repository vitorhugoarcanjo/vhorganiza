from flask import Blueprint, render_template, request, session, jsonify
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json
import os, sqlite3

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_edit_transacao = Blueprint('edit_transacoes', __name__)

def converter_valor_br(valor_str):
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)

@bp_edit_transacao.route('/<int:sequencia>', methods=['GET', 'POST'])
@login_required
def inieditar(sequencia):
    user_id = session['user_id']

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # =========================
    # GET
    # =========================
    if request.method == 'GET':
        cursor.execute("""
            SELECT 
                t.sequencia_transacoes,
                t.id,
                t.tipo,
                t.valor_total,
                t.descricao,
                t.data_emissao,
                t.categoria_id,
                c.nome,
                c.cor,
                t.data_vencimento
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ?
        """, (sequencia, user_id))

        transacao_raw = cursor.fetchone()
        
        if not transacao_raw:
            conexao.close()
            return jsonify({'success': False, 'error': 'Transação não encontrada'})

        from utils.fomatacoes.data_reutilizavel import formatar_moeda_br
        transacao_lista = list(transacao_raw)
        transacao_lista[3] = formatar_moeda_br(transacao_lista[3])
        transacao = tuple(transacao_lista)

        cursor.execute("""
            SELECT id, nome, cor
            FROM categorias_financas
            WHERE user_id = ?
        """, (user_id,))
        categorias = cursor.fetchall()

        conexao.close()

        return render_template(
            'pasta_financas/crud/edit_transacao.html',
            transacao=transacao,
            categorias=categorias,
            sequencia=sequencia
        )

    # =========================
    # POST (AJAX)
    # =========================
    try:
        descricao = request.form.get('descricao')
        valor = converter_valor_br(request.form.get('valor_total'))
        data_vencimento = request.form.get('data_vencimento') or None
        data_emissao = request.form.get('data_emissao') or None
        categoria_id = request.form.get('categoria_id') or None

        cursor.execute("""
            SELECT t.descricao, t.valor_total, t.data_emissao, t.data_vencimento, t.categoria_id, ct.nome AS categoria_nome 
            FROM transacoes t
            LEFT JOIN categorias_financas ct ON t.categoria_id = ct.id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ?
        """, (sequencia, user_id))

        dados_antes = cursor.fetchone()

        cursor.execute("""
            UPDATE transacoes 
            SET descricao = ?, 
                valor_total = ?, 
                data_emissao = ?,
                data_vencimento = ?,
                categoria_id = ?
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (
            descricao, valor,
            data_emissao, data_vencimento,
            categoria_id,
            sequencia, user_id
        ))

        conexao.commit()

        # Auditoria
        alteracoes = []

        if dados_antes[0] != descricao:
            alteracoes.append({
                'campo': 'descrição',
                'antes': dados_antes[0],
                'depois': descricao
            })

        if dados_antes[1] != valor:
            alteracoes.append({
                'campo': 'valor',
                'antes': f'R$ {dados_antes[1]:.2f}',
                'depois': f'R$ {valor:.2f}'
            })

        if dados_antes[2] != data_emissao:
            alteracoes.append({
                'campo': 'data emissão',
                'antes': dados_antes[2],
                'depois': data_emissao
            })

        if dados_antes[3] != data_vencimento:
            alteracoes.append({
                'campo': 'data vencimento',
                'antes': dados_antes[3],
                'depois': data_vencimento
            })

        # Se quiser mostrar o nome da nova categoria (mais amigável):
# Se quiser mostrar o nome da nova categoria (mais amigável):
        categoria_id_novo = int(categoria_id) if categoria_id else None
        if dados_antes[4] != categoria_id_novo:
            nome_antigo = dados_antes[5] or 'Sem categoria'
            nome_novo = 'Sem categoria'
            if categoria_id_novo:
                cursor.execute("SELECT nome FROM categorias_financas WHERE id = ?", (categoria_id_novo,))
                nova_categoria = cursor.fetchone()
                nome_novo = nova_categoria[0] if nova_categoria else 'Sem categoria'
            
            # SÓ adiciona se realmente mudou o NOME
            if nome_antigo != nome_novo:
                alteracoes.append({
                    'campo': 'categoria',
                    'antes': nome_antigo,
                    'depois': nome_novo
                })

        if alteracoes:
            AuditoriaFinanceiraService.registrar(
                transacao_id=sequencia,
                acao='editada',
                campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'],
                valor_antigo=json.dumps(alteracoes, ensure_ascii=False),
                valor_novo=json.dumps(alteracoes, ensure_ascii=False)
            )

        conexao.close()

        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso!'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})