from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br

class FinancasFormatters:
    """ FORMATACOES ESPECIFICAS DO MODULO FINANÇAS (REUTILIZADA FUNÇÕES GLOBAIS) """

    @staticmethod
    def formatar_transacoes(transacoes_raw):
        """ Formatar lista de transacoes para exibição """
        transacoes = []

        for t in transacoes_raw:
            transacao_lista = list(t)

            # formata parcela (mantem a logica original)
            numero_parcela = t[11] if len(t) > 11 else None
            total_parcelas = t[12] if len(t) > 12 else None

            if numero_parcela and total_parcelas and total_parcelas > 1:
                descricao_original = transacao_lista[4]
                transacao_lista[4] = f"{descricao_original}"

            # funções globais
            transacao_lista[3] = formatar_moeda_br(transacao_lista[3]) # valor total
            transacao_lista[5] = formatar_data_br(transacao_lista[5]) # data emissao
            transacao_lista[9] = formatar_data_br(transacao_lista[9]) # data vencimento

            transacoes.append(transacao_lista)

        return transacoes

    @staticmethod
    def formatar_detalhes(transacao):
        """ FORMATA DETALHES DE UMA TRANSAÇÃO PARA JSON """
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
            'parcela_label': f"{transacao[8]}/{transacao[9]}" if transacao[8] and transacao[9] else 'Á vista',
            'categoria': transacao[10] or 'Sem categoria',
            'categoria_cor': transacao[11] or '#6c757d'
        }