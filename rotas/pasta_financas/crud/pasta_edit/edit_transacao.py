# rotas/pasta_financas/crud/pasta_edit/edit_transacao.py
# ==========================================================
# EDITAR TRANSAÇÃO - FUNÇÕES (view_funcs)
# ==========================================================

import logging
import json
from flask import request, session, jsonify, render_template
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from datetime import date, datetime
from utils.database.conexao_global import ini_conexao
from .services import EditarTransacaoService
from .validacoes import validar_dados_edicao, converter_valor_br

logger = logging.getLogger(__name__)


# ==========================================================
# HELPERS
# ==========================================================
def _formatar_data_iso(valor):
    if not valor:
        return ''
    if isinstance(valor, (date, datetime)):
        return valor.strftime('%Y-%m-%d')
    return str(valor)[:10]


def _fmt_moeda(v):
    try:
        return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return str(v)


def _fmt_data_br(data_iso):
    """YYYY-MM-DD → DD/MM/YYYY"""
    if not data_iso:
        return ''
    s = str(data_iso)[:10]
    if len(s) == 10 and s[4] == '-':
        return f'{s[8:10]}/{s[5:7]}/{s[0:4]}'
    return s


# ==========================================================
# DIFF — PAI
# ==========================================================
def _montar_diff(antes, depois):
    """Compara antes/depois do PAI e retorna lista de alterações."""
    mapa_campos = {
        'tipo':            'Tipo',
        'descricao':       'Descrição',
        'valor_total':     'Valor Total',
        'data_emissao':    'Data Emissão',
        'data_vencimento': 'Vencimento',
        'categoria_id':    'Categoria',
        'status':          'Status',
    }

    alteracoes = []
    for campo, label in mapa_campos.items():
        v_antes = antes.get(campo)
        v_depois = depois.get(campo)

        # Normaliza
        if campo == 'valor_total':
            v_antes = float(v_antes or 0)
            v_depois = float(v_depois or 0)
            if abs(v_antes - v_depois) > 0.001:
                alteracoes.append({
                    'campo': label,
                    'antes': _fmt_moeda(v_antes),
                    'depois': _fmt_moeda(v_depois),
                })
        else:
            v_antes_s = str(v_antes or '').strip()
            v_depois_s = str(v_depois or '').strip()
            if v_antes_s != v_depois_s:
                alteracoes.append({
                    'campo': label,
                    'antes': v_antes_s or '(vazio)',
                    'depois': v_depois_s or '(vazio)',
                })

    return alteracoes


# ==========================================================
# DIFF — FILHAS (parcelas)
# ==========================================================
def _montar_diff_filhas(parcelas_antes, parcelas_depois):
    """Compara cada filha (parcela) antes/depois."""
    alteracoes = []

    # Mapeia por número de parcela
    mapa_antes = {p['numero']: p for p in parcelas_antes}
    mapa_depois = {p['numero']: p for p in parcelas_depois}

    for num in sorted(set(mapa_antes.keys()) | set(mapa_depois.keys())):
        antes = mapa_antes.get(num)
        depois = mapa_depois.get(num)

        if not antes or not depois:
            continue

        # Valor
        v_antes = float(antes.get('valor') or 0)
        v_depois = float(depois.get('valor') or 0)
        if abs(v_antes - v_depois) > 0.001:
            alteracoes.append({
                'campo': f'Parcela {num} — Valor',
                'antes': _fmt_moeda(v_antes),
                'depois': _fmt_moeda(v_depois),
            })

        # Vencimento
        d_antes = str(antes.get('vencimento') or '').strip()
        d_depois = str(depois.get('vencimento') or '').strip()
        if d_antes != d_depois:
            alteracoes.append({
                'campo': f'Parcela {num} — Vencimento',
                'antes': _fmt_data_br(d_antes) or '(vazio)',
                'depois': _fmt_data_br(d_depois) or '(vazio)',
            })

    return alteracoes


# ==========================================================
# 1. GET — MODAL VAZIO
# ==========================================================
@login_required
def editar_modal(sequencia):
    usuario_id = session['user_id']
    hoje = date.today().isoformat()

    conexao, cursor = ini_conexao()
    try:
        categorias = EditarTransacaoService.buscar_categorias(cursor, usuario_id) \
                     if hasattr(EditarTransacaoService, 'buscar_categorias') else []

        return render_template(
            'pasta_financas/modais/modal_editar_transacao.html.jinja',
            categorias=categorias,
            sequencia=sequencia,
            hoje=hoje,
        )
    finally:
        conexao.close()


# ==========================================================
# 2. GET — DADOS JSON
# ==========================================================
@login_required
def dados_json(sequencia):
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        transacao, pai_id = EditarTransacaoService.get_pai_da_parcela(cursor, sequencia, usuario_id)
        if not transacao:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404

        parcelas_raw = EditarTransacaoService.buscar_parcelas_filhas(cursor, pai_id)

        return jsonify({
            'success': True,
            'data': {
                'id': transacao[0],
                'sequencia': sequencia,
                'tipo': transacao[2],
                'descricao': transacao[3] or '',
                'valor_total': float(transacao[4]) if transacao[4] else 0.0,
                'data_emissao': _formatar_data_iso(transacao[11]),
                'data_vencimento': _formatar_data_iso(transacao[5]),
                'categoria_id': transacao[6],
                'status': transacao[7],
                'numero_parcelas': transacao[8] or 1,
                'total_parcelas': transacao[9] or 1,
                'transacao_pai_id': transacao[10],
                'parcelas': [
                    {
                        'id': p[0],
                        'sequencia': p[1],
                        'numero_parcela': p[2],
                        'valor': float(p[3]) if p[3] else 0.0,
                        'data_vencimento': _formatar_data_iso(p[4]),
                        'status': p[5],
                        'descricao': p[6]
                    } for p in parcelas_raw
                ]
            }
        })
    finally:
        conexao.close()


# ==========================================================
# 3. POST — SALVAR (com DIFF PAI + FILHAS)
# ==========================================================
@login_required
def salvar_edicao(sequencia):
    usuario_id = session['user_id']
    conexao, cursor = ini_conexao()

    try:
        dados = request.json or {}

        valor = dados.get('valor_total')
        if isinstance(valor, (int, float)):
            dados['valor_total'] = float(valor)
        elif isinstance(valor, str) and valor.strip():
            dados['valor_total'] = converter_valor_br(valor)
        else:
            dados['valor_total'] = 0.0

        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 400

        resultado = EditarTransacaoService.atualizar_transacao(
            cursor, conexao, sequencia, usuario_id, dados
        )

        if not resultado.get('success'):
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado.get('error')}), 400

        # ==========================================================
        # AUDITORIA — PAI + FILHAS
        # ==========================================================
        id_interno = resultado.get('id_interno')
        dados_antes = resultado.get('dados_antes', {})
        dados_depois = resultado.get('dados_depois', {})
        parcelas_antes = resultado.get('parcelas_antes', [])
        parcelas_depois = resultado.get('parcelas_depois', [])

        # 1. Diff do PAI
        alteracoes = _montar_diff(dados_antes, dados_depois)

        # 2. Diff das FILHAS (se for parcelada)
        if parcelas_antes or parcelas_depois:
            alteracoes_filhas = _montar_diff_filhas(parcelas_antes, parcelas_depois)
            alteracoes.extend(alteracoes_filhas)

        # 3. Registra se houve alteração
        if alteracoes:
            AuditoriaFinanceiraService.registrar(
                transacao_id=id_interno,
                acao='editada',
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()

        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso!'
        })

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao salvar edição sequencia={sequencia} usuario_id={usuario_id}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()