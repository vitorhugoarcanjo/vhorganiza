from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json
import os, sqlite3
from datetime import date

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

bp_insert_transacao = Blueprint('nova_transacao', __name__)

def get_proxima_sequencia(cursor, user_id):
    """ Retorna a próxima sequência para o usuário """
    cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]

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

@bp_insert_transacao.route('/', methods=['GET', 'POST'])
@login_required
def initransacao():
    hoje = date.today().isoformat()
    user_id = session['user_id']

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    # carregar categorias
    cursor.execute("""
        SELECT id, nome FROM categorias_financas
        WHERE user_id = ?
    """, (user_id,))
    categorias = cursor.fetchall()

    if request.method == 'POST':
        try:
            tipo = request.form.get('tipo')
            valor_total = converter_valor_br(request.form.get('valor_total'))  # 🔥 CONVERTE
            descricao = request.form.get('descricao')
            data_emissao = request.form.get('data_emissao', hoje)
            data_vencimento = request.form.get('data_vencimento', hoje)
            categoria_id = request.form.get('categoria_id')

            parcelas_str = request.form.get('total_parcelas', '1')
            total_parcelas = int(parcelas_str) if parcelas_str else 1

            status = 'recebido' if tipo == 'receita' else 'aberto'

            sequencia = get_proxima_sequencia(cursor, user_id)

            cursor.execute("""
                INSERT INTO transacoes (
                    user_id, sequencia_transacoes, tipo,
                    valor_total, descricao,
                    data_emissao, data_vencimento,
                    total_parcelas, status, categoria_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, sequencia, tipo,
                valor_total, descricao,
                data_emissao, data_vencimento,
                total_parcelas, status, categoria_id
            ))

            conexao.commit()

            # ==========================================
            # 🔥 REGISTRA AUDITORIA (depois do commit)
            # ==========================================
            # Busca nome da categoria
            categoria_nome = ''
            if categoria_id:
                try:
                    c_cursor = conexao.cursor()
                    c_cursor.execute("SELECT nome FROM categorias_financas WHERE id = ?", (categoria_id,))
                    cat = c_cursor.fetchone()
                    if cat:
                        categoria_nome = cat[0]
                except:
                    pass
            
            # Cria lista de alterações
            alteracoes = [
                {'campo': 'tipo', 'antes': None, 'depois': '📈 Receita' if tipo == 'receita' else '📉 Despesa'},
                {'campo': 'descrição', 'antes': None, 'depois': descricao},
                {'campo': 'valor', 'antes': None, 'depois': f'R$ {valor_total:.2f}'},
                {'campo': 'data emissão', 'antes': None, 'depois': data_emissao},
            ]
            
            if data_vencimento:
                alteracoes.append({'campo': 'data vencimento', 'antes': None, 'depois': data_vencimento})
            
            if categoria_nome:
                alteracoes.append({'campo': 'categoria', 'antes': None, 'depois': categoria_nome})
            
            # Registra no banco
            AuditoriaFinanceiraService.registrar(
                transacao_id=sequencia,
                acao='criada',
                campo_alterado='todos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False)
            )

            conexao.close()

            flash('Transação cadastrada com sucesso!', 'success')
            return redirect(url_for('financas.inifinancas'))

        except Exception as e:
            conexao.close()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return redirect(url_for('nova_transacao.initransacao'))

    conexao.close()
    return render_template(
        'pasta_financas/crud/insert_transacao.html',
        hoje=hoje,
        categorias=categorias
    )