# from flask import Blueprint, jsonify, session, request
# import sqlite3
# import os
# import json
# from rotas.middleware.autenticacao import login_required
# from utils.database.conexao_global import ini_conexao

# bp_colunas = Blueprint('api_colunas', __name__)


# def get_configuracao_padrao():
#     """Configuração padrão - TODAS colunas visíveis"""
#     return [
#         {'campo': 'SEQ', 'label': '📊 Sequência', 'visivel': True, 'largura': '65px', 'fixa': False, 'ajustavel': True},
#         {'campo': 'TIPO', 'label': '🏷️ Tipo', 'visivel': True, 'largura': '100px', 'fixa': True, 'ajustavel': False},
#         {'campo': 'VALOR', 'label': '💰 Valor', 'visivel': True, 'largura': '120px', 'fixa': True, 'ajustavel': False},
#         {'campo': 'DESCRICAO', 'label': '📝 Descrição', 'visivel': True, 'largura': 'auto', 'fixa': True, 'ajustavel': False},
#         {'campo': 'STATUS', 'label': '⚡ Status', 'visivel': True, 'largura': '110px', 'fixa': True, 'ajustavel': False},
#         {'campo': 'CATEGORIA', 'label': '📁 Categoria', 'visivel': True, 'largura': '130px', 'fixa': False, 'ajustavel': True},
#         {'campo': 'EMISSAO', 'label': '📅 Emissão', 'visivel': True, 'largura': '105px', 'fixa': False, 'ajustavel': True},
#         {'campo': 'VENCIMENTO', 'label': '⏰ Vencimento', 'visivel': True, 'largura': '105px', 'fixa': False, 'ajustavel': True},
#         {'campo': 'ACOES', 'label': '⚙️ Ações', 'visivel': True, 'largura': '145px', 'fixa': True, 'ajustavel': False}
#     ]


# @bp_colunas.route('/configurar-colunas', methods=['GET'])
# @login_required
# def get_config_colunas():
#     user_id = session.get('user_id')
    
#     conexao = ini_conexao()
#     cursor = conexao.cursor()
#     cursor.execute("""
#         SELECT configuracao FROM user_preferences
#         WHERE user_id = ? AND tabela = 'financas'
#     """, (user_id,))
#     resultado = cursor.fetchone()
    
#     if resultado:
#         try:
#             colunas = json.loads(resultado[0])
#             return jsonify({'success': True, 'colunas': colunas})
#         except:
#             return jsonify({'success': True, 'colunas': get_configuracao_padrao()})
#     else:
#         return jsonify({'success': True, 'colunas': get_configuracao_padrao()})


# @bp_colunas.route('/configurar-colunas', methods=['POST'])
# @login_required
# def save_config_colunas():
#     user_id = session.get('user_id')
#     data = request.get_json()
#     colunas = data.get('colunas', [])
    
#     if not colunas:
#         return jsonify({'success': False, 'error': 'Nenhuma configuração fornecida'}), 400
    
#     conexao = ini_conexao()
#     cursor = conexao.cursor()
#     cursor.execute("DELETE FROM user_preferences WHERE user_id = ? AND tabela = 'financas'", (user_id,))
#     cursor.execute("""
#         INSERT INTO user_preferences (user_id, tabela, configuracao)
#         VALUES (?, 'financas', ?)
#     """, (user_id, json.dumps(colunas)))
#     conexao.commit()
    
#     return jsonify({'success': True})