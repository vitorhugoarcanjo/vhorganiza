# 01 — Stack e Princípios

## 1.1 Stack

- **Backend:** Flask + PostgreSQL
- **Frontend:** HTMX + JS modular vanilla (sem framework)
- **Templates:** Jinja2
- **PDF:** **WeasyPrint** (100% Python, sem binário externo)
- **Build:** `python scripts/combine_static_<modulo>.py`
- **Deploy:** Git → VPS (Contabo/Alemanha) → `systemctl restart gestao_financeira`
- **Latência prod:** ~200ms (Brasil ↔ Alemanha)

## 1.2 Princípios invioláveis (20)

### Backend
1. **View magra** — toda regra de negócio vai pro `services.py`
2. **Service NÃO faz commit** — quem faz é a view (transacional)
3. **Validação backend SEMPRE** — front ajuda, mas backend é a fonte da verdade
4. **Sequência visual por usuário** — cada user tem seu `#1, #2, #3`
5. **Número formatado único** — `ORC-2026-0001`, não só `#1`
6. **Cache de valores calculados** — `valor_total` salvo no banco
7. **Soft delete SEMPRE** — `UPDATE ativo = 0`, nunca `DELETE FROM`
8. **Colunas explícitas no SELECT** — `dict(zip(colunas, row))`, nunca `dict(row)`

### Frontend
9. **HTMX puro** — front só abre/fecha modal, backend devolve HTML + HX-Trigger
10. **1 arquivo = 1 responsabilidade** — 1 JS por ação
11. **Pós-insert = `htmx.ajax`** — nunca `window.location.reload()`
12. **Sem `setTimeout` fixo** — usar `htmx:afterSwap`
13. **Sem `onclick` inline** — sempre `data-*` + listener JS
14. **Validação campo-a-campo no front** — borda vermelha + mensagem por campo

### Auditoria
15. **Auditoria SEMPRE na view, transacional** — mesma `conexao`
16. **FK da auditoria = `id` interno** — não sequência visual
17. **JSON de alterações** = `[{campo, antes, depois}]` quando `campo_alterado='multiplos'`

### Geral
18. **CSS compartilhado** em `components/` — não duplicar por módulo
19. **Respostas sempre `200`** — HTMX ignora `HX-Trigger` em 4xx/5xx
20. **JS compartilhado** em `static/js/components/` — quando faz sentido

## 1.3 Hierarquia de decisão

**Quando tiver dúvida sobre "onde colocar X":**

| X | Onde colocar |
|---|--------------|
| Regra de negócio | `services.py` do CRUD |
| Validação | `validacoes.py` do CRUD |
| SQL puro | `queries.py` do módulo |
| Filtro | `filters.py` do módulo |
| Serialização | `formatters.py` do módulo |
| Rota principal | `<modulo>.py` |
| Rota CRUD | `crud/pasta_<acao>/<acao>_<x>.py` |
| Template da tabela | `_tabela_<modulo>.html.jinja` |
| Template do tbody | `partials/_tbody_<modulo>.html.jinja` |
| Template da linha | `partials/_linha_<modulo>.html.jinja` |
| Template do modal | `modais/modal_<acao>_<x>.html.jinja` |
| JS de ação | `acoes_e_modais/pasta_<acao>/<acao>_<x>.js` |
| CSS específico | `modules/pasta_<modulo>/` |
| CSS compartilhado | `components/` |

## 1.4 Anti-padrões (o que NUNCA fazer)

- ❌ `dict(row)` — quebra em colunas dinâmicas
- ❌ `DELETE FROM` — perde histórico
- ❌ `window.location.reload()` pós-insert — perde scroll/filtros
- ❌ `setTimeout(50)` pra sync HTMX — quebra em prod
- ❌ `required` no HTML — front é burlável
- ❌ `onclick="funcao()"` inline — dificulta manutenção
- ❌ CSS no `JS_FILES` — quebra o bundle
- ❌ Auditoria com `sequencia` — FK tem que ser `id` interno
- ❌ `required` em campo — backend valida sempre
- ❌ `campo_alterado='todos'` — usar `'multiplos'`