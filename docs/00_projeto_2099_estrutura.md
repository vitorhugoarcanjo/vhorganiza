# VHORGANIZA — Estrutura do Projeto (Padrão 2099)

**Última atualização:** 11/10/2026
**Versão do padrão:** 2099 v3.1
**Módulos em produção:** Tarefas, Finanças, Orçamentos, Categorias

---

## 📑 Índice

1. [Stack Técnica](#1-stack-técnica)
2. [Estrutura de Pastas Geral](#2-estrutura-de-pastas-geral)
3. [Padrão de Módulo (Backend)](#3-padrão-de-módulo-backend)
4. [Padrão de Módulo (Frontend)](#4-padrão-de-módulo-frontend)
5. [Padrão de CRUD](#5-padrão-de-crud)
6. [Padrão de Auditoria](#6-padrão-de-auditoria)
7. [Padrão de Templates](#7-padrão-de-templates)
8. [Padrão de CSS](#8-padrão-de-css)
9. [Padrão de Build](#9-padrão-de-build)
10. [Banco de Dados](#10-banco-de-dados)
11. [Módulos Existentes](#11-módulos-existentes)
12. [Princípios Invioláveis](#12-princípios-invioláveis)

---

## 1. Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Flask + PostgreSQL |
| **Frontend** | HTMX + JS modular vanilla (sem framework) |
| **Templates** | Jinja2 |
| **PDF** | WeasyPrint (100% Python) |
| **Build** | `python scripts/combine_static_<modulo>.py` |
| **Deploy** | Git → VPS (Contabo/Alemanha) → `systemctl restart gestao_financeira` |
| **Latência prod** | ~200ms (Brasil ↔ Alemanha) |

---

## 2. Estrutura de Pastas Geral
vhorganiza/
├── app.py # Entry point
├── config/
│ ├── database.py # criar_todas_tabelas()
│ ├── imports_rotas.py # register_blueprint de todos
│ └── indices_automatico.py # criar_indices()
├── rotas/
│ ├── middleware/ # autenticacao, logs
│ ├── pasta_login/ # Login/Cadastro/Recuperar
│ ├── pasta_dashboard/
│ ├── pasta_config/
│ ├── pasta_tarefas/ # ✅ 2099
│ ├── pasta_financas/ # ✅ 2099
│ ├── pasta_orcamentos/ # ✅ 2099
│ ├── pasta_categorias/ # ✅ 2099
│ ├── auditoria_geral/ # Auditoria de todos
│ └── logs/
├── templates/
│ ├── tela_base_pos_login/base.html # Template base
│ ├── pasta_login/
│ ├── pasta_tarefas/
│ ├── pasta_financas/
│ ├── pasta_orcamentos/
│ ├── pasta_categorias/
│ ├── pasta_auditoria/
│ └── components/ # Templates compartilhados
├── static/
│ ├── css/
│ │ ├── core/ # Reset, responsive
│ │ ├── components/ # Compartilhados
│ │ └── modules/ # Por módulo
│ └── js/
│ ├── components/ # Compartilhados
│ └── modules/ # Por módulo
├── scripts/
│ ├── combine_static_tarefas.py
│ ├── combine_static_financas.py
│ ├── combine_static_orcamentos.py
│ └── combine_static_categorias.py
└── docs/
├── PLAYBOOK_2099.md
├── 01_stack_e_principios.md
├── ...
└── backlog/

text

---

## 3. Padrão de Módulo (Backend)

### 3.1 Estrutura
rotas/pasta_<modulo>/
├── init.py # Blueprint principal + register_blueprint dos CRUDs
├── <modulo>.py # Rotas principais (listagem, limpar_filtros)
├── queries.py # SQL puro (class <Modulo>Queries)
├── filters.py # Filtros (class <Modulo>Filters)
├── formatters.py # Serialização (class <Modulo>Formatters)
├── services/
│ └── services_<modulo>.py # Service principal (class <Modulo>Services)
└── crud/
├── pasta_insert/
│ ├── init.py # bp_insert + add_url_rule
│ ├── insert_<x>.py # View MAGRA — AUDITORIA AQUI
│ ├── services.py # Inserir<X>Service
│ └── validacoes.py # validar_dados_insercao
├── pasta_edit/
│ ├── init.py
│ ├── edit_<x>.py # View + montar_diff
│ ├── services.py # Editar<X>Service
│ └── validacoes.py
├── pasta_delete/
│ ├── init.py
│ ├── delete<x>.py # HTML + HX-Trigger — AUDITORIA
│ └── services.py
├── pasta_reativar/
│ ├── init.py
│ ├── reativar_<x>.py
│ └── services.py
└── pasta_pdf/ # Se o módulo tiver PDF
├── init.py
└── pdf_<x>.py

text

### 3.2 Blueprint principal (`__init__.py`)

```python
from flask import Blueprint

bp_<modulo> = Blueprint('<modulo>', __name__)

from .<modulo> import ini_<modulo>, limpar_filtros
from .crud.pasta_insert   import bp_insert
from .crud.pasta_edit     import bp_edit
from .crud.pasta_delete   import bp_delete
from .crud.pasta_reativar import bp_reativar

bp_<modulo>.add_url_rule('/', view_func=ini_<modulo>, methods=['GET', 'POST'])
bp_<modulo>.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

bp_<modulo>.register_blueprint(bp_insert,    url_prefix='/nova_<x>')
bp_<modulo>.register_blueprint(bp_edit,      url_prefix='/edit_<x>')
bp_<modulo>.register_blueprint(bp_delete,    url_prefix='/excluir_<x>')
bp_<modulo>.register_blueprint(bp_reativar,  url_prefix='/reativar_<x>')
3.3 View principal (<modulo>.py)
python
@login_required
def ini_<modulo>():
    usuario_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. FILTROS
    descricao_filtro = <Modulo>Filters.filtro_descricao()
    mostrar_inativas = <Modulo>Filters.processar_mostrar_inativas()
    filtros = {...}

    conexao, cursor = ini_conexao()

    # 2. QUERY
    service = <Modulo>Services(conexao=None, cursor=cursor)
    dados_raw = service.buscar_<x>(usuario_id, filtros)
    dados = <Modulo>Formatters.formatar_<x>(dados_raw)

    # 3. HTMX (retorna partial + OOB)
    if is_htmx:
        return _renderizar_htmx(dados, filtros)

    # 4. RENDER COMPLETO
    return render_template('pasta_<modulo>/tela_<modulo>.html.jinja', ...)

def _renderizar_htmx(dados, filtros):
    tabela = render_template('pasta_<modulo>/_tabela_<modulo>.html.jinja', ...)
    oob_html = f'''<input type="hidden" ... hx-swap-oob="outerHTML:#...">'''
    return tabela + oob_html
3.4 Queries (queries.py)
python
class <Modulo>Queries:
    @staticmethod
    def get_<x>_base():
        return """
            SELECT col1, col2, ...
            FROM <tabela>
            WHERE usuario_id = %s
        """
    
    @staticmethod
    def criar_<x>():
        return """INSERT INTO ... RETURNING id"""
    
    @staticmethod
    def atualizar_<x>():
        return """UPDATE ... SET ... WHERE id = %s"""
    
    @staticmethod
    def inativar_<x>():
        return """UPDATE ... SET ativo = 0, ... WHERE id = %s AND ativo = 1"""
    
    @staticmethod
    def reativar_<x>():
        return """UPDATE ... SET ativo = 1, ... WHERE id = %s AND ativo = 0"""
3.5 Filters (filters.py)
python
class <Modulo>Filters:
    @staticmethod
    def filtro_descricao():
        descricao = request.form.get('descricao', '')
        if descricao:
            session['<modulo>_descricao'] = descricao
            return descricao
        return session.get('<modulo>_descricao', '')
    
    @staticmethod
    def processar_mostrar_inativas():
        """Retorna '0', '1' ou '2'"""
        mostrar = request.args.get('mostrar_inativas')
        if mostrar is None and request.method == 'POST':
            mostrar = request.form.get('mostrar_inativas')
        if mostrar is None:
            mostrar = session.get('<modulo>_mostrar_inativas', '0')
        session['<modulo>_mostrar_inativas'] = mostrar
        return mostrar
    
    @staticmethod
    def aplicar_filtros_query(query, params, filtros):
        # monta os AND/OR
        return query, params
    
    @staticmethod
    def limpar_filtros():
        session.pop('<modulo>_descricao', None)
        session.pop('<modulo>_mostrar_inativas', None)
3.6 Formatters (formatters.py)
python
class <Modulo>Formatters:
    @staticmethod
    def formatar_<x>(dados_raw):
        """Converte tuplas em dicts."""
        resultado = []
        for d in dados_raw:
            resultado.append({
                'id':     d[0],
                'nome':   d[1] or 'Sem nome',
                'ativo':  d[2],
                ...
            })
        return resultado
3.7 Services principal (services/services_<modulo>.py)
python
class <Modulo>Services:
    def __init__(self, conexao, cursor):
        self.conexao = conexao
        self.cursor = cursor
    
    def buscar_<x>(self, usuario_id, filtros):
        from rotas.pasta_<modulo>.queries import <Modulo>Queries
        from rotas.pasta_<modulo>.filters import <Modulo>Filters
        
        query = <Modulo>Queries.get_<x>_base()
        params = [usuario_id]
        query, params = <Modulo>Filters.aplicar_filtros_query(query, params, filtros)
        query += " ORDER BY ... ASC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
3.8 Service do CRUD (crud/pasta_insert/services.py)
python
class Inserir<X>Service:
    @staticmethod
    def get_proxima_sequencia(cursor, usuario_id):
        cursor.execute("""SELECT COALESCE(MAX(sequencia_<x>), 0) + 1 FROM <tabela> WHERE usuario_id = %s""", (usuario_id,))
        res = cursor.fetchone()
        return res[0] if res else 1
    
    @staticmethod
    def gerar_numero(sequencia, ano=None):
        from datetime import date
        if ano is None:
            ano = date.today().year
        return f'<PREFIXO>-{ano}-{str(sequencia).zfill(4)}'
    
    @staticmethod
    def criar_<x>(cursor, usuario_id, dados):
        # INSERT + regras
        return True, {...}
4. Padrão de Módulo (Frontend)
4.1 Templates
text
templates/pasta_<modulo>/
├── tela_<modulo>.html.jinja        # Página completa
├── _tabela_<modulo>.html.jinja     # Container da tabela
├── partials/
│   ├── _tbody_<modulo>.html.jinja  # <tbody> com for
│   └── _linha_<x>.html.jinja       # 1 <tr>
└── modais/
    ├── modal_nova_<x>.html.jinja
    ├── modal_editar_<x>.html.jinja
    └── modal_excluir_<x>.html.jinja

templates/pasta_auditoria/pasta_<modulo>/
└── modal_auditoria.html.jinja
4.2 JS
text
static/js/modules/pasta_<modulo>/
├── <modulo>.js                     # Orquestrador
├── core/
│   └── <X>Form.js                  # Classe compartilhada (create/edit)
├── modals/
│   ├── <x>-nova.js
│   └── <x>-editar.js
└── acoes_e_modais/
    ├── pasta_excluir/excluir_<x>.js
    ├── pasta_reativar/reativar_<x>.js
    └── pasta_auditoria/auditoria_<modulo>.js
4.3 CSS
text
static/css/modules/pasta_<modulo>/
└── <modulo>.css                    # Prefixo específico (ex: .cat-, .fin-, .tar-)
Regra: prefixo único por módulo pra evitar colisão.

Módulo	Prefixo
Categorias	.cat-
Tarefas	.tar-
Finanças	.fin- (legado) / .fin-crud- (novo)
Orçamentos	.orc-
5. Padrão de CRUD
5.1 Insert — View MAGRA
python
@login_required
def salvar_nova_<x>():
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()
    try:
        payload = request.json or {}
        dados = {  # sanitização
            'nome': (payload.get('nome') or '').strip(),
            ...
        }
        
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200
        
        sucesso, resultado = Inserir<X>Service.criar_<x>(cursor, usuario_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400
        
        # AUDITORIA TRANSACIONAL
        alteracoes = [{'campo': 'Nome', 'depois': dados['nome']}, ...]
        Auditoria<X>Service.registrar(
            <x>_id=resultado['id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )
        
        conexao.commit()
        return jsonify({'success': True, 'message': '...', 'id': resultado['id']}), 201
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()
5.2 Edit — JSON + diff + auditoria
python
@login_required
def salvar_edicao_<x>(id):
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()
    try:
        payload = request.json or {}
        dados = {...}
        
        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200
        
        resultado = Editar<X>Service.atualizar_<x>(cursor, id, usuario_id, dados)
        if not resultado['success']:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado['error']}), 400
        
        # AUDITORIA com diff
        alteracoes = _montar_diff(resultado['dados_antes'], resultado['dados_depois'])
        if alteracoes:
            Auditoria<X>Service.registrar(
                <x>_id=resultado['id_interno'],
                acao='editada',
                campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'].lower(),
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )
        
        conexao.commit()
        return jsonify({'success': True, 'message': '...'}), 200
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()


def _montar_diff(antes, depois):
    alteracoes = []
    if antes.get('nome') != depois.get('nome'):
        alteracoes.append({'campo': 'Nome', 'antes': antes.get('nome') or '(vazio)', 'depois': depois.get('nome') or '(vazio)'})
    return alteracoes
5.3 Delete — HTML + HX-Trigger
python
@login_required
def inativar_<x>_view(id):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        registro = Inativar<X>Service.buscar_<x>(cursor, id, user_id)
        if not registro:
            conexao.close()
            return '', 404
        
        nome = registro[1]
        Inativar<X>Service.inativar_<x>(cursor, id, user_id)
        
        Auditoria<X>Service.registrar(
            <x>_id=id,
            acao='inativada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )
        
        conexao.commit()
        html = _render_tbody(user_id, cursor)
        conexao.close()
        
        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            '<x>Inativada': {'message': f'"{nome}" inativado!'}
        })
        return resp
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro")
        conexao.close()
        return '', 500
5.4 Helpers duplicados (_buscar_<x>_com_filtros + _render_tbody)
python
def _buscar_<x>_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = <Modulo>Filters.processar_filtros_data()
    filtros = <Modulo>Filters.recuperar_filtros(session)
    filtros.update({'data_inicio': data_inicio, 'data_fim': data_fim, 'tipo_data': tipo_data})
    service = <Modulo>Services(conexao=None, cursor=cursor)
    <x>_raw = service.buscar_<x>(user_id, filtros)
    return <Modulo>Formatters.formatar_<x>(<x>_raw)


def _render_tbody(user_id, cursor):
    <x> = _buscar_<x>_com_filtros(cursor, user_id)
    return render_template(
        'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja',
        <x>=<x>,
        mostrar_inativas=session.get('<modulo>_mostrar_inativas', '0'),
    )
6. Padrão de Auditoria
6.1 Estrutura
text
rotas/auditoria_geral/
├── __init__.py                     # bp_auditoria + add_url_rule
└── pasta_<modulo>/
    ├── tabela.py                   # CREATE TABLE <modulo>_auditoria
    ├── services_auditoria.py       # class Auditoria<X>Service
    └── logica_auditoria.py         # view do modal
6.2 Tabela
sql
CREATE TABLE <modulo>_auditoria (
    id SERIAL PRIMARY KEY,
    <x>_id INTEGER,                        -- FK pro ID INTERNO
    acao VARCHAR(50),                      -- criada, editada, inativada, reativada
    campo_alterado VARCHAR(100),           -- 'multiplos' ou 1 campo
    valor_antigo TEXT,
    valor_novo TEXT,                       -- JSON quando 'multiplos'
    usuario_id INTEGER,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45),
    FOREIGN KEY (<x>_id) REFERENCES <tabela>(id),
    FOREIGN KEY (usuario_id) REFERENCES cadastre_se(id)
);
6.3 Service registrar()
python
class Auditoria<X>Service:
    @staticmethod
    def get_db_connection():
        return ini_conexao()
    
    @staticmethod
    def registrar(<x>_id, acao, campo_alterado=None,
                  valor_antigo=None, valor_novo=None, conexao=None):
        propria_conexao = False
        try:
            if conexao is None:
                conexao, cursor = Auditoria<X>Service.get_db_connection()
                propria_conexao = True
            else:
                cursor = conexao.cursor()
            
            # trunca se > 2000 chars
            ...
            
            cursor.execute("""
                INSERT INTO <modulo>_auditoria
                (<x>_id, acao, campo_alterado, valor_antigo, valor_novo, usuario_id, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (<x>_id, acao, campo_alterado, valor_antigo, valor_novo,
                  session.get('user_id'), request.remote_addr))
            
            if propria_conexao:
                conexao.commit()
            return True
        except Exception as e:
            print(f"Erro: {e}")
            if propria_conexao:
                conexao.rollback()
            return False
6.4 JSON de alterações
Padrão: [{campo, antes, depois}]

Quando usar:

multiplos — 2+ campos (criar, editar, concluir, reabrir)

1 campo — 1 campo só (inativar, reativar, quitar)

Formato editada:

json
[
    {"campo": "Status", "antes": "pendente", "depois": "concluido"},
    {"campo": "Data Finalização", "antes": "(vazio)", "depois": "04/10/2026 15:46:23"}
]
Formato criada (sem antes):

json
[
    {"campo": "Título", "depois": "Teste"},
    {"campo": "Categoria", "depois": "Trabalho"}
]
6.5 View (traduz sequência → id)
python
@login_required
def historico_<x>(<x>_seq):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    
    cursor.execute("""
        SELECT id, sequencia_<modulo>, <campos_header>
        FROM <tabela>
        WHERE sequencia_<modulo> = %s AND usuario_id = %s
    """, (<x>_seq, user_id))
    row = cursor.fetchone()
    if not row:
        return '', 404
    
    id_interno = row[0]
    <x> = (row[1], row[2], ...)
    
    historico = Auditoria<X>Service.listar_por_<x>_formatado(id_interno)
    
    return render_template(
        'pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja',
        historico=historico,
        <x>=<x>,
        <x>_seq=<x>_seq,
    )
7. Padrão de Templates
7.1 Tabela em 3 camadas
_tabela_<modulo>.html.jinja:

jinja
<div id="tabela-container" data-url-refresh="{{ url_for('<modulo>.ini_<modulo>') }}">
    <div class="painel-tabela-conteudo scroll-fino">
        <div class="table-responsive">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>SEQ</th>
                        ...
                        <th style="width: 145px; text-align: center;">AÇÕES</th>
                    </tr>
                </thead>
                {% include 'pasta_<modulo>/partials/_tbody_<modulo>.html.jinja' %}
            </table>
        </div>
    </div>
</div>
partials/_tbody_<modulo>.html.jinja:

jinja
<tbody id="tbody-<modulo>">
    {% if <x> %}
        {% for item in <x> %}
            {% include 'pasta_<modulo>/partials/_linha_<modulo>.html.jinja' %}
        {% endfor %}
    {% else %}
        <tr><td colspan="9" class="text-center py-4 text-white-50">Nenhum registro.</td></tr>
    {% endif %}
</tbody>
partials/_linha_<modulo>.html.jinja:

jinja
<tr data-sequencia="{{ item.sequencia }}" id="linha-{{ item.id }}">
    <td class="td-acoes text-center">
        <button class="btn-acao audit"
                hx-get="{{ url_for('auditoria.historico_<x>', <x>_seq=item.sequencia) }}"
                hx-target="#modal-auditoria-container"
                hx-swap="innerHTML">
            <i class="bi bi-clock-history"></i>
        </button>
        
        {% if item.ativo == 1 %}
            <button class="btn-acao edit" onclick="abrirModalEditar({{ item.sequencia }})">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn-acao delete btn-excluir"
                    data-sequencia="{{ item.sequencia }}"
                    data-titulo="{{ item.titulo }}">
                <i class="bi bi-trash"></i>
            </button>
        {% else %}
            <button class="btn-acao reativar btn-reativar"
                    data-sequencia="{{ item.sequencia }}"
                    data-titulo="{{ item.titulo }}">
                <i class="bi bi-arrow-repeat"></i>
            </button>
        {% endif %}
    </td>
</tr>
7.2 Containers na tela principal
jinja
<!-- Containers dinâmicos -->
<div id="modal-nova-container"></div>
<div id="modal-editar-container"></div>
<div id="modal-auditoria-container"></div>
7.3 Modal de auditoria (accordion)
Segue pasta_auditoria/pasta_<modulo>/modal_auditoria.html.jinja.

8. Padrão de CSS
8.1 Estrutura
text
static/css/
├── core/
│   ├── reset.css
│   ├── responsive.css
│   └── base_pos_acesso.css
├── components/                     # Compartilhado (2+ módulos usam)
│   ├── buttons.css
│   ├── filters.css
│   ├── footer.css
│   ├── tables.css
│   ├── modal.css                   # .fin-modal-* (full-screen)
│   ├── modal_confirmacao.css       # .modal-confirmacao-*
│   ├── modal_auditoria.css         # .audit-*
│   ├── form.css
│   ├── notificacoes.css
│   └── categoria_inline.css        # .categoria-wrapper, .btn-add-categoria
└── modules/
    └── pasta_<modulo>/
        └── <modulo>.css            # Específico (prefixo único)
8.2 Prefixo por módulo
Módulo	Prefixo	Exemplo
Categorias	.cat-	.cat-grid, .cat-box, .cat-table
Tarefas	.tar-	.tar-...
Finanças	.fin-crud-	.fin-crud-...
Orçamentos	.orc-	.orc-modal-*
8.3 Modal full-screen (compartilhado)
css
.fin-modal-overlay { ... }
.fin-modal-box { ... }
.fin-modal-header { ... }
.fin-modal-body { ... }
.fin-btn-close-modal { ... }
8.4 Validação campo-a-campo
css
.campo-erro { border: 2px solid #ef4444 !important; }
.msg-erro-campo { color: #ef4444; font-size: 0.7rem; font-weight: 600; }
9. Padrão de Build
9.1 combine_static_<modulo>.py
python
JS_FILES = [
    'static/js/components/botoes_filtros.js',           # compartilhado
    'static/js/modules/pasta_<modulo>/core/<X>Form.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-nova.js',
    'static/js/modules/pasta_<modulo>/modals/<x>-editar.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_excluir/excluir_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_reativar/reativar_<x>.js',
    'static/js/modules/pasta_<modulo>/acoes_e_modais/pasta_auditoria/auditoria_<modulo>.js',
    'static/js/modules/pasta_<modulo>/<modulo>.js',
]

CSS_FILES = [
    'static/css/core/reset.css',
    'static/css/core/responsive.css',
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',
    'static/css/components/modal.css',
    'static/css/components/modal_confirmacao.css',
    'static/css/components/modal_auditoria.css',
    'static/css/components/form.css',
    'static/css/components/notificacoes.css',
    'static/css/modules/pasta_<modulo>/<modulo>.css',
]
9.2 Saída
static/js/modules/pasta_<modulo>/<modulo>.min.js

static/css/modules/pasta_<modulo>/<modulo>.min.css

9.3 Uso no template
jinja
<link rel="stylesheet" href="{{ static_v('css/modules/pasta_<modulo>/<modulo>.min.css') }}">
...
<script src="{{ static_v('js/modules/pasta_<modulo>/<modulo>.min.js') }}"></script>
10. Banco de Dados
10.1 Colunas obrigatórias em TODA tabela principal
sql
id SERIAL PRIMARY KEY,
usuario_id INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
sequencia_<modulo> INTEGER,
numero VARCHAR(30),
<campos específicos>
valor_total NUMERIC(12,2) DEFAULT 0,
ativo INTEGER DEFAULT 1,
excluido_em TIMESTAMP,
excluido_por INTEGER,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
10.2 Índices obrigatórios
Único: (usuario_id, sequencia_<modulo>)

Busca: (usuario_id, ativo)

Data: (data_emissao DESC)

Status: (status)

Número: (numero)

10.3 Convenções
Elemento	Padrão
Tabela principal	<plural> (ex: tarefas, transacoes)
Tabela auditoria	<plural>_auditoria
ID interno	id (SERIAL)
ID do usuário	usuario_id
Sequência visual	sequencia_<singular>
Número formatado	numero
Soft delete	ativo (1/0)
Exclusão	excluido_em, excluido_por
11. Módulos Existentes
11.1 Tarefas (rotas/pasta_tarefas/) — ✅ 2099
Tabela: tarefas + tarefas_auditoria

Endpoint: /tarefas/

Estrutura completa: insert/edit/delete/reativar/concluir/reabrir

Filtros: data, categoria, status, prioridade, descrição

11.2 Finanças (rotas/pasta_financas/) — ✅ 2099
Tabela: transacoes + financas_auditoria

Endpoint: /financas/

Estrutura completa: insert/edit/delete/reativar
Estrutura completa: insert/edit/delete/reativar/quitar/estornar

Parcelamento (PAI + FILHAS)

Categorias agora unificadas (tabela categorias com modulo='financas')

11.3 Orçamentos (rotas/pasta_orcamentos/) — ✅ 2099
Tabela: orcamentos + orcamentos_auditoria

Endpoint: /orcamentos/

Estrutura JSONB (estrutura)

PDF (WeasyPrint)

11.4 Categorias (rotas/pasta_categorias/) — ✅ 2099
Tabela: categorias (unificada) + categorias_auditoria

Endpoint: /categorias/

2 módulos: 'tarefas' e 'financas' (coluna modulo)

CRUD completo + auditoria

Modal inline (botão + nos modais de Tarefa/Finança)

11.5 Login (rotas/pasta_login/)
Login, Cadastro, Recuperar Senha

Tabela: cadastre_se

11.6 Dashboard (rotas/pasta_dashboard/)
Pós-login

11.7 Auditoria (rotas/auditoria_geral/)
bp_auditoria único

Rotas: /auditoria/tarefa/<seq>, /transacao/<id>, /orcamento/<seq>, /categoria/<id>

11.8 Logs (rotas/logs/)
Logs de acesso, erros, ataques

12. Princípios Invioláveis
Backend
View magra — regra de negócio vai pro services.py

Service NÃO faz commit — quem faz é a view (transacional)

Validação backend SEMPRE — front é burlável

Sequência visual por usuário — cada user tem seu #1, #2, #3

Número formatado único — ORC-2026-0001, TAR-2026-0001, CAT-2026-0001

Soft delete SEMPRE — UPDATE ativo = 0, nunca DELETE FROM

Colunas explícitas no SELECT — dict(zip(colunas, row)), nunca dict(row)

Auditoria SEMPRE na view, transacional — mesma conexao

FK da auditoria = id interno — não sequência visual

JSON de alterações = [{campo, antes, depois}] quando campo_alterado='multiplos'

Frontend
HTMX puro — front só abre/fecha modal, backend devolve HTML + HX-Trigger

1 arquivo = 1 responsabilidade — 1 JS por ação

Pós-insert = htmx.ajax — nunca window.location.reload()

Sem setTimeout fixo — usar htmx:afterSwap

Sem onclick inline — sempre data-* + listener JS (exceção: botões dentro de partials HTMX)

Validação campo-a-campo no front — borda vermelha + mensagem por campo

Prefixos CSS por módulo — .cat-, .tar-, .orc- (evita colisão)

Geral
Respostas sempre 200 — HTMX ignora HX-Trigger em 4xx/5xx

CSS compartilhado em components/ — não duplicar por módulo

JS compartilhado em static/js/components/ — quando faz sentido

Anti-padrões (NUNCA fazer)
❌ dict(row) — quebra em colunas dinâmicas

❌ DELETE FROM — perde histórico

❌ window.location.reload() pós-insert — perde scroll/filtros

❌ setTimeout(50) pra sync HTMX — quebra em prod (200ms latência)

❌ required no HTML — front é burlável

❌ onclick="funcao()" inline — dificulta manutenção

❌ CSS no JS_FILES — quebra o bundle

❌ Auditoria com sequencia — FK tem que ser id interno

❌ campo_alterado='todos' — usar 'multiplos'

❌ CSS sem prefixo em módulo — colide com outros módulos

📌 Comandos Úteis
Deploy produção
bash
cd /var/www/vhorganiza
git pull origin main
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
sudo systemctl restart gestao_financeira
sudo systemctl status gestao_financeira
Criar tabelas no produção (após pull com tabela nova)
bash
cd /var/www/vhorganiza
source venv/bin/activate
python -c "from config.database import criar_todas_tabelas; criar_todas_tabelas()"
Ver logs em tempo real
bash
sudo journalctl -u gestao_financeira -f
Build (local)
bash
python scripts/combine_static_tarefas.py
python scripts/combine_static_financas.py
python scripts/combine_static_orcamentos.py
python scripts/combine_static_categorias.py
Rodar Flask local
bash
python app.py
🔥 Observações Finais
Latência prod: ~200ms (Brasil ↔ Alemanha). SEMPRE testar com isso em mente.

Cache busting: static_v() gera hash do conteúdo.

dict(zip(colunas, row)) sempre que precisar converter tupla em dict.

Prefixos CSS por módulo — sem isso, colisões acontecem.

Sempre rodar criar_todas_tabelas() no produção após git pull que adiciona tabela nova.

Modais: 2 sistemas coexistindo:

.fin-modal-* (full-screen, Categorias)

.modal-confirmacao-* (pequeno, Tarefas/Finanças/Orçamentos)

TODO: padronizar num só

Fim do mapa do projeto.

text

---
