# rotas/pasta_orcamentos/crud/pasta_insert/cadastrar_orcamento.py
# ==========================================================
# CRIAR ORÇAMENTO
# ==========================================================

import json
import logging
from flask import request, jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

from rotas.pasta_orcamentos.queries import OrcamentosQueries

logger = logging.getLogger(__name__)


@login_required
def criar_orcamento():
    """CRIA UM NOVO ORÇAMENTO"""
    try:
        dados = request.get_json() or {}

        titulo = (dados.get('titulo') or '').strip()
        cliente = (dados.get('cliente') or '').strip() or None
        status = dados.get('status') or 'rascunho'
        estrutura = dados.get('estrutura') or []

        if not titulo:
            return jsonify({
                'success': False,
                'message': 'Título é obrigatório!',
                'type': 'erro'
            }), 400

        conexao, cursor = ini_conexao()

        cursor.execute(
            OrcamentosQueries.criar_orcamento(),
            (session['user_id'], titulo, cliente, status, json.dumps(estrutura))
        )

        orcamento_id = cursor.fetchone()[0]
        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Orçamento "{titulo}" criado com sucesso!',
            'type': 'sucesso',
            'id': orcamento_id
        })

    except Exception as e:
        logger.exception("Erro ao criar orçamento")
        return jsonify({
            'success': False,
            'message': f'Erro ao criar orçamento: {str(e)}',
            'type': 'erro'
        }), 500