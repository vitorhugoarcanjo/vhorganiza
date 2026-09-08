from flask import jsonify, session
from utils.database.conexao_global import ini_conexao

def get_dados_orcamento(id):
    """BUSCA DADOS DO ORÇAMENTO PARA O MODAL (VIA AJAX)"""
    try:
        conexao, cursor = ini_conexao()
        
        cursor.execute("""
            SELECT id, titulo, cliente, status, estrutura, created_at
            FROM orcamentos
            WHERE id = %s AND usuario_id = %s
        """, (id, session['user_id']))
        
        orcamento = cursor.fetchone()
        
        if not orcamento:
            return jsonify({
                'success': False,
                'message': 'Orçamento não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'id': orcamento[0],
            'titulo': orcamento[1],
            'cliente': orcamento[2] if orcamento[2] else '',
            'status': orcamento[3] if orcamento[3] else 'rascunho',
            'estrutura': orcamento[4] if orcamento[4] else [],
            'created_at': orcamento[5].strftime('%Y-%m-%d') if orcamento[5] else ''
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500