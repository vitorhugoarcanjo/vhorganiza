# 12 — Checklist: Módulo Novo

## Backend

- [ ] Criar `rotas/pasta_<modulo>/__init__.py` (blueprint pai)
- [ ] Criar `<modulo>.py` (view + `_buscar_<x>_com_filtros` + `_render_tbody`)
- [ ] Criar `queries.py`, `filters.py`, `formatters.py`, `services/`
- [ ] Criar `crud/pasta_insert/` (view magra + services.py + validacoes.py)
- [ ] Criar `crud/pasta_edit/` (JSON + diff + auditoria)
- [ ] Criar `crud/pasta_delete/` (HTML + HX-Trigger + auditoria)
- [ ] Criar `crud/pasta_<acao>/` (reativar, concluir, etc) — se aplicável
- [ ] Criar `crud/pasta_pdf/` — se tiver PDF (WeasyPrint)
- [ ] **Todas** as views: `logger.exception()`, `conexao.rollback()`
- [ ] **Todas** as auditorias: `conexao=conexao`, `id_interno`, JSON `[{campo, antes, depois}]`
- [ ] **Toda** migração: SQL de backfill

## Banco de Dados

- [ ] Tabela principal com colunas padrão (sequencia, numero, datas, ativo, etc)
- [ ] Índice único `(usuario_id, sequencia_<modulo>)`
- [ ] Índice `(usuario_id, ativo)`
- [ ] Índice `(data_emissao DESC)`
- [ ] Tabela `<modulo>_auditoria` com FK pra `id` interno
- [ ] `criar_tabela_<modulo>.py` no `config/database.py`
- [ ] `criar_indices()` atualizado

## Auditoria

- [ ] `rotas/auditoria_geral/pasta_<modulo>/tabela.py`
- [ ] `services_auditoria.py` (com `conexao=None` + colunas explícitas + zip)
- [ ] `logica_auditoria.py` (traduz sequência → id)
- [ ] Registrar no `bp_auditoria`
- [ ] Template `modal_auditoria.html.jinja`

## Frontend

- [ ] `core/<X>Form.js` (setData, getData, submit JSON, reset)
- [ ] `components/totalizadores.js`, `ordenacao.js`
- [ ] `modals/<x>-nova.js`, `<x>-editar.js` (com `htmx.ajax` pós-sucesso)
- [ ] `acoes_e_modais/pasta_<acao>/<acao>_<x>.js`
- [ ] `<modulo>.js` (só init + recarregarTabela)
- [ ] Validação campo-a-campo (`mostrarErrosForm`)
- [ ] **Zero** `setTimeout` fixo
- [ ] **Zero** `window.location.reload()` pós-insert

## Templates

- [ ] `tela_<modulo>.html.jinja`
- [ ] `_tabela_<modulo>.html.jinja`
- [ ] `partials/_tbody_<modulo>.html.jinja` + `_linha_<modulo>.html.jinja`
- [ ] `partials/form_<x>.html.jinja`
- [ ] `modais/modal_nova_<x>.html.jinja` + `modal_editar_<x>.html.jinja`
- [ ] `modais/excluir_<x>.html` + `reativar_<x>.html`
- [ ] `pdf/pdf_<x>.html.jinja` (se tiver PDF)
- [ ] `pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja`
- [ ] Containers na tela: `#modal-nova-container`, `#modal-editar-container`, `#modal-auditoria-container`

## CSS

- [ ] Reaproveitar `components/` (não duplicar)
- [ ] Específicos em `modules/pasta_<modulo>/` se necessário
- [ ] Adicionar `loading.css` (spinner) se ainda não tiver

## Build

- [ ] Ajustar `combine_static_<modulo>.py` (JS_FILES + CSS_FILES)
- [ ] **Conferir** que CSS não tá em JS e vice-versa
- [ ] Rodar `python scripts/combine_static_<modulo>.py`
- [ ] **Zero** `⚠️ não encontrado`

## Antes de subir

- [ ] Criar funciona (com sequência + numero)
- [ ] Editar (diff correto)
- [ ] Excluir/reativar
- [ ] Detalhes (se aplicável)
- [ ] PDF gera (WeasyPrint)
- [ ] Auditoria abre em modal (accordion)
- [ ] Toast verde em todas ações
- [ ] Filtros preservam
- [ ] Console sem erro
- [ ] **Pós-insert recarrega só a tabela (não F5)**
- [ ] **Validação campo-a-campo funciona (borda vermelha)**
- [ ] **Testar em prod** (latência 200ms)
- [ ] **Atualizar Playbook** (adicionar na lista de módulos)
- [ ] **Commit + push**

## Pós-deploy

- [ ] Testar em prod
- [ ] Verificar logs (`journalctl -u gestao_financeira -n 50`)
- [ ] Se der bug, adicionar em `11_armadilhas.md`