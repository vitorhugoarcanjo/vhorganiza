# rotas/pasta_financas/crud/pasta_edit/services.py

# ==========================================================
# EDITAR TRANSAÇÃO - SERVICES
# ==========================================================

import json
import logging

logger = logging.getLogger(__name__)


class EditarTransacaoService:

    # ==========================================================
    # CATEGORIAS (pro <select> do modal)
    # ==========================================================
    @staticmethod
    def buscar_categorias(cursor, user_id):
        try:
            cursor.execute("""
                SELECT id, nome
                FROM categorias_financas
                WHERE user_id = %s
                ORDER BY nome ASC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao buscar categorias: {e}")
            return []

    # ==========================================================
    # BUSCAS BÁSICAS
    # ==========================================================
    @staticmethod
    def buscar_transacao_por_sequencia(cursor, sequencia, user_id):
        cursor.execute("""
            SELECT id, sequencia_transacoes, tipo, descricao, valor_total,
                   data_vencimento, categoria_id, status,
                   numero_parcela, total_parcelas, transacao_pai_id, data_emissao
            FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s
        """, (sequencia, user_id))
        return cursor.fetchone()

    @staticmethod
    def buscar_transacao_por_id(cursor, transacao_id, user_id):
        cursor.execute("""
            SELECT id, sequencia_transacoes, tipo, descricao, valor_total,
                   data_vencimento, categoria_id, status,
                   numero_parcela, total_parcelas, transacao_pai_id, data_emissao
            FROM transacoes
            WHERE id = %s AND user_id = %s
        """, (transacao_id, user_id))
        return cursor.fetchone()

    @staticmethod
    def get_pai_da_parcela(cursor, sequencia, user_id):
        """
        Recebe uma sequência (visual). Retorna:
          - se for filha: (transação_pai, id_do_pai)
          - se for simples/sem pai: (a própria transação, id_dela)
        """
        transacao = EditarTransacaoService.buscar_transacao_por_sequencia(cursor, sequencia, user_id)
        if not transacao:
            return None, None

        transacao_pai_id = transacao[10]

        if transacao_pai_id:
            pai = EditarTransacaoService.buscar_transacao_por_id(cursor, transacao_pai_id, user_id)
            return pai, transacao_pai_id

        return transacao, transacao[0]

    @staticmethod
    def buscar_parcelas_filhas(cursor, pai_id):
        cursor.execute("""
            SELECT id, sequencia_transacoes, numero_parcela, valor_parcela,
                   data_vencimento, status, descricao
            FROM transacoes
            WHERE transacao_pai_id = %s
            ORDER BY numero_parcela ASC
        """, (pai_id,))
        return cursor.fetchall()

    @staticmethod
    def formatar_transacao_para_modal(transacao_raw, parcelas_raw):
        lista_parcelas = []
        for p in parcelas_raw:
            lista_parcelas.append({
                'id': p[0],
                'sequencia': p[1],
                'numero_parcela': p[2],
                'valor': float(p[3]) if p[3] else 0.0,
                'vencimento': str(p[4]) if p[4] else '',
                'status': p[5],
                'descricao': p[6]
            })

        return {
            'parcelas': lista_parcelas,
            'parcelas_json': json.dumps(lista_parcelas, ensure_ascii=False)
        }

    # ==========================================================
    # ATUALIZAR TRANSAÇÃO
    # 🔥 A QUANTIDADE de parcelas é IMUTÁVEL
    # 🔥 Retorna dados_antes pra auditoria
    # ==========================================================
    @staticmethod
    def atualizar_transacao(cursor, conexao, sequencia_ou_id, user_id, dados):
        transacao_atual, pai_id_real = EditarTransacaoService.get_pai_da_parcela(
            cursor, sequencia_ou_id, user_id
        )
        if not transacao_atual:
            return {'success': False, 'error': 'Transação não encontrada'}

        tipo = transacao_atual[2]

        # 🔥 Dados ANTES (pra auditoria)
        dados_antes = {
            'tipo':             transacao_atual[2],
            'descricao':        transacao_atual[3],
            'valor_total':      float(transacao_atual[4]) if transacao_atual[4] else 0.0,
            'data_vencimento':  str(transacao_atual[5]) if transacao_atual[5] else '',
            'categoria_id':     transacao_atual[6],
            'status':           transacao_atual[7],
            'data_emissao':     str(transacao_atual[11]) if transacao_atual[11] else '',
        }

        # 🔥 Dados DEPOIS (do form)
        descricao = dados.get('descricao', '').strip()
        valor = float(dados.get('valor_total', 0.0))
        data_emissao = dados.get('data_emissao') or None
        data_vencimento = dados.get('data_vencimento') or None
        categoria_id = dados.get('categoria_id') or None

        dados_depois = {
            'tipo':             tipo,
            'descricao':        descricao,
            'valor_total':      valor,
            'data_vencimento':  data_vencimento,
            'categoria_id':     categoria_id,
            'status':           transacao_atual[7],
            'data_emissao':     data_emissao,
        }

        # Atualiza o PAI (ou a transação simples)
        cursor.execute("""
            UPDATE transacoes
            SET descricao = %s,
                valor_total = %s,
                data_emissao = %s,
                data_vencimento = %s,
                categoria_id = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (descricao, valor, data_emissao, data_vencimento, categoria_id,
              pai_id_real, user_id))

        # Se era parcelada, atualiza as filhas
        total_parcelas_antes = transacao_atual[9] or 1
        if total_parcelas_antes > 1:
            EditarTransacaoService._atualizar_filhas(
                cursor=cursor,
                pai_id=pai_id_real,
                descricao=descricao,
                tipo=tipo,
                parcelas_input=dados.get('parcelas', []),
                data_emissao=data_emissao,
                categoria_id=categoria_id,
            )

        return {
            'success': True,
            'id_interno': pai_id_real,     # 🆕 pro insert_transacao usar
            'dados_antes': dados_antes,    # 🆕
            'dados_depois': dados_depois,  # 🆕
        }

    # ==========================================================
    # ATUALIZAR FILHAS
    # 🔥 NÃO cria, NÃO deleta — a quantidade é imutável.
    # 🔥 FONTE DA VERDADE: dados['parcelas'] do front
    # ==========================================================
    @staticmethod
    def _atualizar_filhas(cursor, pai_id, descricao, tipo, parcelas_input, data_emissao, categoria_id):
        if not parcelas_input:
            return

        # Busca filhas ativas
        cursor.execute("""
            SELECT id, numero_parcela
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (pai_id,))
        existentes = cursor.fetchall()

        # Mapeia numero_parcela -> id
        mapa = {row[1]: row[0] for row in existentes}
        total = len(existentes)

        for p in parcelas_input:
            num = int(p.get('numero') or 0)
            if num not in mapa:
                continue   # segurança: ignora parcelas que não existem

            parcela_id = mapa[num]
            valor = float(p['valor'])
            vencimento = p['vencimento']

            cursor.execute("""
                UPDATE transacoes
                SET valor_total = %s,
                    valor_parcela = %s,
                    data_vencimento = %s,
                    descricao = %s,
                    categoria_id = %s,
                    data_emissao = %s,
                    total_parcelas = %s,
                    data_alteracao = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                valor,
                valor,
                vencimento,
                f'{descricao} ({num}/{total})',
                categoria_id,
                data_emissao,
                total,
                parcela_id
            ))