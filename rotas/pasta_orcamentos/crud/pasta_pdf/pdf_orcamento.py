# rotas/pasta_orcamentos/crud/pasta_pdf/pdf_orcamento.py
# ==========================================================
# GERAR PDF DO ORÇAMENTO (padrão 2099)
# ==========================================================

import json
import logging
from datetime import datetime

from flask import session, render_template, make_response, jsonify
import pdfkit

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

logger = logging.getLogger(__name__)


@login_required
def gerar_pdf(sequencia):
    """GERA PDF DO ORÇAMENTO pela SEQUÊNCIA visual."""
    try:
        conexao, cursor = ini_conexao()

        # Busca por SEQUÊNCIA
        cursor.execute("""
            SELECT id, sequencia_orcamentos, numero,
                   titulo, cliente, status, estrutura,
                   valor_total, data_emissao, data_validade, data_entrega,
                   created_at
            FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s
        """, (sequencia, session['user_id']))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                'success': False,
                'message': 'Orçamento não encontrado!',
                'type': 'erro'
            }), 404

        # Processa estrutura
        estrutura = row[6]
        if isinstance(estrutura, str):
            try:
                estrutura = json.loads(estrutura)
            except Exception:
                estrutura = []
        if not isinstance(estrutura, list):
            estrutura = []

        # 🔥 DICT (padrão 2099 — mais legível)
        orcamento = {
            'id':            row[0],
            'sequencia':     row[1],
            'numero':        row[2] or '',
            'titulo':        row[3] or '',
            'cliente':       row[4] or '',
            'status':        row[5] or 'rascunho',
            'estrutura':     estrutura,
            'valor_total':   float(row[7] or 0),
            'data_emissao':  row[8],
            'data_validade': row[9],
            'data_entrega':  row[10],
            'created_at':    row[11],
        }

        # Variáveis padrão (futuro: buscar do user)
        variaveis = {
            'cor_primaria':    '#2563eb',
            'cor_secundaria':  '#8b5cf6',
            'cor_destaque':    '#10b981',
            'cor_alerta':      '#ef4444',
            'cor_texto':       '#1e293b',
            'cor_texto_claro': '#64748b',
            'cor_fundo':       '#ffffff',
            'cor_fundo_card':  '#f8fafc',
            'cor_borda':       '#e2e8f0',
            'fonte_corpo':     'Inter, sans-serif',
            'pdf_espacamento': 1.6,
            'moeda':           'R$',
        }

        html = render_template(
            'pasta_orcamentos/pdf/pdf_orcamento.html.jinja',
            orcamento=orcamento,
            now=datetime.now(),
            vars=variaveis,
        )

        options = {
            'page-size':                'A4',
            'margin-top':               '20mm',
            'margin-right':             '20mm',
            'margin-bottom':            '20mm',
            'margin-left':              '20mm',
            'encoding':                 'UTF-8',
            'enable-local-file-access': None,
        }

        try:
            pdf = pdfkit.from_string(html, False, options=options)
        except Exception:
            config = pdfkit.configuration(
                wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            )
            pdf = pdfkit.from_string(html, False, options=options, configuration=config)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=orcamento_{sequencia}.pdf'

        return response

    except Exception as e:
        logger.exception(f"Erro ao gerar PDF do orçamento seq={sequencia}")
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar PDF: {str(e)}',
            'type': 'erro'
        }), 500