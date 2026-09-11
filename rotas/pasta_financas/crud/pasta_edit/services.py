# ==========================================================
# EDITAR TRANSAÇÃO - SERVICES
# ==========================================================

from datetime import datetime, date, timedelta
import json


class EditarTransacaoService:

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
            'total_parcelas': transacao_raw[9] or 1,   # 🔥 FIX: fallback p/ 1
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

    @staticmethod
    def atualizar_transacao(cursor, conexao, sequencia_ou_id, user_id, dados):
        # 🔥 FIX: usar get_pai_da_parcela pra resolver o PAI real (antes pegava id da filha)
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

        if total_parcelas > 1 or total_parcelas_antes > 1:
            EditarTransacaoService._gerenciar_parcelas(
                cursor, pai_id_real, user_id, tipo,
                descricao, valor, total_parcelas, total_parcelas_antes,
                dados.get('intervaloDias', 30),
                dados.get('primeiroVencimento', data_vencimento or data_emissao),
                dados.get('parcelas', []),
                data_emissao
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

    @staticmethod
    def _gerenciar_parcelas(cursor, pai_id, user_id, tipo, descricao, valor,
                            total_parcelas, total_parcelas_antes, intervalo_dias,
                            primeiro_vencimento, parcelas_input, data_emissao):

        cursor.execute("""
            SELECT id, sequencia_transacoes, numero_parcela, valor_total, data_vencimento
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (pai_id,))
        parcelas_existentes = cursor.fetchall()

        if total_parcelas > 1:
            if parcelas_input and len(parcelas_input) > 0:
                valores_parcelas = []
                for p in parcelas_input:
                    try:
                        val = float(p['valor'])
                    except (ValueError, TypeError):
                        val = valor / total_parcelas
                    valores_parcelas.append(val)
            else:
                valor_por_parcela = round(valor / total_parcelas, 2)
                valores_parcelas = [valor_por_parcela] * total_parcelas
                diferenca = round(valor - sum(valores_parcelas), 2)
                if diferenca != 0:
                    valores_parcelas[-1] = round(valores_parcelas[-1] + diferenca, 2)

            if len(parcelas_existentes) > total_parcelas:
                cursor.execute("""
                    UPDATE transacoes
                    SET ativo = 0, excluido_em = CURRENT_TIMESTAMP
                    WHERE transacao_pai_id = %s AND ativo = 1 AND numero_parcela > %s
                """, (pai_id, total_parcelas))

            if not primeiro_vencimento:
                primeiro_vencimento = datetime.now().strftime('%Y-%m-%d')
            elif isinstance(primeiro_vencimento, (datetime, date)):
                primeiro_vencimento = primeiro_vencimento.strftime('%Y-%m-%d')

            data_base = datetime.strptime(str(primeiro_vencimento)[:10], '%Y-%m-%d')

            for i in range(1, total_parcelas + 1):
                if i == 1:
                    data_venc_parcela = primeiro_vencimento
                else:
                    data_venc_parcela = (data_base + timedelta(days=(i - 1) * int(intervalo_dias or 30))).strftime('%Y-%m-%d')

                valor_parcela = valores_parcelas[i - 1] if i <= len(valores_parcelas) else (valor / total_parcelas)
                parcela_existente = next((p for p in parcelas_existentes if p[2] == i), None)

                if parcela_existente:
                    cursor.execute("""
                        UPDATE transacoes
                        SET valor_total = %s,
                            valor_parcela = %s,
                            data_vencimento = %s,
                            descricao = %s,
                            data_alteracao = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (valor_parcela, valor_parcela, data_venc_parcela,
                          f'{descricao} ({i}/{total_parcelas})', parcela_existente[0]))
                else:
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
                    """, (user_id, sequencia_parcela, tipo, valor_parcela, valor_parcela,
                          f'{descricao} ({i}/{total_parcelas})', None,
                          data_emissao, data_venc_parcela, total_parcelas, i, i, pai_id))

            cursor.execute("""
                UPDATE transacoes
                SET intervalo_dias = %s
                WHERE id = %s AND user_id = %s
            """, (intervalo_dias, pai_id, user_id))

        elif total_parcelas_antes > 1 and total_parcelas == 1:
            cursor.execute("""
                UPDATE transacoes
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP
                WHERE transacao_pai_id = %s AND ativo = 1
            """, (pai_id,))

    @staticmethod
    def _get_proxima_sequencia(cursor, user_id):
        cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = %s", (user_id,))
        return cursor.fetchone()[0]