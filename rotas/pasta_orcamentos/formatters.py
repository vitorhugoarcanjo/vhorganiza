# rotas/pasta_orcamentos/formatters.py
# ==========================================================
# FORMATADORES DO MÓDULO DE ORÇAMENTOS
# ==========================================================

import json


class OrcamentosFormatters:

    @staticmethod
    def formatar_lista(rows):
        """Recebe lista de tuplas do banco, devolve lista de dicts"""
        colunas = ['id', 'titulo', 'cliente', 'status', 'created_at']
        return [dict(zip(colunas, row)) for row in rows]

    @staticmethod
    def formatar_lista_admin(rows):
        """Lista com JOIN (admin)"""
        colunas = ['id', 'titulo', 'cliente', 'status', 'created_at', 'criado_por']
        return [dict(zip(colunas, row)) for row in rows]

    @staticmethod
    def formatar_detalhes(row):
        """Formata 1 orçamento pra JSON"""
        if not row:
            return None

        estrutura = row[4]
        if isinstance(estrutura, str):
            try:
                estrutura = json.loads(estrutura)
            except Exception:
                estrutura = []

        return {
            'id':         row[0],
            'titulo':     row[1] or '',
            'cliente':    row[2] or '',
            'status':     row[3] or 'rascunho',
            'estrutura':  estrutura,
            'created_at': row[5].strftime('%Y-%m-%d') if row[5] else '',
        }

    @staticmethod
    def calcular_contadores(orcamentos):
        """Contadores pro footer"""
        return {
            'total':     len(orcamentos),
            'rascunho':  sum(1 for o in orcamentos if o['status'] == 'rascunho'),
            'enviado':   sum(1 for o in orcamentos if o['status'] == 'enviado'),
            'aprovado':  sum(1 for o in orcamentos if o['status'] == 'aprovado'),
            'rejeitado': sum(1 for o in orcamentos if o['status'] == 'rejeitado'),
        }