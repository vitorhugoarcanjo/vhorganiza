# 08 — CSS

## 8.1 Modal full-screen (`.fin-modal-*`)

```css
.fin-modal-overlay {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.85);
    display: none; justify-content: center; align-items: center;
    z-index: 99999;
    backdrop-filter: blur(8px);
}

.fin-modal-overlay.active { display: flex; }

.fin-modal-box {
    background: var(--bg-card);
    width: 100%; height: 100vh;
    display: flex; flex-direction: column;
    animation: finModalSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes finModalSlideIn {
    from { opacity: 0; transform: scale(0.96) translateY(20px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}

.fin-modal-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 24px;
    border-bottom: 2px solid var(--border-sutil);
    flex-shrink: 0;
}

.fin-modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px 90px 24px;
}

.fin-modal-overlay.active .footer-fixo-padrao {
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
}
```

## 8.2 Validação campo-a-campo

```css
.campo-erro {
    border: 2px solid #ef4444 !important;
    background: rgba(239, 68, 68, 0.05) !important;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
}

.msg-erro-campo {
    display: block;
    color: #ef4444;
    font-size: 0.7rem;
    margin-top: 4px;
    font-weight: 600;
    line-height: 1.3;
}

/* Casos especiais */
.input-com-prefixo.campo-erro {
    border: 2px solid #ef4444 !important;
    background: rgba(239, 68, 68, 0.05) !important;
}

.tipo-container.campo-erro {
    border: 2px solid #ef4444 !important;
    border-radius: 8px;
    padding: 2px;
}
```

## 8.3 Modal auditoria (accordion)

```css
.audit-entry { background: var(--bg-card); border: 1px solid var(--border-sutil); border-radius: 8px; }
.audit-entry.open { border-color: rgba(37, 99, 235, 0.5); }

.audit-entry-header { display: flex; justify-content: space-between; padding: 12px 16px; cursor: pointer; }

.audit-chevron { transition: transform 0.2s ease; }
.audit-entry.open .audit-chevron { transform: rotate(90deg); }

.audit-badge-criada { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.audit-badge-editada { background: rgba(37, 99, 235, 0.15); color: #2563eb; }
.audit-badge-inativada { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.audit-badge-reativada { background: rgba(37, 99, 235, 0.15); color: #2563eb; }

.audit-entry-body { max-height: 0; overflow: hidden; transition: max-height 0.25s ease; }
.audit-entry.open .audit-entry-body { max-height: 2000px; border-top: 1px solid var(--border-sutil); }

.audit-field { padding: 8px 12px; background: var(--bg-principal); border-radius: 6px; }
.audit-old { color: #f87171; text-decoration: line-through; background: rgba(248, 113, 113, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-new { color: #4ade80; font-weight: 600; background: rgba(74, 222, 128, 0.1); padding: 2px 8px; border-radius: 4px; }
.audit-arrow { color: var(--texto-discreto); margin: 0 8px; }
```

## 8.4 CSS compartilhado vs específico

| Onde | O que colocar |
|------|---------------|
| `components/` | Botões, forms, modais base, tabelas, footer |
| `core/` | Reset, responsive, base_pos_acesso |
| `modules/pasta_<modulo>/` | Específicos do módulo (se necessário) |

**Regra:** se **2+ módulos usam**, vai pra `components/`. Se **só 1 usa**, fica em `modules/`.

## 8.5 Nomenclatura

| Padrão | Uso |
|--------|-----|
| `.fin-modal-*` | Modal full-screen (compartilhado) |
| `.orc-modal-*` | Modal Orçamento (legado, migrando) |
| `.btn-*` | Botões |
| `.td-*` | Células de tabela |
| `.js-*` | Só pra JS (não estiliza) |
| `.campo-erro` | Validação |
| `.msg-erro-campo` | Mensagem de erro |