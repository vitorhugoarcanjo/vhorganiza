# 02 — Estrutura de Pastas

## 2.1 Backend — `rotas/pasta_<modulo>/`

```
rotas/pasta_<modulo>/
├── __init__.py                 # Blueprint principal + register_blueprint dos CRUDs
├── <modulo>.py                 # Rotas principais (listagem, detalhes, limpar_filtros)
├── queries.py                  # SQL puro
├── filters.py                  # Filtros (session, query string)
├── formatters.py               # Serialização/dicionários
├── services/
│   └── services_<modulo>.py    # Service principal
└── crud/
    ├── pasta_insert/
    │   ├── __init__.py         # bp_insert + add_url_rule
    │   ├── insert_<x>.py       # View MAGRA — AUDITORIA AQUI
    │   ├── services.py         # INSERT + regras (sequência, numero, valor_total)
    │   └── validacoes.py       # Validações + helpers
    ├── pasta_edit/
    │   ├── __init__.py
    │   ├── edit_<x>.py         # View + _montar_diff
    │   ├── services.py         # UPDATE + retorna dados_antes/dados_depois
    │   └── validacoes.py
    ├── pasta_delete/
    │   ├── __init__.py
    │   ├── delete_<x>.py       # View — AUDITORIA aqui
    │   └── services.py
    ├── pasta_pdf/              # Se o módulo tiver PDF
    │   ├── __init__.py
    │   └── pdf_<x>.py          # View — WeasyPrint
    └── pasta_<acao>/           # quitar/concluir, estornar/reabrir, reativar
        ├── __init__.py
        ├── <acao>_<x>.py
        └── services.py
```

## 2.2 Templates — `templates/pasta_<modulo>/`

```
templates/pasta_<modulo>/
├── tela_<modulo>.html.jinja
├── _tabela_<modulo>.html.jinja
├── modais/
│   ├── modal_nova_<x>.html.jinja
│   ├── modal_editar_<x>.html.jinja
│   └── excluir_<x>.html
├── pdf/
│   └── pdf_<x>.html.jinja
└── partials/
    ├── _tbody_<modulo>.html.jinja
    ├── _linha_<modulo>.html.jinja
    └── form_<x>.html.jinja

templates/pasta_auditoria/pasta_<modulo>/
└── modal_auditoria.html.jinja
```

## 2.3 Frontend — `static/js/`

```
static/js/
├── components/                    # COMPARTILHADO
│   └── botoes_filtros.js
└── modules/pasta_<modulo>/
    ├── <modulo>.js                # Orquestrador
    ├── core/
    │   ├── formatadores.js
    │   ├── <X>Form.js             # Classe compartilhada (create/edit)
    │   └── pdf.js
    ├── components/
    │   ├── totalizadores.js
    │   └── ordenacao.js
    ├── modals/
    │   ├── <x>-nova.js
    │   └── <x>-editar.js
    └── acoes_e_modais/
        ├── pasta_excluir/excluir_<x>.js
        ├── pasta_reativar/reativar_<x>.js
        └── pasta_auditoria/auditoria_<modulo>.js
```

## 2.4 CSS — `static/css/`

```
static/css/
├── components/                    # COMPARTILHADO
│   ├── buttons.css
│   ├── filters.css
│   ├── footer.css
│   ├── tables.css
│   ├── modal.css                  # .fin-modal-* (full-screen)
│   ├── modal_confirmacao.css
│   ├── modal_auditoria.css
│   ├── form.css
│   └── notificacoes.css
└── core/
    ├── reset.css
    ├── responsive.css
    └── base_pos_acesso.css
```

## 2.5 Auditoria — `rotas/auditoria_geral/`

```
rotas/auditoria_geral/
├── __init__.py
└── pasta_<modulo>/
    ├── __init__.py
    ├── logica_auditoria.py
    ├── services_auditoria.py
    └── tabela.py
```

## 2.6 Docs

```
docs/
├── PLAYBOOK_2099.md
├── 01_stack_e_principios.md
├── 02_estrutura_pastas.md
├── 03_banco_de_dados.md
├── 04_backend.md
├── 05_auditoria.md
├── 06_frontend.md
├── 07_templates.md
├── 08_css.md
├── 09_pdf_weasyprint.md
├── 10_build_combina.md
├── 11_armadilhas.md
├── 12_checklist_modulo_novo.md
└── 13_comandos.md
```