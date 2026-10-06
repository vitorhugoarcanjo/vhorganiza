# rotas/pasta_orcamentos/formatters.py
# ==========================================================
# FORMATADORES DO MÓDULO DE ORÇAMENTOS
# ==========================================================

import json
from utils.fomatacoes.data_reutilizavel import formatar_moeda_br, formatar_data_br


class OrcamentosFormatters:

    @staticmethod
    def formatar_lista(rows):
        """Recebe lista de tuplas do banco, devolve lista de dicts"""
        colunas = [
            'sequencia_orcamentos', 'id', 'numero', 'titulo', 'cliente',
            'status', 'valor_total', 'data_emissao', 'data_validade',
            'created_at', 'ativo'
        ]
        resultado = []
        for row in rows:
            d = dict(zip(colunas, row))
            d['valor_total_fmt'] = formatar_moeda_br(d.get('valor_total') or 0)
            d['data_emissao_fmt'] = formatar_data_br(d.get('data_emissao')) if d.get('data_emissao') else '-'
            d['data_validade_fmt'] = formatar_data_br(d.get('data_validade')) if d.get('data_validade') else '-'
            resultado.append(d)
        return resultado

    @staticmethod
    def formatar_detalhes(row):
        """Formata 1 orçamento pra JSON"""
        if not row:
            return None

        estrutura = row[6]
        if isinstance(estrutura, str):
            try:
                estrutura = json.loads(estrutura)
            except Exception:
                estrutura = []

        return {
            'id':                   row[0],
            'sequencia_orcamentos': row[1],
            'numero':               row[2] or '',
            'titulo':               row[3] or '',
            'cliente':              row[4] or '',
            'status':               row[5] or 'rascunho',
            'estrutura':            estrutura,
            'valor_total':          float(row[7] or 0),
            'data_emissao':         str(row[8]) if row[8] else '',
            'data_validade':        str(row[9]) if row[9] else '',
            'data_entrega':         str(row[10]) if row[10] else '',
            'descricao':            row[11] or '',
            'observacoes':          row[12] or '',
            'created_at':           row[13].strftime('%Y-%m-%d') if row[13] else '',
            'ativo':                row[14] if len(row) > 14 else 1,
        }

    @staticmethod
    def calcular_contadores(orcamentos):
        """Contadores pro footer"""
        return {
            'total':     len(orcamentos),
            'rascunho':  sum(1 for o in orcamentos if o.get('status') == 'rascunho'),
            'enviado':   sum(1 for o in orcamentos if o.get('status') == 'enviado'),
            'aprovado':  sum(1 for o in orcamentos if o.get('status') == 'aprovado'),
            'rejeitado': sum(1 for o in orcamentos if o.get('status') == 'rejeitado'),
        }