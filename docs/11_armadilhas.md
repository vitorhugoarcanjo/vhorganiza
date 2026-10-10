# 11 — Armadilhas Conhecidas

## 11.1 Backend

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `dict(row)` no `listar_formatado` | `object is not iterable` | Colunas explícitas + `dict(zip(colunas, row))` |
| Auditoria com `sequencia` (não `id`) | Modal abre vazio | View traduz `sequencia → id` |
| `campo_alterado='todos'` | JSON não é parseado | Usar `'multiplos'` |
| `converter_valor_br` sempre remove `.` | `1009.9` → `10099` | Check `if ',' in valor` |
| View faz INSERT direto | Código duplicado | Mover pro `services.py` |
| Coluna nova sem backfill | Antigos ficam NULL | SQL de backfill obrigatório |
| `data_emissao` no filtro errado | Orçamento de hoje não aparece | Filtrar por `data_emissao` |

## 11.2 Frontend

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `setTimeout(50)` pra sync HTMX | Quebra em prod (200ms latência) | `htmx:afterSwap` |
| `window.location.reload()` pós-insert | Perde scroll/filtros | `htmx.ajax` só a tabela |
| `required` no HTML | Validação burlável | Backend valida sempre |
| `onchange` pra função inexistente | `is not defined` no console | Remover ou criar a função |
| `modal.onclick` sempre | Clicar dentro fecha | Verificar `event.target === modal` |

## 11.3 CSS/Build

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| CSS no `JS_FILES` | `Uncaught SyntaxError` | Separar JS e CSS |
| Bundle desatualizado | JS novo não roda | Rodar build DEPOIS de editar |
| OOB com classe perdida | Botões "desalinhados" após toggle | Manter `flex-row gap-1` no wrapper OU usar JS compartilhado |

## 11.4 HTMX

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `HX-Trigger` em resposta 4xx | HTMX ignora header | Sempre `200` |
| `hx-target` apontando pra fora do DOM | `htmx:targetError` | Container no partial |

## 11.5 Sessão/Usuário

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| `session['user_id']` ausente | `KeyError` | `session.get('user_id')` |
| Categoria mostra ID | `19` em vez de `Trabalho` | Buscar `nome` no service |

## 11.6 Dados

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| Data ISO crua | `2026-10-04` | Helper `_fmt_data_br` |
| Float sem casas | `150` em vez de `150.00` | Helper `_fmt_moeda` |
| `None` renderizado | `None` na tela | `valor or '(vazio)'` |

## 11.7 PDF (WeasyPrint)

| Armadilha | Sintoma | Solução |
|-----------|---------|---------|
| Falta GTK no Windows | `cannot load library 'libgobject-2.0-0'` | Instalar GTK Runtime |
| Falta libs no Linux | `cannot load library 'libpango...'` | `apt install` |
| `position: fixed` | Footer ignora | Usar `@page` margins |
| JavaScript | Não roda | Evitar no PDF |

## 11.8 Como adicionar uma nova armadilha

1. **Achou um bug?** Documenta aqui **antes** de corrigir
2. **Padrão:** `| sintoma | solução |`
3. **Categoria certa** (Backend, Frontend, HTMX, etc)
4. **Sempre** que corrigir algo, adicionar aqui

**Regra 2099:** "todo bug que quebrou uma vez, documenta pra não quebrar de novo".