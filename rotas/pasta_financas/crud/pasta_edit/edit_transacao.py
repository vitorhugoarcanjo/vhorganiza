from flask import Blueprint, redirect, render_template, url_for, request, session, flash
from rotas.middleware.autenticacao import login_required
import sqlite3, os
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_edit_transacao = Blueprint('edit_transacoes', __name__)

def converter_valor_br(valor_str):
    """Converte formato brasileiro '1.234,56' para float 1234.56"""
    if not valor_str:
        return 0.0
    # Remove R$ se tiver
    valor_str = valor_str.replace('R$', '').strip()
    # Remove pontos de milhar
    valor_str = valor_str.replace('.', '')
    # Troca vírgula por ponto
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
                t.status,
                t.data_vencimento
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.sequencia_transacoes = ? AND t.user_id = ?
        """, (sequencia, user_id))

        transacao_raw = cursor.fetchone()
        
        if not transacao_raw:
            conexao.close()
            flash('Transação não encontrada!', 'danger')
            return redirect(url_for('financas.inifinancas'))
        
        # 🔥 Formata o valor para exibir no input
        from utils.fomatacoes.data_reutilizavel import formatar_moeda_br
        transacao_lista = list(transacao_raw)
        transacao_lista[3] = formatar_moeda_br(transacao_lista[3])  # Formata valor
        transacao = tuple(transacao_lista)

        # categorias pro select
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
    # POST
    # =========================
    descricao = request.form.get('descricao')
    # 🔥 CONVERTE O VALOR (mesma função)
    valor = converter_valor_br(request.form.get('valor_total'))
    tipo = request.form.get('tipo')
    data_emissao = request.form.get('data_emissao')
    data_vencimento = request.form.get('data_vencimento')
    categoria_id = request.form.get('categoria_id') or None
    status = request.form.get('status')

    # Busca dados ANTES da edição
    cursor.execute("""
        SELECT descricao, valor_total, status, tipo
        FROM transacoes 
        WHERE sequencia_transacoes = ? AND user_id = ?
    """, (sequencia, user_id))
    dados_antes = cursor.fetchone()

    cursor.execute("""
        UPDATE transacoes 
        SET descricao = ?, 
            valor_total = ?, 
            tipo = ?, 
            data_emissao = ?,
            data_vencimento = ?,
            categoria_id = ?,
            status = ?
        WHERE sequencia_transacoes = ? AND user_id = ?
    """, (
        descricao, valor, tipo,
        data_emissao, data_vencimento,
        categoria_id, status,
        sequencia, user_id
    ))

    conexao.commit()

    # ==========================================
    # 🔥 REGISTRA AUDITORIA
    # ==========================================
    alteracoes = []
    
    status_map = {'aberto': '🔴 Aberto', 'quitado': '✅ Quitado', 'recebido': '💰 Recebido'}
    
    if dados_antes[0] != descricao:
        alteracoes.append({'campo': 'descrição', 'antes': dados_antes[0], 'depois': descricao})
    
    if dados_antes[1] != valor:
        alteracoes.append({'campo': 'valor', 'antes': f'R$ {dados_antes[1]:.2f}', 'depois': f'R$ {valor:.2f}'})
    
    if dados_antes[2] != status:
        alteracoes.append({'campo': 'status', 'antes': status_map.get(dados_antes[2], dados_antes[2]), 'depois': status_map.get(status, status)})
    
    if alteracoes:
        AuditoriaFinanceiraService.registrar(
            transacao_id=sequencia,
            acao='editada',
            campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'],
            valor_antigo=json.dumps(alteracoes, ensure_ascii=False) if len(alteracoes) > 1 else alteracoes[0]['antes'],
            valor_novo=json.dumps(alteracoes, ensure_ascii=False) if len(alteracoes) > 1 else alteracoes[0]['depois']
        )

    conexao.close()

    flash('Transação atualizada com sucesso!', 'success')
    return redirect(url_for('financas.inifinancas'))