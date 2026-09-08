from flask import request, jsonify, session
from utils.database.conexao_global import ini_conexao


def excluir_orcamento(id):
    """EXCLUI UM ORÇAMENTO"""
    try:
        conexao, cursor = ini_conexao()
        
        cursor.execute("SELECT usuario_id, titulo FROM orcamentos WHERE id = %s", (id,))
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
                'message': 'Sem permissão para excluir!',
                'type': 'erro'
            }), 403
        
        titulo = resultado[1]
        
        cursor.execute("DELETE FROM orcamentos WHERE id = %s", (id,))
        conexao.commit()
        
        return jsonify({
            'success': True,
            'message': f'Orçamento "{titulo}" excluído com sucesso!',
            'type': 'sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir orçamento: {str(e)}',
            'type': 'erro'
        }), 500