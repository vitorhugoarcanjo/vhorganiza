from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json
from utils.database.conexao_global import ini_conexao
from datetime import date, datetime, timedelta
from .validacoes.validacoes import validacao_campos_obrigatorios


bp_insert_transacao = Blueprint('nova_transacao', __name__)

def get_proxima_sequencia(cursor, user_id):
    """ Retorna a próxima sequência para o usuário """
    cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = %s", (user_id,))
    return cursor.fetchone()[0]

def converter_valor_br(valor_str):
    """Converte formato brasileiro '1.234,56' para float 1234.56"""
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.')
    return float(valor_str)

@bp_insert_transacao.route('/', methods=['GET', 'POST'])
@login_required
def initransacao():
    hoje = date.today().isoformat()
    user_id = session['user_id']

    conexao, cursor = ini_conexao()

    # carregar categorias
    cursor.execute("""
        SELECT id, nome FROM categorias_financas
        WHERE user_id = %s
    """, (user_id,))
    categorias = cursor.fetchall()

    if request.method == 'GET':
        return render_template(
            'pasta_financas/crud/insert_transacao.html',
            hoje=hoje,
            categorias=categorias
        )

    # ==========================================================
    # POST - Processa o formulário
    # ==========================================================
    if request.method == 'POST':
        try:
            tipo = request.form.get('tipo')
            valor_total = converter_valor_br(request.form.get('valor_total'))
            descricao = request.form.get('descricao')
            data_emissao = request.form.get('data_emissao', hoje)
            data_vencimento = request.form.get('data_vencimento')
            categoria_id = request.form.get('categoria_id') or None
            
            total_parcelas = int(request.form.get('total_parcelas', 1))

            erros = validacao_campos_obrigatorios(tipo)
            if erros:
                return jsonify({
                    'success': False,
                    'errors': erros
                }), 400

            # ==========================================================
            # PARCELA ÚNICA (total_parcelas <= 1)
            # ==========================================================
            if total_parcelas <= 1:
                # 🔥 CORRIGIDO: usa conexão global sem with
                sequencia = get_proxima_sequencia(cursor, user_id)
                
                cursor.execute("""
                    INSERT INTO transacoes (
                        user_id, sequencia_transacoes, tipo,
                        valor_total, descricao, categoria_id,
                        data_emissao, data_vencimento,
                        total_parcelas, numero_parcela, status, ativo
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
                """, (
                    user_id, sequencia, tipo,
                    valor_total, descricao, categoria_id,
                    data_emissao, data_vencimento,
                    1, 1
                ))
                conexao.commit()
                
                # Auditoria
                try:
                    AuditoriaFinanceiraService.registrar(
                        transacao_id=sequencia,
                        acao='criada',
                        campo_alterado='multiplos',
                        valor_antigo=None,
                        valor_novo=json.dumps([{'campo': 'transação', 'depois': descricao}], ensure_ascii=False)
                    )
                except Exception as audit_error:
                    print(f"Erro na auditoria: {audit_error}")
                
                return jsonify({
                    'success': True,
                    'message': f'Transação "{descricao}" cadastrada com sucesso!',
                    'sequencia': sequencia
                })
            
            # ==========================================================
            # MÚLTIPLAS PARCELAS (total_parcelas > 1)
            # ==========================================================
            intervalo_dias = int(request.form.get('intervaloDias', 30))
            primeiro_vencimento = request.form.get('primeiroVencimento', data_vencimento or hoje)
            
            # Coleta os valores de cada parcela
            valores_parcelas = []
            for i in range(1, total_parcelas + 1):
                valor_parcela = request.form.get(f'parcela_valor_{i}')
                if valor_parcela:
                    valores_parcelas.append(converter_valor_br(valor_parcela))
                else:
                    valores_parcelas.append(valor_total / total_parcelas)
            
            # 🔥 CORRIGIDO: usa conexão global sem with e sem caminho_banco
            # 1. Cria a transação PAI (registro principal)
            sequencia_pai = get_proxima_sequencia(cursor, user_id)
            
            cursor.execute("""
                INSERT INTO transacoes (
                    user_id, sequencia_transacoes, tipo,
                    valor_total, descricao, categoria_id,
                    data_emissao, data_vencimento,
                    total_parcelas, intervalo_dias, status, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
            """, (
                user_id, sequencia_pai, tipo,
                valor_total, descricao, categoria_id,
                data_emissao, primeiro_vencimento,
                total_parcelas, intervalo_dias
            ))
            
            # 2. Cria cada parcela filha
            for i in range(1, total_parcelas + 1):
                # Calcula a data de vencimento da parcela
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
                """, (
                    user_id, sequencia_parcela, tipo,
                    valor_parcela, valor_parcela, f'{descricao} - Parcela {i}/{total_parcelas}', categoria_id,
                    data_emissao, data_venc_parcela,
                    total_parcelas, i, i,
                    sequencia_pai
                ))
            
            conexao.commit()
            
            # Auditoria da transação principal
            try:
                AuditoriaFinanceiraService.registrar(
                    transacao_id=sequencia_pai,
                    acao='criada_parcelada',
                    campo_alterado='multiplos',
                    valor_antigo=None,
                    valor_novo=json.dumps({
                        'descricao': descricao,
                        'total_parcelas': total_parcelas,
                        'valor_total': valor_total,
                        'intervalo_dias': intervalo_dias
                    }, ensure_ascii=False)
                )
            except Exception as audit_error:
                print(f"Erro na auditoria: {audit_error}")
            
            return jsonify({
                'success': True,
                'message': f'Transação "{descricao}" cadastrada com {total_parcelas} parcelas!',
                'sequencia': sequencia_pai,
                'total_parcelas': total_parcelas
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Erro ao cadastrar: {str(e)}'})