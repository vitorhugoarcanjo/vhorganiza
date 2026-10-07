# rotas/pasta_orcamentos/crud/pasta_edit/services.py
# ==========================================================
# EDITAR ORÇAMENTO - SERVICE
# ==========================================================

import json
import logging

from rotas.pasta_orcamentos.queries import OrcamentosQueries
from rotas.pasta_orcamentos.crud.pasta_insert.services import (
    _auditar_estrutura,
    _resumo_bloco,
)

logger = logging.getLogger(__name__)


class EditarOrcamentoService:

    # ==========================================================
    # BUSCAR ORÇAMENTO ATUAL (ANTES DA EDIÇÃO)
    # ==========================================================
    @staticmethod
    def buscar_orcamento(cursor, sequencia, user_id):
        """Busca orçamento pela sequência. Retorna (id_interno, dados) ou None."""
        cursor.execute("""
            SELECT id, titulo, cliente, status, estrutura,
                   valor_total, data_emissao, data_validade, data_entrega
            FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, user_id))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'id_interno':    row[0],
            'titulo':        row[1] or '',
            'cliente':       row[2] or '',
            'status':        row[3] or 'rascunho',
            'estrutura':     row[4] if row[4] else [],
            'valor_total':   float(row[5] or 0),
            'data_emissao':  str(row[6]) if row[6] else '',
            'data_validade': str(row[7]) if row[7] else '',
            'data_entrega':  str(row[8]) if row[8] else '',
        }

    # ==========================================================
    # ATUALIZAR ORÇAMENTO
    # ==========================================================
    @staticmethod
    def atualizar_orcamento(cursor, sequencia, user_id, dados):
        """
        Atualiza orçamento pela sequência.
        Retorna (sucesso, resultado_ou_erro).
        """
        try:
            # 1. Busca dados ANTES
            dados_antes = EditarOrcamentoService.buscar_orcamento(cursor, sequencia, user_id)
            if not dados_antes:
                return False, 'Orçamento não encontrado'

            id_interno = dados_antes['id_interno']

            # 2. UPDATE
            cursor.execute(
                OrcamentosQueries.atualizar_orcamento(),
                (
                    dados['titulo'],
                    dados['cliente'],
                    dados['status'],
                    json.dumps(dados.get('estrutura') or []),
                    dados.get('valor_total', 0.0),
                    dados.get('data_emissao') or None,
                    dados.get('data_validade') or None,
                    dados.get('data_entrega') or None,
                    sequencia,
                    user_id,
                )
            )

            # 3. Monta dados DEPOIS
            dados_depois = {
                'titulo':        dados['titulo'],
                'cliente':       dados['cliente'],
                'status':        dados['status'],
                'estrutura':     dados.get('estrutura') or [],
                'valor_total':   dados.get('valor_total', 0.0),
                'data_emissao':  dados.get('data_emissao') or '',
                'data_validade': dados.get('data_validade') or '',
                'data_entrega':  dados.get('data_entrega') or '',
            }

            return True, {
                'id_interno':   id_interno,
                'dados_antes':  dados_antes,
                'dados_depois': dados_depois,
            }

        except KeyError as e:
            msg = f'Campo obrigatório ausente: {str(e)}'
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f'Erro ao editar orçamento: {str(e)}'
            logger.error(msg)
            return False, msg

    # ==========================================================
    # AUDITORIA — montar alterações
    # ==========================================================
    @staticmethod
    def montar_alteracoes_auditoria(dados_antes, dados_depois):
        """
        Compara antes/depois e retorna lista de alterações.
        Inclui diff da estrutura (blocos).
        """
        def _fmt_moeda(v):
            try:
                return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            except Exception:
                return str(v)

        def _fmt_data_br(data_iso):
            if not data_iso:
                return '(vazio)'
            try:
                ano, mes, dia = str(data_iso)[:10].split('-')
                return f'{dia}/{mes}/{ano}'
            except Exception:
                return str(data_iso)

        mapa_campos = {
            'titulo':        ('Título',      None),
            'cliente':       ('Cliente',     None),
            'status':        ('Status',      None),
            'valor_total':   ('Valor Total', _fmt_moeda),
            'data_emissao':  ('Emissão',     _fmt_data_br),
            'data_validade': ('Validade',    _fmt_data_br),
            'data_entrega':  ('Entrega',     _fmt_data_br),
        }

        alteracoes = []
        for campo, (label, fmt) in mapa_campos.items():
            v_antes = dados_antes.get(campo)
            v_depois = dados_depois.get(campo)

            if fmt:
                v_antes = fmt(v_antes)
                v_depois = fmt(v_depois)

            v_antes_s = str(v_antes or '').strip()
            v_depois_s = str(v_depois or '').strip()

            if v_antes_s != v_depois_s:
                alteracoes.append({
                    'campo': label,
                    'antes': v_antes_s or '(vazio)',
                    'depois': v_depois_s or '(vazio)',
                })

        # 🔥 DIFF DA ESTRUTURA (blocos)
        alteracoes.extend(
            _auditar_estrutura_diff(
                dados_antes.get('estrutura') or [],
                dados_depois.get('estrutura') or [],
            )
        )

        return alteracoes


# ==========================================================
# HELPER — diff da estrutura (blocos)
# ==========================================================
def _auditar_estrutura_diff(estrutura_antes, estrutura_depois):
    """
    Compara duas estruturas (listas de blocos) e retorna diff.
    Estratégia: por índice. Se um bloco foi adicionado, removido ou alterado.
    """
    alteracoes = []

    qtd_antes = len(estrutura_antes)
    qtd_depois = len(estrutura_depois)

    # Resumo geral
    if qtd_antes != qtd_depois:
        alteracoes.append({
            'campo': '📋 Blocos do Orçamento',
            'antes': f'{qtd_antes} bloco(s)',
            'depois': f'{qtd_depois} bloco(s)',
        })

    # Diff por índice
    max_len = max(qtd_antes, qtd_depois)
    for i in range(max_len):
        antes = estrutura_antes[i] if i < qtd_antes else None
        depois = estrutura_depois[i] if i < qtd_depois else None

        if antes is None and depois is not None:
            # Bloco ADICIONADO
            tipo = (depois.get('tipo') or 'desconhecido').lower()
            alteracoes.append({
                'campo': f'• Bloco {i+1} ({tipo})',
                'antes': '(vazio)',
                'depois': _resumo_bloco(depois),
            })
        elif antes is not None and depois is None:
            # Bloco REMOVIDO
            tipo = (antes.get('tipo') or 'desconhecido').lower()
            alteracoes.append({
                'campo': f'• Bloco {i+1} ({tipo})',
                'antes': _resumo_bloco(antes),
                'depois': '(removido)',
            })
        elif antes is not None and depois is not None:
            # Bloco ALTERADO?
            resumo_antes = _resumo_bloco(antes)
            resumo_depois = _resumo_bloco(depois)

            if resumo_antes != resumo_depois:
                tipo = (depois.get('tipo') or 'desconhecido').lower()
                alteracoes.append({
                    'campo': f'• Bloco {i+1} ({tipo})',
                    'antes': resumo_antes,
                    'depois': resumo_depois,
                })

    return alteracoes