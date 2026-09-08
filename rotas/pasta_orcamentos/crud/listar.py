from flask import render_template, session, jsonify
from rotas.middleware.permissoes import requer_master
from utils.database.conexao_global import ini_conexao

@requer_master
def listar_todos():
    try:
        conexao, cursor = ini_conexao()
        
        cursor.execute("""
            SELECT o.id, o.titulo, o.cliente, o.status, o.created_at, c.nome as criado_por
            FROM orcamentos o
            LEFT JOIN cadastre_se c ON o.usuario_id = c.id
            ORDER BY o.created_at DESC
        """)
        
        # 🔥 CONVERTE PARA DICIONÁRIO
        colunas = ['id', 'titulo', 'cliente', 'status', 'created_at', 'criado_por']
        orcamentos = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        return render_template(
            'pasta_orcamentos/tela_orcamentos.html.jinja',
            orcamentos=orcamentos,
            modo_admin=True
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar todos: {str(e)}',
            'type': 'erro'
        }), 500