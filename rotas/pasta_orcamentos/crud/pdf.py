from flask import jsonify, session, render_template, make_response
from utils.database.conexao_global import ini_conexao
import pdfkit
import json
from datetime import datetime

def gerar_pdf(id):
    """GERA PDF DO ORÇAMENTO"""
    try:
        conexao, cursor = ini_conexao()
        
        cursor.execute("""
            SELECT id, usuario_id, titulo, cliente, status, estrutura, created_at 
            FROM orcamentos 
            WHERE id = %s
        """, (id,))
        
        orcamento = cursor.fetchone()
        
        if not orcamento:
            return jsonify({
                'success': False,
                'message': 'Orçamento não encontrado!',
                'type': 'erro'
            }), 404
        
        if orcamento[1] != session['user_id'] and session.get('is_master', 0) != 1:
            return jsonify({
                'success': False,
                'message': 'Sem permissão para gerar PDF!',
                'type': 'erro'
            }), 403
        
        estrutura = orcamento[5]
        if isinstance(estrutura, str):
            estrutura = json.loads(estrutura)
        
        orcamento_com_estrutura = (
            orcamento[0],
            orcamento[1],
            orcamento[2],
            orcamento[3],
            orcamento[4],
            orcamento[6],
            estrutura
        )
        
        # 🔥 CARREGA AS VARIÁVEIS DO USUÁRIO (se existirem)
        # Por enquanto, usa valores padrão
        variaveis = {
            'cor_primaria': '#2563eb',
            'cor_secundaria': '#8b5cf6',
            'cor_destaque': '#10b981',
            'cor_alerta': '#ef4444',
            'cor_texto': '#1e293b',
            'cor_texto_claro': '#64748b',
            'cor_fundo': '#ffffff',
            'cor_fundo_card': '#f8fafc',
            'cor_borda': '#e2e8f0',
            'fonte_corpo': 'Inter, sans-serif',
            'pdf_espacamento': 1.6,
            'moeda': 'R$'
        }
        
        html = render_template(
            'pasta_orcamentos/pdf/pdf_orcamento.html.jinja',
            orcamento=orcamento_com_estrutura,
            now=datetime.now(),
            vars=variaveis  # ← PASSA AS VARIÁVEIS PARA O TEMPLATE
        )
        
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'enable-local-file-access': None
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
        response.headers['Content-Disposition'] = f'inline; filename=orcamento_{id}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar PDF: {str(e)}',
            'type': 'erro'
        }), 500