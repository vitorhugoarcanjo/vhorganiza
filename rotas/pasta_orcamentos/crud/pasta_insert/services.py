# rotas/pasta_orcamentos/crud/pasta_insert/services.py
# ==========================================================
# INSERIR ORÇAMENTO - SERVICE
# ==========================================================

import json
import logging
from datetime import date, timedelta

from rotas.pasta_orcamentos.queries import OrcamentosQueries

logger = logging.getLogger(__name__)


class InserirOrcamentoService:

    # ==========================================================
    # SEQUÊNCIA VISUAL
    # ==========================================================
    @staticmethod
    def get_proxima_sequencia(cursor, user_id):
        """Retorna a próxima sequência visual pro usuário."""
        cursor.execute(
            OrcamentosQueries.get_proxima_sequencia(),
            (user_id,)
        )
        res = cursor.fetchone()
        return res[0] if res else 1

    # ==========================================================
    # NÚMERO FORMATADO (ORC-2026-0004)
    # ==========================================================
    @staticmethod
    def gerar_numero(sequencia, ano=None):
        """Gera 'ORC-{ano}-{seq 4 dígitos}'."""
        if ano is None:
            ano = date.today().year
        return f'ORC-{ano}-{str(sequencia).zfill(4)}'

    # ==========================================================
    # CRIAR ORÇAMENTO
    # ==========================================================
    @staticmethod
    def criar_orcamento(cursor, user_id, dados):
        """
        Insere um orçamento novo (com sequência, numero, datas, valor_total).
        Retorna (sucesso, resultado_ou_erro).
        """
        try:
            # 1. Sequência visual
            sequencia = InserirOrcamentoService.get_proxima_sequencia(cursor, user_id)

            # 2. Número formatado
            numero = InserirOrcamentoService.gerar_numero(sequencia)

            # 3. Datas
            hoje = date.today()
            data_emissao = dados.get('data_emissao') or hoje
            data_validade = dados.get('data_validade') or (hoje + timedelta(days=30))
            data_entrega = dados.get('data_entrega')  # opcional

            # 4. Valor total (já calculado na view)
            valor_total = dados.get('valor_total', 0.0)

            # 5. INSERT
            cursor.execute(
                OrcamentosQueries.criar_orcamento(),
                (
                    user_id,
                    sequencia,
                    numero,
                    dados['titulo'],
                    dados['cliente'],
                    dados.get('status', 'rascunho'),
                    json.dumps(dados.get('estrutura') or []),
                    valor_total,
                    data_emissao,
                    data_validade,
                    data_entrega,
                    dados.get('descricao') or None,
                    dados.get('observacoes') or None,
                )
            )

            row = cursor.fetchone()
            orcamento_id = row[0]
            sequencia_retornada = row[1]
            numero_retornado = row[2]

            return True, {
                'id': orcamento_id,
                'sequencia': sequencia_retornada,
                'numero': numero_retornado,
                'titulo': dados['titulo'],
                'valor_total': valor_total,
                'data_emissao': str(data_emissao),
                'data_validade': str(data_validade),
                'data_entrega': str(data_entrega) if data_entrega else None,
            }

        except KeyError as e:
            msg = f'Campo obrigatório ausente: {str(e)}'
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f'Erro ao inserir orçamento: {str(e)}'
            logger.error(msg)
            return False, msg

    # ==========================================================
    # AUDITORIA — montar alterações
    # ==========================================================
    @staticmethod
    def montar_alteracoes_auditoria(dados, resultado):
        """Monta a lista de alterações pra auditoria."""
        def _fmt_moeda(v):
            try:
                return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            except Exception:
                return str(v)

        alteracoes = [
            {'campo': 'Número',      'depois': resultado.get('numero', '-')},
            {'campo': 'Título',      'depois': dados['titulo']},
            {'campo': 'Cliente',     'depois': dados['cliente']},
            {'campo': 'Status',      'depois': dados.get('status', 'rascunho').title()},
            {'campo': 'Valor Total', 'depois': _fmt_moeda(resultado.get('valor_total', 0))},
            {'campo': 'Emissão',     'depois': resultado.get('data_emissao', '-')},
            {'campo': 'Validade',    'depois': resultado.get('data_validade', '-')},
        ]

        if resultado.get('data_entrega'):
            alteracoes.append({'campo': 'Entrega', 'depois': resultado['data_entrega']})

        if dados.get('descricao'):
            alteracoes.append({'campo': 'Descrição', 'depois': dados['descricao']})

        if dados.get('observacoes'):
            alteracoes.append({'campo': 'Observações', 'depois': dados['observacoes']})

        alteracoes.extend(_auditar_estrutura(dados.get('estrutura') or []))
        return alteracoes


# ==========================================================
# HELPER — auditoria da estrutura (blocos)
# ==========================================================
def _resumo_bloco(bloco):
    tipo = (bloco.get('tipo') or 'desconhecido').lower()
    titulo = (bloco.get('titulo') or '').strip()
    conteudo = (bloco.get('conteudo') or '').strip()

    if tipo == 'cabecalho':
        return titulo or conteudo or '(cabeçalho vazio)'
    if tipo == 'secao':
        return titulo or '(seção sem título)'
    if tipo == 'lista':
        itens = bloco.get('itens') or []
        qtd = len(itens) if isinstance(itens, list) else 0
        if titulo and qtd:
            return f'{titulo} ({qtd} item(ns))'
        return titulo or f'{qtd} item(ns)'
    if tipo == 'tabela':
        linhas = bloco.get('linhas') or []
        colunas = bloco.get('colunas') or []
        qtd_linhas = len(linhas) if isinstance(linhas, list) else 0
        qtd_colunas = len(colunas) if isinstance(colunas, list) else 0
        if titulo:
            return f'{titulo} ({qtd_linhas} linhas × {qtd_colunas} colunas)'
        return f'{qtd_linhas} linhas × {qtd_colunas} colunas'
    if tipo == 'valor':
        valor = (bloco.get('valor') or '').strip()
        if titulo and valor:
            return f'{titulo} — {valor}'
        return titulo or valor or '(valor vazio)'
    if tipo == 'observacao':
        if titulo and conteudo:
            return f'{titulo}: {conteudo[:60]}{"..." if len(conteudo) > 60 else ""}'
        return titulo or conteudo[:80] or '(observação vazia)'
    if tipo == 'destaque':
        cor = bloco.get('cor') or ''
        base = titulo or conteudo[:60] or '(destaque vazio)'
        return f'{base} [{cor}]' if cor else base
    if titulo:
        return titulo
    if conteudo:
        return conteudo[:80] + ('...' if len(conteudo) > 80 else '')
    return f'({tipo})'


def _auditar_estrutura(estrutura):
    alteracoes = []
    if not estrutura:
        alteracoes.append({'campo': '📋 Blocos do Orçamento', 'depois': '(vazio)'})
        return alteracoes

    alteracoes.append({
        'campo': '📋 Blocos do Orçamento',
        'depois': f'{len(estrutura)} bloco(s)'
    })

    for i, bloco in enumerate(estrutura, start=1):
        tipo = (bloco.get('tipo') or 'desconhecido').lower()
        resumo = _resumo_bloco(bloco)
        alteracoes.append({'campo': f'• Bloco {i} ({tipo})', 'depois': resumo})

    return alteracoes