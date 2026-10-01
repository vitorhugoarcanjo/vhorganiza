# rotas/pasta_financas/crud/pasta_edit/services.py

# ==========================================================
# EDITAR TRANSAÇÃO - SERVICES
# ==========================================================

from datetime import datetime, date, timedelta
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
                   numero_parcela, total_parcelas, transacao_pai_id
            FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s
        """, (sequencia, user_id))
        return cursor.fetchone()

    @staticmethod
    def buscar_transacao_por_id(cursor, transacao_id, user_id):
        cursor.execute("""
            SELECT id, sequencia_transacoes, tipo, descricao, valor_total,
                   data_vencimento, categoria_id, status,
                   numero_parcela, total_parcelas, transacao_pai_id
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
            SELECT id, sequencia_transacoes, numero_parcela, valor_total,
                   data_vencimento, status, descricao
            FROM transacoes
            WHERE transacao_pai_id = %s
            ORDER BY numero_parcela ASC
        """, (pai_id,))
        return cursor.fetchall()

    # ==========================================================
    # SERIALIZAÇÃO PRO MODAL
    # ==========================================================
    @staticmethod
    def data_para_dicionario(transacao_raw):
        if not transacao_raw:
            return None
        return {
            'id': transacao_raw[0],
            'sequencia_transacoes': transacao_raw[1],
            'tipo': transacao_raw[2],
            'descricao': transacao_raw[3],
            'valor_total': transacao_raw[4],
            'data_vencimento': str(transacao_raw[5]) if transacao_raw[5] else '',
            'categoria_id': transacao_raw[6],
            'status': transacao_raw[7],
            'numero_parcelas': transacao_raw[8],
            'total_parcelas': transacao_raw[9] or 1,
            'transacao_pai_id': transacao_raw[10]
        }

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
    # ==========================================================
    @staticmethod
    def atualizar_transacao(cursor, conexao, sequencia_ou_id, user_id, dados):
        transacao_atual, pai_id_real = EditarTransacaoService.get_pai_da_parcela(
            cursor, sequencia_ou_id, user_id
        )
        if not transacao_atual:
            return {'success': False, 'error': 'Transação não encontrada'}

        tipo = transacao_atual[2]

        descricao = dados.get('descricao', '').strip()
        valor = float(dados.get('valor_total', 0.0))
        data_emissao = dados.get('data_emissao') or None
        data_vencimento = dados.get('data_vencimento') or None
        categoria_id = dados.get('categoria_id') or None
        total_parcelas = int(dados.get('total_parcelas', 1))

        dados_antes = (
            transacao_atual[4], transacao_atual[3], transacao_atual[5],
            transacao_atual[6], transacao_atual[7], transacao_atual[9]
        )
        total_parcelas_antes = transacao_atual[9] or 1

        # Atualiza o PAI (ou a transação simples)
        cursor.execute("""
            UPDATE transacoes
            SET descricao = %s,
                valor_total = %s,
                data_emissao = %s,
                data_vencimento = %s,
                categoria_id = %s,
                total_parcelas = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (descricao, valor, data_emissao, data_vencimento, categoria_id,
              total_parcelas, pai_id_real, user_id))

        # Se envolve parcelamento, gerencia as filhas
        if total_parcelas > 1 or total_parcelas_antes > 1:
            EditarTransacaoService._gerenciar_parcelas(
                cursor=cursor,
                pai_id=pai_id_real,
                user_id=user_id,
                tipo=tipo,
                descricao=descricao,
                valor=valor,
                total_parcelas=total_parcelas,
                total_parcelas_antes=total_parcelas_antes,
                intervalo_dias=dados.get('intervaloDias', 30),
                primeiro_vencimento=dados.get('primeiroVencimento') or data_vencimento or data_emissao,
                parcelas_input=dados.get('parcelas', []),
                data_emissao=data_emissao,
                categoria_id=categoria_id,
            )

        return {
            'success': True,
            'dados_antes': dados_antes,
            'descricao': descricao,
            'valor': valor,
            'data_emissao': data_emissao,
            'data_vencimento': data_vencimento,
            'categoria_id': categoria_id
        }

    # ==========================================================
    # GERENCIAR PARCELAS (criar/atualizar/remover filhas)
    # 🔥 FONTE DA VERDADE: dados.get('parcelas') do front
    # ==========================================================
    @staticmethod
    def _gerenciar_parcelas(cursor, pai_id, user_id, tipo, descricao, valor,
                            total_parcelas, total_parcelas_antes, intervalo_dias,
                            primeiro_vencimento, parcelas_input, data_emissao,
                            categoria_id):

        # Busca filhas ativas atuais
        cursor.execute("""
            SELECT id, sequencia_transacoes, numero_parcela, valor_total, data_vencimento
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (pai_id,))
        parcelas_existentes = cursor.fetchall()

        # ======================================================
        # CASO 1: continua parcelada (total > 1)
        # ======================================================
        if total_parcelas > 1:

            # 🔥 Monta a lista de parcelas finais — prioriza o FRONT
            parcelas_finais = []

            if parcelas_input and len(parcelas_input) == total_parcelas:
                # Fonte da verdade: front
                for i, p in enumerate(parcelas_input, start=1):
                    parcelas_finais.append({
                        'numero': i,
                        'valor': float(p['valor']),
                        'vencimento': p['vencimento'],
                    })
            else:
                # Fallback: recalcula (só se o front não mandou nada)
                valor_por_parcela = round(valor / total_parcelas, 2)
                valores = [valor_por_parcela] * total_parcelas
                dif = round(valor - sum(valores), 2)
                if dif != 0:
                    valores[-1] = round(valores[-1] + dif, 2)

                if not primeiro_vencimento:
                    primeiro_vencimento = datetime.now().strftime('%Y-%m-%d')
                elif isinstance(primeiro_vencimento, (datetime, date)):
                    primeiro_vencimento = primeiro_vencimento.strftime('%Y-%m-%d')

                data_base = datetime.strptime(str(primeiro_vencimento)[:10], '%Y-%m-%d')

                for i in range(1, total_parcelas + 1):
                    if i == 1:
                        data_venc = primeiro_vencimento
                    else:
                        data_venc = (data_base + timedelta(days=(i - 1) * int(intervalo_dias or 30))).strftime('%Y-%m-%d')

                    parcelas_finais.append({
                        'numero': i,
                        'valor': valores[i - 1],
                        'vencimento': data_venc,
                    })

            # Se o total DIMINUIU: desativa as filhas que sobraram
            if len(parcelas_existentes) > total_parcelas:
                cursor.execute("""
                    UPDATE transacoes
                    SET ativo = 0, excluido_em = CURRENT_TIMESTAMP
                    WHERE transacao_pai_id = %s AND ativo = 1 AND numero_parcela > %s
                """, (pai_id, total_parcelas))

            # Atualiza ou cria cada parcela
            for i, p in enumerate(parcelas_finais, start=1):
                valor_parcela = p['valor']
                data_venc_parcela = p['vencimento']

                parcela_existente = next((x for x in parcelas_existentes if x[2] == i), None)

                if parcela_existente:
                    # UPDATE com data/valor/categoria/emissão EXATOS
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
                        valor_parcela,
                        valor_parcela,
                        data_venc_parcela,
                        f'{descricao} ({i}/{total_parcelas})',
                        categoria_id,
                        data_emissao,
                        total_parcelas,
                        parcela_existente[0]
                    ))
                else:
                    # INSERT de parcela nova (total aumentou)
                    sequencia_parcela = EditarTransacaoService._get_proxima_sequencia(cursor, user_id)
                    cursor.execute("""
                        INSERT INTO transacoes (
                            user_id, sequencia_transacoes, tipo,
                            valor_total, valor_parcela, descricao, categoria_id,
                            data_emissao, data_vencimento,
                            total_parcelas, numero_parcela, sequencia_parcela,
                            transacao_pai_id, status, ativo
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
                    """, (
                        user_id,
                        sequencia_parcela,
                        tipo,
                        valor_parcela,
                        valor_parcela,
                        f'{descricao} ({i}/{total_parcelas})',
                        categoria_id,
                        data_emissao,
                        data_venc_parcela,
                        total_parcelas,
                        i,
                        i,
                        pai_id
                    ))

            # Atualiza o intervalo do PAI
            cursor.execute("""
                UPDATE transacoes
                SET intervalo_dias = %s
                WHERE id = %s AND user_id = %s
            """, (intervalo_dias, pai_id, user_id))

        # ======================================================
        # CASO 2: virou simples (era parcelada, virou 1 parcela)
        # ======================================================
        elif total_parcelas_antes > 1 and total_parcelas == 1:
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP
                WHERE transacao_pai_id = %s AND ativo = 1
            """, (pai_id,))

    # ==========================================================
    # HELPER: próxima sequência visual
    # ==========================================================
    @staticmethod
    def _get_proxima_sequencia(cursor, user_id):
        cursor.execute(
            "SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchone()[0]