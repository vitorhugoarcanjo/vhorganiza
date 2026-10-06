# rotas/pasta_orcamentos/crud/pasta_insert/cadastrar_orcamento.py
# ==========================================================
# CRIAR ORÇAMENTO — VIEW (padrão 2099)
# ==========================================================

import json
import logging
from flask import request, jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.auditoria_geral.pasta_orcamentos.services_auditoria import AuditoriaOrcamentosService

from .services import InserirOrcamentoService
from .validacoes import (
    validar_dados_insercao,
    limpar_texto,
    calcular_valor_total,
)

logger = logging.getLogger(__name__)


@login_required
def criar_orcamento():
    """CRIA UM NOVO ORÇAMENTO"""
    user_id = session['user_id']
    conexao = None

    try:
        payload = request.get_json() or {}

        # 1. Sanitiza
        estrutura = payload.get('estrutura') or []

        dados = {
            'titulo':        limpar_texto(payload.get('titulo'), max_len=200),
            'cliente':       limpar_texto(payload.get('cliente'), max_len=200),
            'status':        (payload.get('status') or 'rascunho').strip().lower(),
            'estrutura':     estrutura,
            'valor_total':   calcular_valor_total(estrutura),
            'data_emissao':  payload.get('data_emissao') or None,
            'data_validade': payload.get('data_validade') or None,
            'data_entrega':  payload.get('data_entrega') or None,
            'descricao':     limpar_texto(payload.get('descricao')) or None,
            'observacoes':   limpar_texto(payload.get('observacoes')) or None,
        }

        # 2. Valida
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({
                'success': False,
                'errors': erros,
                'message': 'Dados inválidos.'
            }), 400

        # 3. Insere
        conexao, cursor = ini_conexao()

        sucesso, resultado = InserirOrcamentoService.criar_orcamento(cursor, user_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({
                'success': False,
                'message': resultado,
                'type': 'erro'
            }), 400

        # 4. Auditoria
        alteracoes = InserirOrcamentoService.montar_alteracoes_auditoria(dados, resultado)

        AuditoriaOrcamentosService.registrar(
            orcamento_id=resultado['id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Orçamento "{dados["titulo"]}" criado com sucesso!',
            'type': 'sucesso',
            'id': resultado['id'],
            'sequencia': resultado['sequencia'],
            'numero': resultado['numero'],
        }), 201

    except Exception as e:
        if conexao:
            conexao.rollback()
        logger.exception(f"Erro ao criar orçamento user_id={user_id}")
        return jsonify({
            'success': False,
            'message': f'Erro ao criar orçamento: {str(e)}',
            'type': 'erro'
        }), 500