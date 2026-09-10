from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br

class FinancasFormatters:
    """ FORMATACOES ESPECIFICAS DO MODULO FINANÇAS (REUTILIZA FUNÇÕES GLOBAIS) """

    @staticmethod
    def formatar_transacoes(transacoes_raw):
        """ Formata a lista de transações brutas em DICIONÁRIOS para o Jinja/HTML """
        transacoes = []

        for t in transacoes_raw:
            # Pega as parcelas se existirem na tupla
            numero_parcela = t[11] if len(t) > 11 else None
            total_parcelas = t[12] if len(t) > 12 else None

            # Preserva o valor numérico (float) para cálculos de soma/totais no backend
            valor_bruto = float(t[3]) if t[3] is not None else 0.0

            transacao_dict = {
                "sequencia_transacoes": t[0],
                "id": t[1],
                "tipo": t[2],
                "valor_raw": valor_bruto,                            # Para somas no Python
                "valor": formatar_moeda_br(t[3]),                    # Ex: "R$ 150,00" para exibição
                "descricao": t[4] or 'Sem descrição',
                "data_emissao": formatar_data_br(t[5]),
                "categoria_nome": t[6],
                "categoria_cor": t[7] or '#6c757d',
                "status": t[8],
                "data_vencimento": formatar_data_br(t[9]),
                "ativo": t[10],
                "numero_parcela": numero_parcela,
                "total_parcelas": total_parcelas,
                "transacao_pai_id": t[13] if len(t) > 13 else None,
                
                # Rótulo amigável para parcelas
                "parcela_label": f"{numero_parcela}/{total_parcelas}" if numero_parcela and total_parcelas and total_parcelas > 1 else 'À vista'
            }

            transacoes.append(transacao_dict)

        return transacoes

    @staticmethod
    def formatar_detalhes(transacao):
        """ FORMATA DETALHES DE UMA TRANSAÇÃO PARA JSON (MANTIDO PERFEITO COMO JÁ ESTAVA) """
        if not transacao:
            return None
        
        return {
            'sequencia_transacoes': transacao[0],
            'tipo': transacao[1],
            'tipo_label': '📈 Receita' if transacao[1] == 'receita' else '📉 Despesa',
            'valor': formatar_moeda_br(transacao[2]),
            'descricao': transacao[3] or 'Sem descrição',
            'data_emissao': formatar_data_br(transacao[4]),
            'data_vencimento': formatar_data_br(transacao[5]),
            'data_quitamento': formatar_data_br(transacao[6]) if transacao[6] else 'Não quitado',
            'status': transacao[7],
            'status_label': '🔴 Aberto' if transacao[7] == 'aberto' else '✅ Quitado' if transacao[7] == 'quitado' else '💰 Recebido',
            'numero_parcela': transacao[8],
            'total_parcelas': transacao[9],
            'parcela_label': f"{transacao[8]}/{transacao[9]}" if transacao[8] and transacao[9] else 'À vista',
            'categoria': transacao[10] or 'Sem categoria',
            'categoria_cor': transacao[11] or '#6c757d'
        }