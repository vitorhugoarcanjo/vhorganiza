# rotas/pasta_dashboard/services/services_dashboard.py
# ==========================================================
# SERVICES - DASHBOARD (padrão 2099)
# ==========================================================

import logging
from datetime import date, timedelta

from rotas.pasta_dashboard.queries import DashboardQueries
from rotas.pasta_dashboard.formatters import DashboardFormatters

logger = logging.getLogger(__name__)


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

        # Monta dict pra o formatter
        dados_por_mes = {r[0]: {'receitas': float(r[1]), 'despesas': float(r[2])} for r in rows}

        return DashboardFormatters.formatar_fluxo_mensal(dados_por_mes, inicio, hoje)

    # ==========================================================
    # TOP CATEGORIAS
    # ==========================================================
    def buscar_top_categorias(self, usuario_id, data_inicio, data_fim):
        # 1. Top 5 categorias
        self.cursor.execute(
            DashboardQueries.get_top_categorias(),
            (usuario_id, data_inicio, data_fim)
        )
        rows = self.cursor.fetchall()

        # 2. Total geral (todas as categorias)
        self.cursor.execute(
            DashboardQueries.get_total_despesas_periodo(),
            (usuario_id, data_inicio, data_fim)
        )
        total_geral = float(self.cursor.fetchone()[0] or 0)

        return DashboardFormatters.formatar_top_categorias(rows, total_geral)

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