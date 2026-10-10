# 09 — PDF (WeasyPrint)

## 9.1 Por que WeasyPrint (não wkhtmltopdf)

| Critério | WeasyPrint | wkhtmltopdf |
|----------|------------|-------------|
| Linguagem | Python puro | C++ binário |
| Instalação | `pip install` + libs | binário + PATH |
| Status | Ativo | **Abandonado (2023)** |
| CSS | Moderno | Congelado (WebKit antigo) |
| Cross-platform | ✅ | ⚠️ Windows chato |

## 9.2 Instalação

### Windows

1. Baixar **GTK Runtime**: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Rodar o `.exe` e **MARCAR** `Set up PATH environment variable to include GTK+`
3. **REINICIAR O PC** (crítico)
4. `pip install weasyprint`

**Se der erro `cannot load library 'libgobject-2.0-0'`:** o GTK não tá no PATH.

### Linux (servidor)

```bash
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
                    libfontconfig1 libcairo2 libgdk-pixbuf-2.0-0
pip install weasyprint
```

## 9.3 View do PDF

```python
# rotas/pasta_<modulo>/crud/pasta_pdf/pdf_<x>.py
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
    """GERA PDF pela SEQUÊNCIA visual."""
    try:
        conexao, cursor = ini_conexao()

        cursor.execute("""
            SELECT id, sequencia_<modulo>, numero,
                   titulo, cliente, status, estrutura,
                   valor_total, data_emissao, data_validade, data_entrega,
                   created_at
            FROM <tabela>
            WHERE sequencia_<modulo> = %s AND usuario_id = %s
        """, (sequencia, session['user_id']))

        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Não encontrado!'}), 404

        # Processa estrutura (se JSONB)
        estrutura = row[6]
        if isinstance(estrutura, str):
            try: estrutura = json.loads(estrutura)
            except Exception: estrutura = []
        if not isinstance(estrutura, list):
            estrutura = []

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

        html = render_template(
            'pasta_<modulo>/pdf/pdf_<x>.html.jinja',
            orcamento=orcamento,
            now=datetime.now(),
        )

        # CSS de página (A4 + margens)
        css_page = CSS(string="""
            @page {
                size: A4;
                margin: 20mm;
            }
        """)

        pdf_bytes = HTML(string=html).write_pdf(stylesheets=[css_page])

        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=<x>_{sequencia}.pdf'
        return response

    except Exception as e:
        logger.exception(f"Erro ao gerar PDF seq={sequencia}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
```

## 9.4 Template do PDF

- **`@page`** cuida das margens (não precisa `padding` no body)
- **Flexbox** funciona (casos simples)
- **`position: fixed`** é **ignorado** (footer vira inline)
- **JavaScript** **não roda**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Orçamento {{ orcamento.numero }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; color: #333; }  /* sem padding */
        .header { text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }
        /* ... */
    </style>
</head>
<body>
    <!-- conteúdo -->
</body>
</html>
```

## 9.5 Botão na linha

```jinja
<!-- PDF -->
<a href="{{ url_for('<modulo>.pdf_<modulo>.gerar_pdf', sequencia=item.sequencia) }}"
   class="btn-acao check"
   target="_blank"
   title="Gerar PDF">
    <i class="bi bi-file-pdf"></i>
</a>
```

## 9.6 Armadilhas do WeasyPrint

| Problema | Sintoma | Solução |
|----------|---------|---------|
| Falta GTK no Windows | `cannot load library 'libgobject-2.0-0'` | Instalar GTK Runtime |
| Falta libs no Linux | `cannot load library 'libpango...'` | `apt install` |
| `position: fixed` | Footer ignora | Usar `@page` margins |
| JavaScript | Não roda | Evitar no PDF |
| `fontTools` warning | Aparece no log | Ignorar (não afeta) |
| `GLib-GIO-WARNING` (Windows) | Log gigante | Ignorar (é do Windows) |