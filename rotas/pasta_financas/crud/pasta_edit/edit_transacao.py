from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json
import os, sqlite3
from datetime import date, datetime, timedelta

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_edit_transacao = Blueprint('edit_transacoes', __name__)

def converter_valor_br(valor_str):
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)

def get_proxima_sequencia(cursor, user_id):
    cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]

@bp_edit_transacao.route('/<int:sequencia>', methods=['GET', 'POST'])
@login_required
def inieditar(sequencia):
    user_id = session['user_id']
    hoje = date.today().isoformat()

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # =========================
    # GET - Carrega os dados
    # =========================
    if request.method == 'GET':
        # Busca a transação
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
                t.data_vencimento,
                t.total_parcelas,
                t.intervalo_dias,
                t.transacao_pai_id,
                t.numero_parcela
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ? AND t.ativo = 1
        """, (sequencia, user_id))

        transacao_raw = cursor.fetchone()
        
        if not transacao_raw:
            conexao.close()
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404

        transacao_pai_id = transacao_raw[12]
        
        # 🔥 SE FOR UMA PARCELA (tem pai), REDIRECIONA PARA O PAI
        if transacao_pai_id:
            conexao.close()
            return redirect(url_for('edit_transacoes.inieditar', sequencia=transacao_pai_id))
        
        from utils.fomatacoes.data_reutilizavel import formatar_moeda_br
        
        transacao_lista = list(transacao_raw)
        transacao_lista[3] = formatar_moeda_br(transacao_lista[3])  # valor_total
        transacao = tuple(transacao_lista)
        
        total_parcelas = transacao[10] or 1
        
        # Busca as parcelas filhas
        parcelas_filhas = []
        if total_parcelas > 1:
            cursor.execute("""
                SELECT sequencia_transacoes, numero_parcela, data_vencimento, valor_total, status
                FROM transacoes
                WHERE transacao_pai_id = ? AND ativo = 1
                ORDER BY numero_parcela
            """, (sequencia,))
            parcelas_filhas_raw = cursor.fetchall()
            
            for p in parcelas_filhas_raw:
                parcelas_filhas.append({
                    'sequencia': p[0],
                    'numero': p[1],
                    'data_vencimento': p[2],
                    'valor': p[3],
                    'valor_formatado': formatar_moeda_br(p[3]),
                    'status': p[4]
                })
        
        parcelas_filhas_json = json.dumps(parcelas_filhas, default=str) if parcelas_filhas else '[]'

        # Busca categorias do usuário
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
            sequencia=sequencia,
            total_parcelas=total_parcelas,
            parcelas_filhas=parcelas_filhas,
            parcelas_filhas_json=parcelas_filhas_json,
            hoje=hoje
        )

    # =========================
    # POST - Atualiza os dados
    # =========================
    try:
        # 🔥 BUSCA O TIPO ORIGINAL DO BANCO (IGNORA O FORMULÁRIO)
        cursor.execute("""
            SELECT tipo FROM transacoes
            WHERE sequencia_transacoes = ? AND user_id = ? AND ativo = 1
        """, (sequencia, user_id))
        
        tipo_result = cursor.fetchone()
        if not tipo_result:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        tipo = tipo_result[0]  # 🔥 FORÇA O TIPO ORIGINAL
        descricao = request.form.get('descricao')
        valor = converter_valor_br(request.form.get('valor_total'))
        data_vencimento = request.form.get('data_vencimento') or None
        data_emissao = request.form.get('data_emissao') or None
        categoria_id = request.form.get('categoria_id') or None
        total_parcelas = int(request.form.get('total_parcelas', 1))
        
        # Busca dados atuais da transação
        cursor.execute("""
            SELECT t.descricao, t.valor_total, t.data_emissao, t.data_vencimento, 
                   t.categoria_id, ct.nome AS categoria_nome, t.total_parcelas
            FROM transacoes t
            LEFT JOIN categorias_financas ct ON t.categoria_id = ct.id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ?
        """, (sequencia, user_id))

        dados_antes = cursor.fetchone()
        total_parcelas_antes = dados_antes[6] if dados_antes else 1
        
        # Atualiza a transação principal
        cursor.execute("""
            UPDATE transacoes 
            SET descricao = ?, 
                valor_total = ?, 
                data_emissao = ?,
                data_vencimento = ?,
                categoria_id = ?,
                total_parcelas = ?,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE sequencia_transacoes = ? AND user_id = ?
        """, (
            descricao, valor,
            data_emissao, data_vencimento,
            categoria_id,
            total_parcelas,
            sequencia, user_id
        ))

        # ==========================================================
        # GERENCIAMENTO DE PARCELAS
        # ==========================================================
        if total_parcelas > 1:
            intervalo_dias = int(request.form.get('intervaloDias', 30))
            primeiro_vencimento = request.form.get('primeiroVencimento', data_vencimento or data_emissao)
            
            valores_parcelas = []
            for i in range(1, total_parcelas + 1):
                valor_parcela = request.form.get(f'parcela_valor_{i}')
                if valor_parcela:
                    valores_parcelas.append(converter_valor_br(valor_parcela))
                else:
                    valores_parcelas.append(valor / total_parcelas)
            
            # Remove parcelas filhas antigas
            cursor.execute("""
                UPDATE transacoes 
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                WHERE transacao_pai_id = ? AND ativo = 1
            """, (sequencia,))
            
            # Cria as novas parcelas
            for i in range(1, total_parcelas + 1):
                if i == 1:
                    data_venc_parcela = primeiro_vencimento
                else:
                    data_base = datetime.strptime(primeiro_vencimento, '%Y-%m-%d')
                    data_venc_parcela = (data_base + timedelta(days=(i-1) * intervalo_dias)).strftime('%Y-%m-%d')
                
                valor_parcela = valores_parcelas[i-1]
                sequencia_parcela = get_proxima_sequencia(cursor, user_id)
                
                cursor.execute("""
                    INSERT INTO transacoes (
                        user_id, sequencia_transacoes, tipo,
                        valor_total, valor_parcela, descricao, categoria_id,
                        data_emissao, data_vencimento,
                        total_parcelas, numero_parcela, sequencia_parcela,
                        transacao_pai_id, status, ativo
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'aberto', 1)
                """, (
                    user_id, sequencia_parcela, tipo,
                    valor_parcela, valor_parcela, f'{descricao} - Parcela {i}/{total_parcelas}', categoria_id,
                    data_emissao, data_venc_parcela,
                    total_parcelas, i, i,
                    sequencia
                ))
            
            # Atualiza o intervalo na transação pai
            cursor.execute("""
                UPDATE transacoes 
                SET intervalo_dias = ? 
                WHERE sequencia_transacoes = ? AND user_id = ?
            """, (intervalo_dias, sequencia, user_id))
        
        elif total_parcelas_antes > 1:
            # Se tinha parcelas e agora não tem mais
            cursor.execute("""
                UPDATE transacoes 
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                WHERE transacao_pai_id = ? AND ativo = 1
            """, (sequencia,))

        conexao.commit()

        # ==========================================================
        # AUDITORIA
        # ==========================================================
        alteracoes = []

        if dados_antes[0] != descricao:
            alteracoes.append({'campo': 'descrição', 'antes': dados_antes[0], 'depois': descricao})

        if dados_antes[1] != valor:
            alteracoes.append({'campo': 'valor', 'antes': f'R$ {dados_antes[1]:.2f}', 'depois': f'R$ {valor:.2f}'})

        if dados_antes[2] != data_emissao:
            alteracoes.append({'campo': 'data emissão', 'antes': dados_antes[2], 'depois': data_emissao})

        if dados_antes[3] != data_vencimento:
            alteracoes.append({'campo': 'data vencimento', 'antes': dados_antes[3], 'depois': data_vencimento})

        if dados_antes[4] != categoria_id:
            nome_antigo = dados_antes[5] or 'Sem categoria'
            nome_novo = 'Sem categoria'
            if categoria_id:
                cursor.execute("SELECT nome FROM categorias_financas WHERE id = ?", (categoria_id,))
                nova_categoria = cursor.fetchone()
                nome_novo = nova_categoria[0] if nova_categoria else 'Sem categoria'
            if nome_antigo != nome_novo:
                alteracoes.append({'campo': 'categoria', 'antes': nome_antigo, 'depois': nome_novo})

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
        import traceback
        traceback.print_exc()
        conexao.close()
        return jsonify({'success': False, 'error': str(e)})