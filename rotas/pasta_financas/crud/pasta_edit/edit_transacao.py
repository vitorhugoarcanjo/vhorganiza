# ========================================================== #
# EDITAR TRANSAÇÃO - ROTAS (SEM BLUEPRINT)
# ========================================================== #

from flask import request, session, jsonify, render_template, redirect, url_for
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
import json
from datetime import date
from utils.database.conexao_global import ini_conexao
from .services import EditarTransacaoService
from .validacoes import validar_dados_edicao

def converter_valor_br(valor_str):
    if not valor_str:
        return 0.0
    valor_str = valor_str.replace('R$', '').strip()
    valor_str = valor_str.replace('.', '')
    valor_str = valor_str.replace(',', '.') 
    return float(valor_str)

@login_required
def editar_modal(sequencia):
    """Retorna o HTML do modal de edição"""
    user_id = session['user_id']
    hoje = date.today().isoformat()
    
    conexao, cursor = ini_conexao()
    
    transacao_raw = EditarTransacaoService.buscar_transacao(cursor, sequencia, user_id)
    if not transacao_raw:
        return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
    
    transacao_pai_id = transacao_raw[12]
    if transacao_pai_id:
        # 🔥 CORRIGIDO: financas.editar_modal
        return redirect(url_for('financas.editar_modal', sequencia=transacao_pai_id))
    
    parcelas_raw = EditarTransacaoService.buscar_parcelas(cursor, sequencia)
    dados = EditarTransacaoService.formatar_transacao_para_modal(transacao_raw, parcelas_raw)
    categorias = EditarTransacaoService.buscar_categorias(cursor, user_id)
    
    return render_template(
        'pasta_financas/modais/modal_editar_transacao.html.jinja',
        transacao=dados['transacao'],
        categorias=categorias,
        sequencia=sequencia,
        total_parcelas=dados['total_parcelas'],
        parcelas_filhas=dados['parcelas'],
        parcelas_filhas_json=dados['parcelas_json'],
        hoje=hoje
    )

@login_required
def dados_json(sequencia):
    """Retorna os dados da transação em JSON"""
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    
    transacao_raw = EditarTransacaoService.buscar_transacao(cursor, sequencia, user_id)
    if not transacao_raw:
        return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
    
    transacao_pai_id = transacao_raw[12]
    if transacao_pai_id:
        # 🔥 CORRIGIDO: financas.editar_modal
        return redirect(url_for('financas.editar_modal', sequencia=transacao_pai_id))
    
    parcelas_raw = EditarTransacaoService.buscar_parcelas(cursor, sequencia)
    
    return jsonify({
        'success': True,
        'data': {
            'sequencia': transacao_raw[0],
            'tipo': transacao_raw[2],
            'valor_total': float(transacao_raw[3]) if transacao_raw[3] else 0.0,
            'descricao': transacao_raw[4] or '',
            'data_emissao': transacao_raw[5].strftime('%Y-%m-%d') if transacao_raw[5] else '',
            'data_vencimento': transacao_raw[9].strftime('%Y-%m-%d') if transacao_raw[9] else '',
            'categoria_id': transacao_raw[6],
            'total_parcelas': transacao_raw[10] or 1,
            'intervalo_dias': transacao_raw[11] or 30,
            'parcelas': [
                {
                    'numero': p[1],
                    'data_vencimento': p[2].strftime('%Y-%m-%d') if p[2] else '',
                    'valor': float(p[3]) if p[3] else 0.0
                } for p in parcelas_raw
            ]
        }
    })

@login_required
def salvar_edicao(sequencia):
    """Salva a edição da transação"""
    user_id = session['user_id']
    
    try:
        dados = request.json or {}
        
        if dados.get('valor_total'):
            dados['valor_total'] = converter_valor_br(str(dados.get('valor_total')))
        else:
            dados['valor_total'] = 0.0
        
        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400
        
        conexao, cursor = ini_conexao()
        
        resultado = EditarTransacaoService.atualizar_transacao(
            cursor, conexao, sequencia, user_id, dados
        )
        
        if not resultado['success']:
            return jsonify({'success': False, 'error': resultado.get('error')}), 400
        
        auditoria = _registrar_auditoria(cursor, sequencia, resultado)
        conexao.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso!',
            'auditoria': auditoria
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def _registrar_auditoria(cursor, sequencia, resultado):
    try:
        dados_antes = resultado.get('dados_antes')
        if not dados_antes:
            return None
        
        alteracoes = []
        
        if dados_antes[0] != resultado.get('descricao'):
            alteracoes.append({'campo': 'descrição', 'antes': dados_antes[0], 'depois': resultado.get('descricao')})
        
        if dados_antes[1] != resultado.get('valor'):
            alteracoes.append({
                'campo': 'valor', 
                'antes': f'R$ {dados_antes[1]:.2f}', 
                'depois': f'R$ {resultado.get("valor"):.2f}'
            })
        
        if dados_antes[4] != resultado.get('categoria_id'):
            nome_antigo = dados_antes[5] or 'Sem categoria'
            nome_novo = 'Sem categoria'
            if resultado.get('categoria_id'):
                cursor.execute("SELECT nome FROM categorias_financas WHERE id = %s", (resultado.get('categoria_id'),))
                nova_categoria = cursor.fetchone()
                nome_novo = nova_categoria[0] if nova_categoria else 'Sem categoria'
            if nome_antigo != nome_novo:
                alteracoes.append({'campo': 'categoria', 'antes': nome_antigo, 'depois': nome_novo})
        
        if alteracoes:
            AuditoriaFinanceiraService.registrar(
                transacao_id=sequencia,
                acao='editada',
                campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'],
                valor_antigo=json.dumps(alteracoes, ensure_ascii=False, default=str),
                valor_novo=json.dumps(alteracoes, ensure_ascii=False, default=str)
            )
        
        return alteracoes
        
    except Exception as e:
        print(f"Erro na auditoria: {e}")
        return None