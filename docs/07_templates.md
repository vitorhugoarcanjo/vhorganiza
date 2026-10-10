# 07 — Templates

## 7.1 Estrutura da tabela (3 camadas)

**`_tabela_<modulo>.html.jinja`:**
```jinja
<div id="tabela-container" data-url-refresh="{{ url_for('<modulo>.ini_<modulo>') }}">
    <div class="painel-tabela-conteudo scroll-fino">
        <div class="table-responsive">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th style="width: 65px;">Nº REG.</th>
                        <th style="width: 145px; text-align: center;">AÇÕES</th>
                    </tr>
                </thead>
                {% include 'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja' %}
            </table>
        </div>
    </div>
</div>
```

**`partials/_tbody_<modulo>.html.jinja`:**
```jinja
<tbody id="tbody-<modulo>">
    {% if <x> %}
        {% for <x> in <x>s %}
            {% include 'pasta_<modulo>/partials/_linha_<modulo>.html.jinja' %}
        {% endfor %}
    {% else %}
        <tr>
            <td colspan="9" class="text-center py-4 text-white-50">Nenhum registro encontrado.</td>
        </tr>
    {% endif %}
</tbody>
```

**`partials/_linha_<modulo>.html.jinja`:**
```jinja
<tr data-sequencia="{{ <x>.sequencia }}" id="linha-<x>-{{ <x>.sequencia }}">
    <td class="td-acoes text-center">
        <button type="button" class="btn-acao audit"
                hx-get="{{ url_for('auditoria.historico_<x>', <x>_seq=<x>.sequencia) }}"
                hx-target="#modal-auditoria-container"
                hx-swap="innerHTML">
            <i class="bi bi-clock-history"></i>
        </button>

        {% if <x>.ativo == 1 %}
            <button type="button" class="btn-acao edit"
                    onclick="abrirModalEditar({{ <x>.sequencia }})">
                <i class="bi bi-pencil"></i>
            </button>

            <button type="button" class="btn-acao delete btn-excluir"
                    data-sequencia="{{ <x>.sequencia }}"
                    data-titulo="{{ <x>.titulo }}">
                <i class="bi bi-trash"></i>
            </button>
        {% else %}
            <button type="button" class="btn-acao reativar btn-reativar"
                    data-sequencia="{{ <x>.sequencia }}"
                    data-titulo="{{ <x>.titulo }}">
                <i class="bi bi-arrow-repeat"></i>
            </button>
        {% endif %}
    </td>
</tr>
```

## 7.2 Modal de auditoria (accordion)

```jinja
<div class="fin-modal-overlay active" id="modalAuditoria">
    <div class="fin-modal-box">
        <div class="fin-modal-header">
            <h3>Auditoria — <X> #{{ <x>_seq }}</h3>
            <button class="fin-btn-close-modal" onclick="fecharModalAuditoria()">✕</button>
        </div>

        <div class="fin-modal-body">
            <div class="audit-wrapper">
                {% for item in historico %}
                <div class="audit-entry">
                    <div class="audit-entry-header" onclick="toggleAuditEntry(this)">
                        <div class="audit-entry-header-left">
                            <i class="bi bi-chevron-right audit-chevron"></i>
                            <span class="audit-badge audit-badge-{{ item.acao }}">
                                {% if item.acao == 'criada' %}✨ Criada
                                {% elif item.acao == 'editada' %}✏️ Editada
                                {% elif item.acao == 'inativada' %}🗑️ Inativada
                                {% elif item.acao == 'reativada' %}🔄 Reativada
                                {% else %}{{ item.acao }}
                                {% endif %}
                            </span>
                            <span class="audit-data-hora">{{ item.data_hora }}</span>
                        </div>
                        <span class="audit-usuario">
                            <i class="bi bi-person-circle"></i> {{ item.usuario_nome or 'Sistema' }}
                        </span>
                    </div>

                    <div class="audit-entry-body">
                        {% if item.alteracoes %}
                            <div class="audit-fields">
                                {% for alt in item.alteracoes %}
                                <div class="audit-field">
                                    <div class="audit-field-label">{{ alt.campo }}</div>
                                    <div class="audit-field-value">
                                        {% if alt.antes is defined and alt.antes is not none %}
                                            <span class="audit-old">{{ alt.antes }}</span>
                                            <i class="bi bi-arrow-right audit-arrow"></i>
                                        {% endif %}
                                        <span class="audit-new">{{ alt.depois or '(vazio)' }}</span>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        {% elif item.campo_alterado %}
                            <div class="audit-fields">
                                <div class="audit-field">
                                    <div class="audit-field-label">{{ item.campo_alterado }}</div>
                                    <div class="audit-field-value">
                                        {% if item.valor_antigo %}
                                            <span class="audit-old">{{ item.valor_antigo }}</span>
                                            <i class="bi bi-arrow-right audit-arrow"></i>
                                        {% endif %}
                                        <span class="audit-new">{{ item.valor_novo or '(vazio)' }}</span>
                                    </div>
                                </div>
                            </div>
                        {% else %}
                            <p class="audit-empty">Nenhuma alteração detalhada.</p>
                        {% endif %}
                        <div class="audit-footer">
                            <i class="bi bi-globe"></i> IP: {{ item.ip or '-' }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer-fixo-padrao">
            <button class="btn-footer-cancelar" onclick="fecharModalAuditoria()">
                <i class="bi bi-x-circle"></i> FECHAR
            </button>
            <h2>AUDITORIA</h2>
            <div class="contador-footer">
                <i class="bi bi-list-ul"></i> {{ historico|length }} registros
            </div>
        </div>
    </div>
</div>
```

## 7.3 Modal novo — regras

- **NÃO usar `required`** no HTML — backend valida
- **NÃO usar `onchange="atualizarPreview()"`** se a função não existe
- **Sempre** incluir `<input type="hidden">` pra dados que o JS atualiza

## 7.4 Containers na tela principal

```jinja
<!-- Containers dinâmicos -->
<div id="modal-nova-container"></div>
<div id="modal-editar-container"></div>
<div id="modal-auditoria-container"></div>
```