# rotas/pasta_tela_pos_login/services/services.py
# ==========================================================
# SERVICES - TELA PÓS-LOGIN ("Meu Dia")
# ==========================================================

import logging
from datetime import date, timedelta

from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br
from rotas.pasta_tela_pos_login.queries import PosLoginQueries

logger = logging.getLogger(__name__)


class PosLoginServices:

    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor

    # ==========================================================
    # VENCENDO (atrasado + hoje)
    # ==========================================================
    def buscar_vencendo(self, usuario_id):
        """Retorna lista unificada (finanças + tarefas) de vencidos/hoje"""
        hoje = date.today()

        # 1. Finanças
        self.cursor.execute(PosLoginQueries.get_vencendo_financas(), (usuario_id, hoje))
        financas_raw = self.cursor.fetchall()

        # 2. Tarefas
        self.cursor.execute(PosLoginQueries.get_vencendo_tarefas(), (usuario_id, hoje))
        tarefas_raw = self.cursor.fetchall()

        itens = []

        # Formata finanças
        for t in financas_raw:
            valor_efetivo = float(t[4]) if t[5] is not None else float(t[3] or 0)
            dias_atraso = (hoje - t[8]).days if t[8] else 0
            itens.append({
                'tipo':        'financas',
                'id':          t[1],                # sequencia visual
                'id_interno':  t[0],
                'titulo':      t[2] or 'Sem descrição',
                'valor_raw':   valor_efetivo,
                'valor':       formatar_moeda_br(valor_efetivo),
                'data':        t[8],
                'data_br':     formatar_data_br(t[8]),
                'dias_atraso': dias_atraso,
                'urgente':     dias_atraso > 0,
                'categoria':   t[9],
                'cor':         t[10] or '#6c757d',
                'icone':       '💰',
                'modulo_nome': 'Finanças',
                'url_modulo':  'financas.ini_financas',
                'parcela':     (f"{t[6]}/{t[7]}" if t[6] and t[7] and t[7] > 1 else 'À vista'),
                'prioridade':  None,
            })

        # Formata tarefas
        prioridade_map = {'alta': 1, 'media': 2, 'baixa': 3}
        for t in tarefas_raw:
            dias_atraso = (hoje - t[5]).days if t[5] else 0
            itens.append({
                'tipo':        'tarefas',
                'id':          t[1],                # sequencia visual
                'id_interno':  t[0],
                'titulo':      t[2] or 'Sem título',
                'valor_raw':   None,
                'valor':       None,
                'data':        t[5],
                'data_br':     formatar_data_br(t[5]),
                'dias_atraso': dias_atraso,
                'urgente':     dias_atraso > 0,
                'categoria':   t[6],
                'cor':         t[7] or '#6c757d',
                'icone':       '📋',
                'modulo_nome': 'Tarefas',
                'url_modulo':  'tarefas.ini_tarefas',
                'parcela':     None,
                'prioridade':  t[4],
                'prioridade_ordem': prioridade_map.get(t[4], 4),
            })

        # Ordena: vencido primeiro, depois por data, depois por prioridade
        itens.sort(key=lambda x: (
            0 if x['urgente'] else 1,
            x['data'] or date(9999, 12, 31),
            x.get('prioridade_ordem', 4),
        ))

        return itens

    # ==========================================================
    # PRÓXIMOS 7 DIAS
    # ==========================================================
    def buscar_proximos(self, usuario_id):
        hoje = date.today()
        amanha = hoje + timedelta(days=1)
        limite = hoje + timedelta(days=7)

        # 1. Finanças
        self.cursor.execute(
            PosLoginQueries.get_proximos_financas(),
            (usuario_id, hoje, limite)
        )
        financas_raw = self.cursor.fetchall()

        # 2. Tarefas
        self.cursor.execute(
            PosLoginQueries.get_proximos_tarefas(),
            (usuario_id, hoje, limite)
        )
        tarefas_raw = self.cursor.fetchall()

        itens = []

        for t in financas_raw:
            valor_efetivo = float(t[4]) if t[5] is not None else float(t[3] or 0)
            itens.append({
                'tipo':        'financas',
                'id':          t[1],
                'titulo':      t[2] or 'Sem descrição',
                'valor':       formatar_moeda_br(valor_efetivo),
                'data':        t[8],
                'data_br':     formatar_data_br(t[8]),
                'categoria':   t[9],
                'cor':         t[10] or '#6c757d',
                'icone':       '💰',
                'modulo_nome': 'Finanças',
                'parcela':     (f"{t[6]}/{t[7]}" if t[6] and t[7] and t[7] > 1 else None),
                'prioridade':  None,
                'prioridade_ordem': 4,
            })

        prioridade_map = {'alta': 1, 'media': 2, 'baixa': 3}
        for t in tarefas_raw:
            itens.append({
                'tipo':        'tarefas',
                'id':          t[1],
                'titulo':      t[2] or 'Sem título',
                'valor':       None,
                'data':        t[5],
                'data_br':     formatar_data_br(t[5]),
                'categoria':   t[6],
                'cor':         t[7] or '#6c757d',
                'icone':       '📋',
                'modulo_nome': 'Tarefas',
                'parcela':     None,
                'prioridade':  t[4],
                'prioridade_ordem': prioridade_map.get(t[4], 4),
            })

        itens.sort(key=lambda x: (
            x['data'] or date(9999, 12, 31),
            x.get('prioridade_ordem', 4),
        ))

        return itens

    # ==========================================================
    # RESUMO RÁPIDO (KPIs do mês)
    # ==========================================================
    def buscar_resumo(self, usuario_id):
        hoje = date.today()
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = (primeiro_dia.replace(month=primeiro_dia.month % 12 + 1, day=1)
                      - timedelta(days=1)) if primeiro_dia.month < 12 else primeiro_dia.replace(year=primeiro_dia.year + 1, month=1, day=1) - timedelta(days=1)

        # 1. Saldo do mês (receitas - despesas quitadas)
        self.cursor.execute(
            PosLoginQueries.get_saldo_mes(),
            (usuario_id, primeiro_dia, ultimo_dia)
        )
        receitas, despesas = self.cursor.fetchone()
        saldo = float(receitas) - float(despesas)

        # 2. Total a pagar no mês (aberto)
        self.cursor.execute(
            PosLoginQueries.get_total_a_pagar_mes(),
            (usuario_id, primeiro_dia, ultimo_dia)
        )
        a_pagar = float(self.cursor.fetchone()[0] or 0)

        # 3. Tarefas pendentes
        self.cursor.execute(
            PosLoginQueries.get_contagem_tarefas_pendentes(),
            (usuario_id,)
        )
        tarefas_pendentes = self.cursor.fetchone()[0] or 0

        return {
            'saldo':              saldo,
            'saldo_fmt':          formatar_moeda_br(saldo),
            'saldo_positivo':     saldo >= 0,
            'tarefas_pendentes':  tarefas_pendentes,
            'a_pagar':            a_pagar,
            'a_pagar_fmt':        formatar_moeda_br(a_pagar),
            'mes_nome':           primeiro_dia.strftime('%B/%Y').capitalize(),
            # Orçamentos: placeholder por enquanto
            'orcamentos_ativos':  0,
        }