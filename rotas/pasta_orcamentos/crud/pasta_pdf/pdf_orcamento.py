# rotas/pasta_orcamentos/crud/pasta_pdf/pdf_orcamento.py
# ==========================================================
# GERAR PDF DO ORÇAMENTO (WeasyPrint — padrão 2099)
# ==========================================================

import json
import logging
from datetime import datetime

from flask import session, render_template, make_response, jsonify
from weasyprint import HTML, CSS

from rotas.middleware.autenticacao import login_required
from utils.database.conexao_global import ini_conexao

logger = logging.getLogger(__name__)


@login_required
def gerar_pdf(sequencia):
    """GERA PDF DO ORÇAMENTO pela SEQUÊNCIA visual (WeasyPrint)."""
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

        # DICT (padrão 2099)
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

        # Variáveis padrão
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

        # 🔥 WEASYPRINT (em vez de pdfkit)
        # CSS extra pra configurar página (A4 + margens)
        css_page = CSS(string="""
            @page {
                size: A4;
                margin: 20mm;
            }
        """)

        pdf_bytes = HTML(string=html).write_pdf(stylesheets=[css_page])

        response = make_response(pdf_bytes)
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