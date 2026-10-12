# rotas/pasta_dashboard/formatters.py
# ==========================================================
# FORMATTERS DO DASHBOARD (padrão 2099 — igual Finanças)
# ==========================================================

from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br


class DashboardFormatters:
    """ FORMATAÇÕES ESPECÍFICAS DO MÓDULO DASHBOARD """

    @staticmethod
    def formatar_kpis(receitas, despesas, a_pagar, a_receber, saldo_anterior):
        """ Formata os 4 KPIs + tendência """
        receitas = float(receitas or 0)
        despesas = float(despesas or 0)
        a_pagar  = float(a_pagar or 0)
        a_receber = float(a_receber or 0)
        saldo = receitas - despesas

        saldo_anterior = float(saldo_anterior or 0)

        if saldo_anterior != 0:
            tendencia = ((saldo - saldo_anterior) / abs(saldo_anterior)) * 100
        else:
            tendencia = 100 if saldo > 0 else 0

        return {
            'saldo':            saldo,
            'saldo_fmt':        formatar_moeda_br(saldo),
            'saldo_positivo':   saldo >= 0,
            'receitas':         receitas,
            'receitas_fmt':     formatar_moeda_br(receitas),
            'despesas':         despesas,
            'despesas_fmt':     formatar_moeda_br(despesas),
            'a_pagar':          a_pagar,
            'a_pagar_fmt':      formatar_moeda_br(a_pagar),
            'a_receber':        a_receber,
            'a_receber_fmt':    formatar_moeda_br(a_receber),
            'tendencia':        tendencia,
            'tendencia_fmt':    f"{tendencia:+.1f}%",
            'tendencia_up':     tendencia >= 0,
        }

    @staticmethod
    def formatar_fluxo_mensal(rows):
        """ Formata o fluxo mensal com alturas percentuais pro gráfico """
        from datetime import date

        dados_por_mes = {r[0]: {'receitas': float(r[1]), 'despesas': float(r[2])} for r in rows}

        hoje = date.today()
        # Início = 6 meses atrás
        inicio = (hoje.replace(day=1) - __import__('datetime').timedelta(days=30 * 6)).replace(day=1)

        resultado = []
        mes_atual = inicio
        while mes_atual <= hoje:
            chave = mes_atual.strftime('%Y-%m')
            dados = dados_por_mes.get(chave, {'receitas': 0, 'despesas': 0})
            saldo = dados['receitas'] - dados['despesas']
            nome_mes = mes_atual.strftime('%b').upper()

            resultado.append({
                'mes_chave':      chave,
                'mes_nome':       nome_mes,
                'receitas':       dados['receitas'],
                'receitas_fmt':   formatar_moeda_br(dados['receitas']),
                'despesas':       dados['despesas'],
                'despesas_fmt':   formatar_moeda_br(dados['despesas']),
                'saldo':          saldo,
                'saldo_fmt':      formatar_moeda_br(saldo),
                'saldo_positivo': saldo >= 0,
            })

            # Avança mês
            if mes_atual.month == 12:
                mes_atual = mes_atual.replace(year=mes_atual.year + 1, month=1)
            else:
                mes_atual = mes_atual.replace(month=mes_atual.month + 1)

        max_valor = max(
            (max(m['receitas'], m['despesas']) for m in resultado),
            default=1
        ) or 1

        for m in resultado:
            m['altura_receita_pct'] = (m['receitas'] / max_valor) * 100
            m['altura_despesa_pct'] = (m['despesas'] / max_valor) * 100

        return resultado

    @staticmethod
    def formatar_top_categorias(rows):
        """ Formata top categorias com percentual """
        total_geral = sum(float(r[2]) for r in rows) or 1

        resultado = []
        for r in rows:
            valor = float(r[2])
            resultado.append({
                'nome':           r[0],
                'cor':            r[1],
                'valor':          valor,
                'valor_fmt':      formatar_moeda_br(valor),
                'percentual':     (valor / total_geral) * 100,
                'percentual_fmt': f"{(valor / total_geral) * 100:.1f}%",
            })

        return {
            'categorias': resultado,
            'total':      total_geral,
            'total_fmt':  formatar_moeda_br(total_geral),
        }

    @staticmethod
    def formatar_ultimas_transacoes(rows):
        """ Formata últimas transações """
        transacoes = []
        for t in rows:
            valor = float(t[5]) if t[6] is not None else float(t[4] or 0)
            transacoes.append({
                'id':              t[0],
                'sequencia':       t[1],
                'tipo':            t[2],
                'tipo_label':      '📈 Receita' if t[2] == 'receita' else '📉 Despesa',
                'descricao':       t[3] or 'Sem descrição',
                'valor_raw':       valor,
                'valor_fmt':       formatar_moeda_br(valor),
                'status':          t[7],
                'status_label':    '✅ Quitado' if t[7] == 'quitado' else '🔴 Aberto',
                'data_emissao':    formatar_data_br(t[8]),
                'data_vencimento': formatar_data_br(t[9]),
                'data_quitamento': formatar_data_br(t[10]) if t[10] else 'Não quitado',
                'categoria_nome':  t[11],
                'categoria_cor':   t[12] or '#6c757d',
            })

        return transacoes