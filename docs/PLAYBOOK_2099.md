# VHORGANIZA — PLAYBOOK 2099 (v3.1)
## Índice geral do padrão de desenvolvimento

**Versão:** 3.1 (pós-WeasyPrint)
**Data:** Outubro/2026
**Módulos de referência:** Finanças + Tarefas + Orçamentos (todos ~95%)

---

## 🎯 O QUE É ISSO

Este é o **índice geral** do padrão 2099 do VHORGANIZA.
Cada arquivo trata de **um assunto específico** (não de um módulo).

**Motivo:** os 3 módulos têm **80% do padrão comum**.
Separar por módulo **duplicaria tudo**. Separar por assunto **reaproveita**.

---

## 📚 ESTRUTURA DOS DOCS

| # | Arquivo | O que tem |
|---|---------|-----------|
| 01 | [Stack e Princípios](01_stack_e_principios.md) | Stack + 20 princípios invioláveis |
| 02 | [Estrutura de Pastas](02_estrutura_pastas.md) | Árvore completa de pastas |
| 03 | [Banco de Dados](03_banco_de_dados.md) | Colunas, índices, backfill, auditoria |
| 04 | [Backend](04_backend.md) | View magra, services, validações, filtros |
| 05 | [Auditoria](05_auditoria.md) | Tabela, service, view, JSON de alterações |
| 06 | [Frontend](06_frontend.md) | Classes JS, htmx.ajax, campo-a-campo |
| 07 | [Templates](07_templates.md) | 3 camadas, partials, modais |
| 08 | [CSS](08_css.md) | Modal full-screen, campo-erro, componentes |
| 09 | [PDF — WeasyPrint](09_pdf_weasyprint.md) | Geração de PDF 100% Python |
| 10 | [Build / combina.py](10_build_combina.md) | Concatenar JS/CSS |
| 11 | [Armadilhas](11_armadilhas.md) | O que já quebrou e como evitar |
| 12 | [Checklist — Módulo Novo](12_checklist_modulo_novo.md) | Passo a passo |
| 13 | [Comandos](13_comandos.md) | Build, commit, deploy, debug |

---

## 🚦 POR ONDE COMEÇAR

**Se você é NOVO no projeto:**
1. Leia **01** (Stack e Princípios) → entender a filosofia
2. Leia **02** (Estrutura de Pastas) → saber onde as coisas ficam
3. Leia **12** (Checklist) → saber o passo a passo de criar módulo

**Se você vai CRIAR um módulo novo:**
1. **02** (Estrutura) → copiar o padrão de pastas
2. **03** (Banco) → criar tabela + índices + backfill
3. **04** (Backend) → view magra + service + validações
4. **05** (Auditoria) → tabela auditoria + service
5. **06** (Frontend) → JS
6. **07** (Templates) → HTML
7. **08** (CSS) → reaproveitar componentes
8. **12** (Checklist) → conferir antes de subir

**Se você encontrou um BUG:**
1. **11** (Armadilhas) → ver se já aconteceu antes
2. Se não tá lá → adicionar

**Se você vai gerar PDF:**
1. **09** (PDF) → leia **inteiro** antes de começar

---

## 🎯 PRINCÍPIOS GERAIS (resumo)

**Os 5 mais importantes:**
1. **HTMX puro** — front só abre modal, backend devolve HTML
2. **View magra** — regra de negócio vai pro `services.py`
3. **Auditoria SEMPRE na view, transacional**
4. **Soft delete** — `UPDATE ativo = 0`, nunca `DELETE FROM`
5. **Pós-insert = `htmx.ajax`** — não `window.location.reload()`

**Detalhes nos arquivos seguintes.**

---

## 📌 MÓDULOS DE REFERÊNCIA

| Módulo | Status | O que tem de mais avançado |
|--------|--------|----------------------------|
| **Finanças** | 95% | Parcelamento, diff de filhas, `TransacaoForm` robusto |
| **Tarefas** | 95% | Auditoria com nome de categoria, erros 200 |
| **Orçamentos** | 100% | Estrutura JSONB, PDF, campo-a-campo, reativar |

**Quando tiver dúvida:** olhe nos 3 módulos como referência.

---

## 🎯 REGRAS DE OURO

1. **Nunca `window.location.reload()`** — usa `htmx.ajax`
2. **Nunca `dict(row)`** — usa `dict(zip(colunas, row))`
3. **Nunca `DELETE FROM`** — soft delete
4. **Nunca `required` no HTML** — backend valida
5. **Nunca `setTimeout` pra sync HTMX** — usa `htmx:afterSwap`
6. **Nunca `onclick` inline** — usa `data-*` + listener
7. **Nunca CSS no `JS_FILES`** — separar
8. **Sempre rodar build DEPOIS de editar JS**
9. **Sempre backfill em coluna nova**
10. **Sempre atualizar este playbook ao mudar padrão**

---

## 📥 FIM DO ÍNDICE

> **Este documento é a porta de entrada do padrão 2099.**
> Ao criar módulo novo: leia **01 → 02 → 12**.
> Ao encontrar bug: veja **11**.
> Ao mudar padrão: atualize o arquivo do assunto + avise no **PLAYBOOK_2099.md**.