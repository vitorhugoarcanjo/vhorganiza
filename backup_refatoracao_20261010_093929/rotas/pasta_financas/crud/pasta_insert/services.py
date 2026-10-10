# rotas/pasta_financas/crud/pasta_insert/services.py
# ==========================================================
# INSERIR TRANSAÇÃO - SERVICES (PostgreSQL)
# ==========================================================

from datetime import datetime, timedelta
import logging

from utils.fomatacoes.data_reutilizavel import obter_hoje_cuiaba

logger = logging.getLogger(__name__)


class InserirTransacaoService:

    @staticmethod
    def get_proxima_sequencia(cursor, user_id):
        """Retorna a próxima sequência de transações para o usuário."""
        cursor.execute("""
            SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1
            FROM transacoes
            WHERE user_id = %s
        """, (user_id,))
        res = cursor.fetchone()
        return res[0] if res else 1

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
            logger.error(f"Erro ao buscar categorias do usuário {user_id}: {str(e)}")
            return []

    @staticmethod
    def criar_transacao_simples(cursor, user_id, dados):
        """Cria uma transação única/à vista (1/1 parcela)."""
        try:
            sequencia = InserirTransacaoService.get_proxima_sequencia(cursor, user_id)
            valor_total = float(dados['valor_total'])

            hoje_cuiaba = obter_hoje_cuiaba()
            data_emissao = dados.get('data_emissao') or hoje_cuiaba
            data_vencimento = dados.get('data_vencimento') or data_emissao

            cursor.execute("""
                INSERT INTO transacoes (
                    user_id, sequencia_transacoes, tipo,
                    valor_total, valor_parcela, descricao, categoria_id,
                    data_emissao, data_vencimento,
                    total_parcelas, numero_parcela, transacao_pai_id, status, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1, NULL, 'aberto', 1)
                RETURNING id
            """, (
                user_id,
                sequencia,
                dados['tipo'],
                valor_total,
                valor_total,
                dados['descricao'],
                dados['categoria_id'],
                data_emissao,
                data_vencimento
            ))

            transacao_id = cursor.fetchone()[0]

            return True, {
                "transacao_id": transacao_id,
                "sequencia": sequencia,
                "total_parcelas": 1,
                "mensagem": "Transação simples registrada com sucesso!"
            }

        except KeyError as e:
            msg = f"Campo obrigatório ausente: {str(e)}"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Erro ao inserir transação simples: {str(e)}"
            logger.error(msg)
            return False, msg

    @staticmethod
    def criar_transacao_parcelada(cursor, user_id, dados):
        """Cria uma transação PAI + N FILHAS."""
        try:
            total_parcelas = int(dados['total_parcelas'])
            if total_parcelas < 1:
                return False, "O número de parcelas deve ser maior ou igual a 1."

            intervalo_dias = int(dados.get('intervalo_dias') or 30)
            hoje_cuiaba = obter_hoje_cuiaba()

            data_emissao = dados.get('data_emissao') or hoje_cuiaba
            valor_total = float(dados['valor_total'])

            parcelas_input = dados.get('parcelas') or []

            if not parcelas_input or len(parcelas_input) != total_parcelas:
                primeiro_vencimento = (
                    dados.get('primeiro_vencimento')
                    or dados.get('primeiroVencimento')
                    or dados.get('data_vencimento')
                    or data_emissao
                )
                data_base = datetime.strptime(primeiro_vencimento, '%Y-%m-%d')

                valor_por_parcela = round(valor_total / total_parcelas, 2)
                valores_parcelas = [valor_por_parcela] * total_parcelas
                diferenca = round(valor_total - sum(valores_parcelas), 2)
                if diferenca != 0:
                    valores_parcelas[-1] = round(valores_parcelas[-1] + diferenca, 2)

                parcelas_input = []
                for i in range(1, total_parcelas + 1):
                    if i == 1:
                        data_venc = primeiro_vencimento
                    else:
                        data_venc = (data_base + timedelta(days=(i - 1) * intervalo_dias)).strftime('%Y-%m-%d')
                    parcelas_input.append({
                        'numero': i,
                        'valor': valores_parcelas[i - 1],
                        'vencimento': data_venc,
                    })

            # 1. PAI
            cursor.execute("""
                INSERT INTO transacoes (
                    user_id, sequencia_transacoes, tipo,
                    valor_total, descricao, categoria_id,
                    data_emissao, data_vencimento,
                    total_parcelas, intervalo_dias, transacao_pai_id, status, ativo
                )
                VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, NULL, 'aberto', 1)
                RETURNING id
            """, (
                user_id,
                dados['tipo'],
                valor_total,
                dados['descricao'],
                dados['categoria_id'],
                data_emissao,
                parcelas_input[0]['vencimento'],
                total_parcelas,
                intervalo_dias
            ))

            pai_id = cursor.fetchone()[0]

            # 2. FILHAS
            for i, p in enumerate(parcelas_input, start=1):
                sequencia_parcela = InserirTransacaoService.get_proxima_sequencia(cursor, user_id)
                valor_parcela = float(p['valor'])
                data_venc_parcela = p['vencimento']

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
                    dados['tipo'],
                    valor_total,
                    valor_parcela,
                    f"{dados['descricao']} ({i}/{total_parcelas})",
                    dados['categoria_id'],
                    data_emissao,
                    data_venc_parcela,
                    total_parcelas,
                    i,
                    i,
                    pai_id
                ))

            return True, {
                "pai_id": pai_id,
                "total_parcelas": total_parcelas,
                "mensagem": f"Transação parcelada em {total_parcelas}x registrada com sucesso!"
            }

        except Exception as e:
            msg = f"Erro inesperado ao criar parcelas: {str(e)}"
            logger.error(msg)
            return False, msg