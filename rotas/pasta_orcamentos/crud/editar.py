import json  # ← ADICIONA NO TOPO
from flask import request, jsonify, session
from utils.database.conexao_global import ini_conexao

def salvar_estrutura(id):
    """SALVA A ESTRUTURA COMPLETA DO ORÇAMENTO (VIA AJAX)"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Dados inválidos!',
                'type': 'erro'
            }), 400
        
        titulo = dados.get('titulo')
        cliente = dados.get('cliente')
        status = dados.get('status', 'rascunho')
        estrutura = dados.get('estrutura', [])
        
        if not titulo:
            return jsonify({
                'success': False,
                'message': 'Título é obrigatório!',
                'type': 'erro'
            }), 400
        
        conexao, cursor = ini_conexao()
        
        # VERIFICA PERMISSÃO
        cursor.execute("SELECT usuario_id FROM orcamentos WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return jsonify({
                'success': False,
                'message': 'Orçamento não encontrado!',
                'type': 'erro'
            }), 404
        
        if resultado[0] != session['user_id'] and session.get('is_master', 0) != 1:
            return jsonify({
                'success': False,
                'message': 'Sem permissão para editar!',
                'type': 'erro'
            }), 403
        
        # 🔥 CONVERTE PARA JSON ANTES DE ENVIAR
        estrutura_json = json.dumps(estrutura)  # ← ESSENCIAL!
        
        # ATUALIZA
        cursor.execute("""
            UPDATE orcamentos 
            SET titulo = %s, cliente = %s, status = %s, estrutura = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (titulo, cliente, status, estrutura_json, id))
        
        conexao.commit()
        
        return jsonify({
            'success': True,
            'message': 'Orçamento salvo com sucesso!',
            'type': 'sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar: {str(e)}',
            'type': 'erro'
        }), 500