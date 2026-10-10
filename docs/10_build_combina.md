# 10 — Build / combina.py

## 10.1 O que é

`python scripts/combine_static_<modulo>.py` — concatena vários JS/CSS em 1 arquivo `.min.js`/`.min.css`.

**Motivo:** reduzir requisições HTTP.

## 10.2 Estrutura do `combine_static_<modulo>.py`

```python
import os
import re
from datetime import datetime

JS_FILES = [
    'static/js/components/botoes_filtros.js',   # compartilhado
    'static/js/modules/pasta_<modulo>/core/<X>Form.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-nova.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-editar.js',
    # ... ordem importa!
]

CSS_FILES = [
    'static/css/core/reset.css',
    'static/css/core/responsive.css',
    'static/css/components/buttons.css',
    'static/css/components/modal.css',
    # ...
]


def resolve_imports(content, file_path):
    """Resolve @import dentro de arquivos CSS."""
    pattern = r'@import\s+url\([\'"]?([^\'"]+)[\'"]?\);?'
    def replace_import(match):
        import_path = match.group(1)
        if import_path.startswith('/static/'):
            import_path = import_path[8:]
        elif import_path.startswith('static/'):
            import_path = import_path[7:]
        full_path = os.path.join('static', import_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
    return re.sub(pattern, replace_import, content, flags=re.IGNORECASE)


def combinar():
    with open('static/js/modules/pasta_<modulo>/<modulo>.min.js', 'w', encoding='utf-8') as out:
        out.write(f'// COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
        for file in JS_FILES:
            if os.path.exists(file):
                out.write(f'// ==== {os.path.basename(file)} ====\n')
                with open(file, 'r', encoding='utf-8') as f:
                    out.write(f.read())
                out.write('\n\n')

    with open('static/css/modules/pasta_<modulo>/<modulo>.min.css', 'w', encoding='utf-8') as out:
        out.write(f'/* COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")} */\n\n')
        for file in CSS_FILES:
            if os.path.exists(file):
                out.write(f'/* ===== {os.path.basename(file)} ===== */\n')
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = resolve_imports(content, file)
                    out.write(content)
                out.write('\n\n')


if __name__ == '__main__':
    combinar()
```

## 10.3 Regras

- ⚠️ **NUNCA misturar CSS no `JS_FILES`** nem JS no `CSS_FILES`
- ⚠️ **Ordem importa** — o `botoes_filtros.js` vem antes dos módulos
- ⚠️ **Rodar build DEPOIS de substituir o JS** — senão o bundle fica velho

## 10.4 Uso

```bash
python scripts/combine_static_orcamentos.py
```

**Saída esperada:**
```
COMBINANDO ARQUIVOS
==================
Combinando JS...
 ok botoes_filtros.js
 ok variaveis.js
 ok templates.js
 ...

Combinando CSS...
 ok modal.css
 ok form.css
 ...

ok PRONTO! Arquivos combinados:
static/js/modules/pasta_orcamentos/orcamento.min.js
static/css/modules/pasta_orcamentos/orcamento.min.css
```

**⚠️ Zero `⚠️ não encontrado`** — se aparecer, é caminho errado.

## 10.5 Cache busting

**No template:**
```jinja
<link rel="stylesheet" href="{{ static_v('css/modules/pasta_orcamentos/orcamento.min.css') }}">
<script src="{{ static_v('js/modules/pasta_orcamentos/orcamento.min.js') }}"></script>
```

**`static_v()`** gera hash do conteúdo (`?v=abc123`), forçando o navegador a baixar de novo quando muda.