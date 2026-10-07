# rotas/pasta_orcamentos/crud/pasta_edit/editar_orcamento.py
# ==========================================================
# EDITAR ORÇAMENTO — VIEW (padrão 2099)
# ==========================================================

import json
import logging
from flask import request, jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.auditoria_geral.pasta_orcamentos.services_auditoria import AuditoriaOrcamentosService

from .services import EditarOrcamentoService
from .validacoes import validar_dados_edicao
from rotas.pasta_orcamentos.crud.pasta_insert.validacoes import (
    limpar_texto,
    calcular_valor_total,
)

logger = logging.getLogger(__name__)


@login_required
def editar_orcamento(sequencia):
    """Edita orçamento pela sequência."""
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
        }

        # 2. Valida
        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({
                'success': False,
                'errors': erros,
                'message': 'Dados inválidos.'
            }), 400

        # 3. Atualiza
        conexao, cursor = ini_conexao()

        sucesso, resultado = EditarOrcamentoService.atualizar_orcamento(
            cursor, sequencia, user_id, dados
        )
        if not sucesso:
            conexao.rollback()
            return jsonify({
                'success': False,
                'message': resultado,
                'type': 'erro'
            }), 400

        # 4. Auditoria (só se mudou algo)
        alteracoes = EditarOrcamentoService.montar_alteracoes_auditoria(
            resultado.get('dados_antes', {}),
            resultado.get('dados_depois', {}),
        )

        if alteracoes:
            AuditoriaOrcamentosService.registrar(
                orcamento_id=resultado['id_interno'],
                acao='editada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': f'Orçamento "{dados["titulo"]}" atualizado com sucesso!',
            'type': 'sucesso',
            'sequencia': sequencia,
        }), 200

    except Exception as e:
        if conexao:
            conexao.rollback()
        logger.exception(f"Erro ao editar orçamento seq={sequencia} user_id={user_id}")
        return jsonify({
            'success': False,
            'message': f'Erro ao editar orçamento: {str(e)}',
            'type': 'erro'
        }), 500