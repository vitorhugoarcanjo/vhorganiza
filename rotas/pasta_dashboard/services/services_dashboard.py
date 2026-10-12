# rotas/pasta_dashboard/services/services_dashboard.py
# ==========================================================
# SERVICES - DASHBOARD (padrão 2099)
# ==========================================================

import logging
from datetime import date, timedelta

from rotas.pasta_dashboard.queries import DashboardQueries
from rotas.pasta_dashboard.formatters import DashboardFormatters

logger = logging.getLogger(__name__)


# Mapa de meses em pt-BR
MESES_PT = {
    1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR',
    5: 'MAI', 6: 'JUN', 7: 'JUL', 8: 'AGO',
    9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ',
}


class DashboardServices:

    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    # ==========================================================
    # KPIs
    # ==========================================================
    def buscar_kpis(self, usuario_id, data_inicio, data_fim):
        # 1. Saldo do período
        self.cursor.execute(
            DashboardQueries.get_saldo_periodo(),
            (usuario_id, data_inicio, data_fim)
        )
        receitas, despesas = self.cursor.fetchone()

        # 2. A pagar (aberto)
        self.cursor.execute(
            DashboardQueries.get_a_pagar_periodo(),
            (usuario_id, data_inicio, data_fim)
        )
        a_pagar = self.cursor.fetchone()[0]

        # 3. A receber (aberto)
        self.cursor.execute(
            DashboardQueries.get_a_receber_periodo(),
            (usuario_id, data_inicio, data_fim)
        )
        a_receber = self.cursor.fetchone()[0]

        # 4. Período anterior (pra tendência)
        d_ini = date.fromisoformat(data_inicio)
        d_fim = date.fromisoformat(data_fim)
        dias = (d_fim - d_ini).days + 1
        ini_ant = d_ini - timedelta(days=dias)
        fim_ant = d_ini - timedelta(days=1)

        self.cursor.execute(
            DashboardQueries.get_saldo_periodo_anterior(),
            (usuario_id, ini_ant.isoformat(), fim_ant.isoformat())
        )
        rec_ant, desp_ant = self.cursor.fetchone()
        saldo_anterior = float(rec_ant or 0) - float(desp_ant or 0)

        return DashboardFormatters.formatar_kpis(
            receitas, despesas, a_pagar, a_receber, saldo_anterior
        )

    # ==========================================================
    # FLUXO MENSAL
    # ==========================================================
    def buscar_fluxo_mensal(self, usuario_id, meses=6):
        hoje = date.today()
        inicio = (hoje.replace(day=1) - timedelta(days=30 * meses)).replace(day=1)

        self.cursor.execute(
            DashboardQueries.get_fluxo_mensal(),
            (usuario_id, inicio.isoformat())
        )
        rows = self.cursor.fetchall()

        # Mapa {chave: {'receitas': ..., 'despesas': ...}}
        dados_por_mes = {r[0]: {'receitas': float(r[1]), 'despesas': float(r[2])} for r in rows}

        resultado = []
        mes_atual = inicio
        while mes_atual <= hoje:
            chave = mes_atual.strftime('%Y-%m')
            dados = dados_por_mes.get(chave, {'receitas': 0, 'despesas': 0})
            saldo = dados['receitas'] - dados['despesas']

            # 🔥 Mês em pt-BR
            nome_mes = MESES_PT.get(mes_atual.month, mes_atual.strftime('%b').upper())

            resultado.append({
                'mes_chave':      chave,
                'mes_nome':       nome_mes,
                'receitas':       dados['receitas'],
                'receitas_fmt':   f'R$ {dados["receitas"]:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                'despesas':       dados['despesas'],
                'despesas_fmt':   f'R$ {dados["despesas"]:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                'saldo':          saldo,
                'saldo_fmt':      f'R$ {saldo:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                'saldo_positivo': saldo >= 0,
            })

            # Avança mês
            if mes_atual.month == 12:
                mes_atual = mes_atual.replace(year=mes_atual.year + 1, month=1)
            else:
                mes_atual = mes_atual.replace(month=mes_atual.month + 1)

        # Alturas percentuais pro gráfico
        max_valor = max(
            (max(m['receitas'], m['despesas']) for m in resultado),
            default=1
        ) or 1

        for m in resultado:
            m['altura_receita_pct'] = (m['receitas'] / max_valor) * 100
            m['altura_despesa_pct'] = (m['despesas'] / max_valor) * 100

        return resultado

    # ==========================================================
    # TOP CATEGORIAS
    # ==========================================================
    def buscar_top_categorias(self, usuario_id, data_inicio, data_fim):
        self.cursor.execute(
            DashboardQueries.get_top_categorias(),
            (usuario_id, data_inicio, data_fim)
        )
        rows = self.cursor.fetchall()

        return DashboardFormatters.formatar_top_categorias(rows)

    # ==========================================================
    # ÚLTIMAS TRANSAÇÕES
    # ==========================================================
    def buscar_ultimas_transacoes(self, usuario_id, data_inicio, data_fim):
        self.cursor.execute(
            DashboardQueries.get_ultimas_transacoes(),
            (usuario_id, data_inicio, data_fim)
        )
        rows = self.cursor.fetchall()

        return DashboardFormatters.formatar_ultimas_transacoes(rows)