from flask import render_template, session, jsonify
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

@login_required
def ini_orcamento():
    """TELA PRINCIPAL DE ORÇAMENTOS"""
    try:
        conexao, cursor = ini_conexao()
        
        cursor.execute("""
            SELECT id, titulo, cliente, status, created_at 
            FROM orcamentos 
            WHERE usuario_id = %s 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        
        colunas = ['id', 'titulo', 'cliente', 'status', 'created_at']
        orcamentos = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        return render_template(
            'pasta_orcamentos/tela_orcamentos.html.jinja',
            orcamentos=orcamentos
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar orçamentos: {str(e)}',
            'type': 'erro'
        }), 500