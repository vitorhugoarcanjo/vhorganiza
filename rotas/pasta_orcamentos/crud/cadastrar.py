import json  # ← ADICIONA NO TOPO
from flask import request, jsonify, session
from utils.database.conexao_global import ini_conexao

def criar_orcamento():
    """CRIA UM NOVO ORÇAMENTO"""
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
        
        # 🔥 CONVERTE PARA JSON ANTES DE ENVIAR
        estrutura_json = json.dumps(estrutura)  # ← ESSENCIAL!
        
        cursor.execute("""
            INSERT INTO orcamentos (usuario_id, titulo, cliente, status, estrutura)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            session['user_id'],
            titulo.strip(),
            cliente.strip() if cliente else None,
            status,
            estrutura_json  # ← USA O JSON CONVERTIDO
        ))
        
        orcamento_id = cursor.fetchone()[0]
        conexao.commit()
        
        return jsonify({
            'success': True,
            'message': f'Orçamento "{titulo}" criado com sucesso!',
            'type': 'sucesso',
            'id': orcamento_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar orçamento: {str(e)}',
            'type': 'erro'
        }), 500