# rotas/pasta_orcamentos/crud/pasta_edit/editar_orcamento.py
# ==========================================================
# SALVAR ESTRUTURA DO ORÇAMENTO
# ==========================================================

import json
import logging
from flask import request, jsonify, session
from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao
from rotas.auditoria_geral.pasta_orcamentos.services_auditoria import AuditoriaOrcamentosService

from rotas.pasta_orcamentos.queries import OrcamentosQueries

logger = logging.getLogger(__name__)


@login_required
def salvar_estrutura(id):
    """SALVA A ESTRUTURA COMPLETA DO ORÇAMENTO"""
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

        # Verifica permissão
        cursor.execute("""
            SELECT usuario_id, titulo, cliente, status
            FROM orcamentos WHERE id = %s
        """, (id,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({'success': False, 'message': 'Orçamento não encontrado!'}), 404

        if resultado[0] != session['user_id'] and session.get('is_master', 0) != 1:
            return jsonify({'success': False, 'message': 'Sem permissão!'}), 403

        # 🔥 Dados ANTES
        dados_antes = {
            'titulo':  resultado[1],
            'cliente': resultado[2] or '',
            'status':  resultado[3] or 'rascunho',
        }

        cursor.execute(
            OrcamentosQueries.atualizar_orcamento(),
            (titulo, cliente, status, json.dumps(estrutura), id)
        )

        # 🔥 Auditoria com DIFF
        alteracoes = []
        if dados_antes['titulo'] != titulo:
            alteracoes.append({'campo': 'Título',  'antes': dados_antes['titulo'],   'depois': titulo})
        if (dados_antes['cliente'] or '') != (cliente or ''):
            alteracoes.append({'campo': 'Cliente', 'antes': dados_antes['cliente'] or '(vazio)', 'depois': cliente or '(vazio)'})
        if dados_antes['status'] != status:
            alteracoes.append({'campo': 'Status',  'antes': dados_antes['status'],  'depois': status})

        if alteracoes:
            AuditoriaOrcamentosService.registrar(
                orcamento_id=id,
                acao='editada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': 'Orçamento salvo com sucesso!',
            'type': 'sucesso'
        })

    except Exception as e:
        logger.exception("Erro ao salvar orçamento")
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar: {str(e)}',
            'type': 'erro'
        }), 500