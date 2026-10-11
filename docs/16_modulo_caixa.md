# Backlog — Módulo Caixa / Contas Bancárias / Importação OFX

**Status:** 📋 Planejamento (não iniciar agora)
**Criado em:** 11/10/2026
**Pré-requisitos:** Tarefas 2099 + Categorias 2099 100% em produção
**Estimativa:** 40-60h (1-2 meses)

---

## 📑 Índice

1. [Visão Geral](#1-visão-geral)
2. [Modelo de Dados](#2-modelo-de-dados)
3. [Estrutura de Pastas](#3-estrutura-de-pastas)
4. [Backend 2099 (CRUDs)](#4-backend-2099-cruds)
5. [Frontend (Templates + JS + CSS)](#5-frontend-templates--js--css)
6. [Auditoria](#6-auditoria)
7. [Migração de Dados](#7-migração-de-dados)
8. [Importação OFX](#8-importação-ofx)
9. [Conciliação Bancária](#9-conciliação-bancária)
10. [Relatórios](#10-relatórios)
11. [Cronograma por Fases](#11-cronograma-por-fases)
12. [Impactos nos Módulos Existentes](#12-impactos-nos-módulos-existentes)
13. [Checklist de Implementação](#13-checklist-de-implementação)
14. [Referências](#14-referências)

---

## 1. Visão Geral

### 🎯 Objetivo

Transformar o módulo Finanças num **sistema de controle financeiro profissional**, com:

- **Contas** separadas (Nubank, Itaú, Poupança, Carteira, Cartão)
- **Saldo consolidado** (caixa)
- **Importação de OFX** dos bancos
- **Conciliação bancária** (matching entre OFX e transações)
- **Relatórios** de fluxo de caixa

### 💡 Motivação

O controle financeiro atual é "flat" — todas as transações caem num balde só. Falta granularidade:

- De qual conta saiu?
- Qual o saldo real de cada uma?
- O extrato do banco bate com o sistema?

### 🏗 Arquitetura
┌─────────────────────────────────────────┐
│ 1. CONTAS (onde o dinheiro tá) │
│ - Conta Corrente Nubank │
│ - Conta Poupança Itaú │
│ - Carteira (dinheiro físico) │
│ - Cartão de Crédito │
└─────────────────────────────────────────┘
↓
┌─────────────────────────────────────────┐
│ 2. CAIXA (saldo consolidado) │
│ - Quanto tem em cada conta │
│ - Quanto tem no total │
│ - Movimentações (entrada/saída) │
└─────────────────────────────────────────┘
↓
┌─────────────────────────────────────────┐
│ 3. TRANSAÇÕES (o que entra/sai) │
│ - Receita (salário, freelance) │
│ - Despesa (aluguel, mercado) │
│ - Transferência (entre contas) │
│ - Cada uma vinculada a UMA conta │
└─────────────────────────────────────────┘


---

## 2. Modelo de Dados

### 2.1 Tabela `contas`

```sql
CREATE TABLE contas (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
    nome            TEXT NOT NULL,
    tipo            TEXT NOT NULL,            -- 'corrente' | 'poupanca' | 'carteira' | 'cartao' | 'investimento'
    banco           TEXT,                     -- 'Nubank' | 'Itaú' | 'Inter' | ...
    agencia         VARCHAR(20),
    conta           VARCHAR(30),
    saldo_inicial   NUMERIC(12,2) DEFAULT 0,
    cor             TEXT DEFAULT '#3b82f6',
    icone           TEXT DEFAULT 'bi-bank',
    ativo           INTEGER DEFAULT 1,
    excluido_em     TIMESTAMP,
    excluido_por    INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_contas_usuario_id ON contas(usuario_id);
CREATE INDEX idx_contas_usuario_ativo ON contas(usuario_id, ativo);
CREATE INDEX idx_contas_usuario_tipo ON contas(usuario_id, tipo);


2.2 Tabelas caixas + caixa_contas (agrupamento opcional)
sql
CREATE TABLE caixas (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES cadastre_se(id) ON DELETE CASCADE,
    nome        TEXT NOT NULL,
    cor         TEXT DEFAULT '#3b82f6',
    ativo       INTEGER DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE caixa_contas (
    caixa_id  INTEGER REFERENCES caixas(id) ON DELETE CASCADE,
    conta_id  INTEGER REFERENCES contas(id) ON DELETE CASCADE,
    PRIMARY KEY (caixa_id, conta_id)
);

-- Índices
CREATE INDEX idx_caixas_usuario_id ON caixas(usuario_id);
CREATE INDEX idx_caixa_contas_conta ON caixa_contas(conta_id);


2.3 Alteração na tabela transacoes
sql
ALTER TABLE transacoes
    ADD COLUMN conta_id         INTEGER REFERENCES contas(id) ON DELETE SET NULL,
    ADD COLUMN conciliada       BOOLEAN DEFAULT FALSE,
    ADD COLUMN ofx_id           VARCHAR(100),
    ADD COLUMN ofx_importado_em TIMESTAMP;

CREATE INDEX idx_transacoes_conta_id ON transacoes(conta_id);
CREATE INDEX idx_transacoes_usuario_conta ON transacoes(usuario_id, conta_id);
CREATE INDEX idx_transacoes_ofx_id ON transacoes(ofx_id);
CREATE INDEX idx_transacoes_conciliada ON transacoes(conciliada);


2.4 Tabelas OFX (staging)
sql
CREATE TABLE ofx_importacoes (
    id                 SERIAL PRIMARY KEY,
    usuario_id         INTEGER REFERENCES cadastre_se(id),
    conta_id           INTEGER REFERENCES contas(id),
    arquivo_nome       TEXT,
    importado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_transacoes   INTEGER DEFAULT 0,
    processadas        INTEGER DEFAULT 0,
    ignoradas          INTEGER DEFAULT 0,
    status             TEXT DEFAULT 'pendente'
);

CREATE TABLE ofx_transacoes (
    id                 SERIAL PRIMARY KEY,
    importacao_id      INTEGER REFERENCES ofx_importacoes(id) ON DELETE CASCADE,
    fitid              VARCHAR(100),
    tipo               TEXT,
    valor              NUMERIC(12,2),
    data               DATE,
    descricao          TEXT,
    memo               TEXT,
    categoria_sugerida INTEGER REFERENCES categorias(id),
    conciliada         BOOLEAN DEFAULT FALSE,
    transacao_id       INTEGER REFERENCES transacoes(id) ON DELETE SET NULL
);

CREATE INDEX idx_ofx_importacoes_usuario ON ofx_importacoes(usuario_id);
CREATE INDEX idx_ofx_importacoes_conta ON ofx_importacoes(conta_id);
CREATE INDEX idx_ofx_transacoes_importacao ON ofx_transacoes(importacao_id);
CREATE INDEX idx_ofx_transacoes_fitid ON ofx_transacoes(fitid);


2.5 Auditoria
sql
CREATE TABLE contas_auditoria (
    id SERIAL PRIMARY KEY,
    conta_id INTEGER REFERENCES contas(id),
    acao VARCHAR(50),
    campo_alterado VARCHAR(100),
    valor_antigo TEXT,
    valor_novo TEXT,
    usuario_id INTEGER REFERENCES cadastre_se(id),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45)
);

3. Estrutura de Pastas
3.1 Backend
text
rotas/pasta_contas/
├── __init__.py                      # bp_contas + register_blueprint
├── contas.py                        # view principal (listar)
├── queries.py                       # ContasQueries
├── filters.py                       # ContasFilters
├── formatters.py                    # ContasFormatters
├── services/
│   └── services_contas.py           # ContasServices
├── crud/
│   ├── pasta_insert/
│   │   ├── __init__.py
│   │   ├── insert_conta.py          # JSON + auditoria
│   │   ├── services.py              # InserirContaService
│   │   └── validacoes.py
│   ├── pasta_edit/
│   │   ├── __init__.py
│   │   ├── edit_conta.py            # JSON + diff + auditoria
│   │   ├── services.py
│   │   └── validacoes.py
│   ├── pasta_delete/
│   │   ├── __init__.py
│   │   ├── delete_conta.py          # HTML + HX-Trigger
│   │   └── services.py
│   └── pasta_reativar/
│       ├── __init__.py
│       ├── reativar_conta.py
│       └── services.py
└── tabela/
    └── tabela_contas.py
3.2 Frontend
text
templates/pasta_contas/
├── tela_contas.html.jinja
├── _tabela_contas.html.jinja
├── partials/
│   ├── _tbody_contas.html.jinja
│   └── _linha_conta.html.jinja
└── modais/
    ├── modal_nova_conta.html.jinja
    ├── modal_editar_conta.html.jinja
    └── modal_excluir_conta.html.jinja

static/js/modules/pasta_contas/
├── contas.js
├── core/
│   └── ContaForm.js
├── modals/
│   ├── conta-nova.js
│   └── conta-editar.js
└── acoes_e_modais/
    ├── pasta_excluir/excluir_conta.js
    └── pasta_reativar/reativar_conta.js

static/css/modules/pasta_contas/
└── contas.css
3.3 Auditoria
text
rotas/auditoria_geral/pasta_contas/
├── tabela.py
├── services_auditoria.py
└── logica_auditoria.py
4. Backend 2099 (CRUDs)
4.1 Blueprint principal (rotas/pasta_contas/__init__.py)
python
from flask import Blueprint

bp_contas = Blueprint('contas', __name__)

from .contas import ini_contas, limpar_filtros
from .crud.pasta_insert   import bp_insert
from .crud.pasta_edit     import bp_edit
from .crud.pasta_delete   import bp_delete
from .crud.pasta_reativar import bp_reativar

bp_contas.add_url_rule('/', view_func=ini_contas, methods=['GET', 'POST'])
bp_contas.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

bp_contas.register_blueprint(bp_insert,    url_prefix='/nova_conta')
bp_contas.register_blueprint(bp_edit,      url_prefix='/edit_contas')
bp_contas.register_blueprint(bp_delete,    url_prefix='/excluir_conta')
bp_contas.register_blueprint(bp_reativar,  url_prefix='/reativar_conta')
4.2 View principal (contas.py)
Segue o padrão de Tarefas (view magra, filtros da sessão, HTMX):

python
@login_required
def ini_contas():
    usuario_id = session['user_id']
    is_htmx = request.headers.get('HX-Request') == 'true'

    # 1. FILTROS
    descricao_filtro = ContasFilters.filtro_descricao()
    mostrar_inativas = ContasFilters.processar_mostrar_inativas()
    tipo_filtro      = ContasFilters.filtro_tipo()

    # 2. QUERY
    filtros = {...}
    service = ContasServices(conexao=None, cursor=cursor)
    contas_raw = service.buscar_contas(usuario_id, filtros)
    contas = ContasFormatters.formatar_contas(contas_raw)

    # 3. HTMX ou completo
    if is_htmx:
        return _renderizar_htmx(...)
    return render_template('pasta_contas/tela_contas.html.jinja', ...)
4.3 CRUD — Insert (crud/pasta_insert/insert_conta.py)
Segue o padrão 2099:

python
@login_required
def salvar_nova_conta():
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()
    try:
        payload = request.json or {}
        dados = {
            'nome':          (payload.get('nome') or '').strip(),
            'tipo':          (payload.get('tipo') or '').strip(),
            'banco':         (payload.get('banco') or '').strip(),
            'saldo_inicial': float(payload.get('saldo_inicial') or 0),
            'cor':           (payload.get('cor') or '#3b82f6').strip(),
        }

        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        sucesso, resultado = InserirContaService.criar_conta(cursor, usuario_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado}), 400

        # Auditoria
        alteracoes = [
            {'campo': 'Nome',          'depois': dados['nome']},
            {'campo': 'Tipo',          'depois': dados['tipo']},
            {'campo': 'Banco',         'depois': dados['banco'] or '(vazio)'},
            {'campo': 'Saldo Inicial', 'depois': f"R$ {dados['saldo_inicial']:.2f}"},
        ]
        AuditoriaContasService.registrar(
            conta_id=resultado['conta_id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()
        return jsonify({
            'success': True,
            'message': f'Conta "{dados["nome"]}" criada!',
            'conta_id': resultado['conta_id'],
        }), 201
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao criar conta")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()
4.4 CRUD — Edit (crud/pasta_edit/edit_conta.py)
Segue o padrão 2099 com _montar_diff:

python
@login_required
def salvar_edicao_conta(conta_id):
    usuario_id = session.get('user_id')
    conexao, cursor = ini_conexao()
    try:
        payload = request.json or {}
        dados = {...}

        erros = validar_dados_edicao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        resultado = EditarContaService.atualizar_conta(cursor, conta_id, usuario_id, dados)
        if not resultado['success']:
            conexao.rollback()
            return jsonify({'success': False, 'error': resultado['error']}), 400

        # Auditoria com diff
        alteracoes = _montar_diff(resultado['dados_antes'], resultado['dados_depois'])
        if alteracoes:
            AuditoriaContasService.registrar(
                conta_id=resultado['id_interno'],
                acao='editada',
                campo_alterado='multiplos' if len(alteracoes) > 1 else alteracoes[0]['campo'].lower(),
                valor_novo=json.dumps(alteracoes, ensure_ascii=False),
                conexao=conexao,
            )

        conexao.commit()
        return jsonify({'success': True, 'message': 'Conta atualizada!'}), 200
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao editar conta")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conexao.close()
4.5 CRUD — Delete (crud/pasta_delete/delete_conta.py)
Soft delete + HTML + HX-Trigger:

python
@login_required
def inativar_conta_view(conta_id):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        conta = InativarContaService.buscar_conta(cursor, conta_id, user_id)
        if not conta:
            conexao.close()
            return '', 404

        nome = conta[1]
        InativarContaService.inativar_conta(cursor, conta_id, user_id)

        AuditoriaContasService.registrar(
            conta_id=conta_id,
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
            'contaInativada': {'message': f'Conta "{nome}" inativada!'}
        })
        return resp
    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro ao inativar conta")
        conexao.close()
        return '', 500
4.6 CRUD — Reativar (crud/pasta_reativar/reativar_conta.py)
Mesma estrutura do delete, mas invertendo ativo = 0 → 1.

5. Frontend (Templates + JS + CSS)
5.1 Tela principal (tela_contas.html.jinja)
Layout de grid de cards (não tabela):

text
┌────────────────────────────────────────────────────┐
│  CONTAS                          [+ NOVO]           │
├────────────────────────────────────────────────────┤
│  🔍 [buscar]    [Corrente|Poupança|Cartão|Todas]   │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │ Nubank       │  │ Itaú         │  │ Carteira ││
│  │ Corrente     │  │ Poupança     │  │ Dinheiro ││
│  │ R$ 3.450,00  │  │ R$ 12.000,00 │  │ R$ 150,00││
│  │ [Editar][X]  │  │ [Editar][X]  │  │ [Editar] ││
│  └──────────────┘  └──────────────┘  └──────────┘│
└────────────────────────────────────────────────────┘
5.2 JS — ContaForm.js (core compartilhado)
Mesma estrutura do CategoriaForm.js:

mode: 'create' | 'edit'

init() — pega os campos

getData() — serializa pro POST

submit(url) — fetch JSON + validação campo-a-campo

Pós-sucesso: htmx.ajax recarrega a tabela

5.3 JS — conta-nova.js e conta-editar.js
Modais HTMX (iguais aos de Categoria):

Abrem via hx-get

Injetam no #modal-nova-container / #modal-editar-container

Inicializam o ContaForm

Fecham no sucesso

5.4 CSS — contas.css (prefixo .ct-)
Seguindo o padrão de Categorias (prefixo pra evitar colisão):

css
.ct-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.ct-card { background: var(--bg-card); border-radius: 12px; padding: 16px; }
.ct-card-titulo { font-weight: 600; }
.ct-card-saldo { font-size: 1.5rem; color: var(--cor-ativa); }
.ct-btn-acao { ... }
6. Auditoria
6.1 Tabela contas_auditoria
Já mostrada na seção 2.5.

6.2 Service (services_auditoria.py)
Padrão 2099 (igual Categorias):

python
class AuditoriaContasService:
    @staticmethod
    def registrar(conta_id, acao, campo_alterado=None,
                  valor_antigo=None, valor_novo=None, conexao=None):
        # ... mesmo padrão de Tarefas/Finanças/Categorias
6.3 View (logica_auditoria.py)
Traduz conta_id → renderiza modal de auditoria.

7. Migração de Dados
7.1 Criar conta "Geral"
Antes de adicionar conta_id em transacoes, criar uma conta default pra todos os usuários que têm transações:

sql
INSERT INTO contas (usuario_id, nome, tipo, saldo_inicial, cor, icone, ativo)
SELECT DISTINCT
    usuario_id,
    'Geral',
    'carteira',
    0,
    '#6c757d',
    'bi-wallet2',
    1
FROM transacoes
WHERE usuario_id IS NOT NULL;

-- Vincular todas as transações
UPDATE transacoes t
SET conta_id = (
    SELECT c.id FROM contas c
    WHERE c.usuario_id = t.usuario_id AND c.nome = 'Geral'
)
WHERE t.conta_id IS NULL;
7.2 Rollback
Criar script de rollback pra reverter a migração, se necessário.

8. Importação OFX
8.1 Biblioteca
Usar ofxparse (mais estável) ou ofxtools (mais moderno).

bash
pip install ofxparse
8.2 Fluxo
Usuário faz upload do .ofx

Backend faz parse (extrai fitid, valor, data, descricao, memo)

Salva em ofx_importacoes + ofx_transacoes (staging)

Mostra preview (checkbox por transação)

Usuário seleciona quais importar

Backend cria transacoes + marca como conciliada = TRUE + ofx_id = fitid

8.3 Deduplicação
Antes de importar, checar se fitid já existe em transacoes.ofx_id. Se sim, pular.

8.4 Auto-categorização
Tabela de regras:

sql
CREATE TABLE ofx_regras_categorizacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES cadastre_se(id),
    palavra_chave TEXT NOT NULL,
    categoria_id INTEGER REFERENCES categorias(id),
    prioridade INTEGER DEFAULT 0
);
Ex: "SUPERMERCADO" → categoria "Alimentação".

9. Conciliação Bancária
9.1 Matching automático
Pra cada ofx_transacoes não conciliada, procurar transacoes que bata em:

Valor (exato)

Data (± 3 dias)

Descrição (fuzzy match)

Se achar 1 → conciliar automaticamente.
Se achar > 1 → mostrar pro usuário escolher.

9.2 Matching manual
Tela com 2 colunas:

text
┌──────────────────────┐  ┌──────────────────────┐
│  OFX (banco)         │  │  SISTEMA (manual)    │
│  - R$ 150,00 10/10   │  │  - R$ 150,00 10/10   │ ← conciliar
│  - R$ 80,00  11/10   │  │  - R$ 80,00  11/10   │ ← conciliar
└──────────────────────┘  └──────────────────────┘
9.3 Relatório de divergências
No banco mas não no sistema → esqueceram de lançar

No sistema mas não no banco → lançaram errado, ou ainda não caiu

10. Relatórios
10.1 Fluxo de caixa (mensal)
text
Mês: Outubro/2026

Entradas:   R$ 8.500,00
Saídas:     R$ 6.200,00
Saldo:      R$ 2.300,00

Por conta:
- Nubank:    +R$ 5.000,00  -R$ 3.200,00  = R$ 1.800,00
- Itaú:      +R$ 3.500,00  -R$ 3.000,00  = R$ 500,00
10.2 Extrato por conta
Filtro por conta, período, tipo.

10.3 Gráfico de entradas/saídas
Chart.js (já deve ter no projeto).

10.4 Exportar
PDF (WeasyPrint — já tem no projeto)

Excel (openpyxl)

11. Cronograma por Fases
Fase	Descrição	Horas	Prioridade
1	CRUD de Contas	8-10h	🔴 Alta
2	Caixa / Saldo	6-8h	🔴 Alta
3	Importação OFX	12-16h	🟡 Média
4	Conciliação	8-10h	🟡 Média
5	Relatórios	8-10h	🟢 Baixa
Total		40-60h	
Pré-requisitos antes de começar
✅ Módulo Finanças 2099 concluído

✅ Módulo Tarefas 2099 concluído

✅ Módulo Categorias 2099 concluído

✅ Auditoria funcionando em todos

✅ Backup do banco antes da migração

12. Impactos nos Módulos Existentes
12.1 No módulo Finanças
Tabela transacoes ganha 4 colunas (conta_id, conciliada, ofx_id, ofx_importado_em)

Migração obrigatória: criar conta "Geral" + vincular transações existentes

Refatoração do CRUD: modal de Nova Transação ganha select de conta

Quitar/Estornar: mantém a conta

12.2 No módulo Categorias
Nenhum impacto — categorias continuam como estão

12.3 No módulo Orçamentos
Futuro: orçamentos podem vincular a conta (não é pré-requisito)

12.4 No módulo Tarefas
Nenhum impacto

13. Checklist de Implementação
Backend
□ Criar tabelas (contas, caixas, caixa_contas, ofx_importacoes, ofx_transacoes, contas_auditoria)
□ Adicionar colunas em transacoes
□ Migrar dados (criar conta "Geral" + vincular)
□ Criar rotas/pasta_contas/ (backend 2099)
□ Criar rotas/auditoria_geral/pasta_contas/
□ Registrar bp_contas no imports_rotas.py
□ Adicionar tabela_contas no config/database.py
□ Adicionar índices no indices_automatico.py
Frontend
□ templates/pasta_contas/tela_contas.html.jinja
□ templates/pasta_contas/_tabela_contas.html.jinja
□ Partial _tbody_contas.html.jinja
□ Partial _linha_conta.html.jinja
□ Modais (modal_nova_conta, modal_editar_conta, modal_excluir_conta)
□ JS (ContaForm, conta-nova, conta-editar, excluir_conta, reativar_conta)
□ CSS contas.css (prefixo .ct-)
□ Build (combine_static_contas.py)
□ Link no menu lateral
Importação OFX
□ Instalar ofxparse
□ View de upload
□ Parser OFX
□ Preview de transações
□ Importação seletiva
□ Deduplicação por fitid
□ Auto-categorização (regras)
Conciliação
□ Matching automático
□ Tela de conciliação manual
□ Marcar como conciliada
□ Relatório de divergências
Relatórios
□ Fluxo de caixa
□ Extrato por conta
□ Gráfico entradas/saídas
□ Exportar PDF
□ Exportar Excel
14. Referências
Bibliotecas OFX
ofxparse — https://pypi.org/project/ofxparse/

ofxtools — https://pypi.org/project/ofxtools/

python-ofx — https://pypi.org/project/python-ofx/

Padrão de mercado
Mobills — controle financeiro completo com OFX

Organizze — conciliação bancária

GuiaBolso — importação OFX (descontinuado)

Artigos
Como funciona conciliação bancária (Nubank/Itaú)

OFX vs CSV vs CNAB (formatos de extrato)

📝 Notas Finais
Refatoração do Finanças — a tabela transacoes ganha conta_id. Migração obrigatória.

Importação OFX é o "pulo do gato" — 80% do trabalho manual é eliminado.

Conciliação é o diferencial — garante que o sistema tá igual ao banco.

Fazer em fases — não tentar fazer tudo de uma vez.

Cada fase é um "módulo" completo — backend + frontend + testes + produção.

Fim do backlog.

text

---

## 📥 SALVA ISSO

**No PowerShell:**

```powershell
mkdir docs\backlog -Force
notepad docs\backlog\caixa_contas_ofx.md
Aí cola tudo e salva. Agora tá completo — tabelas + CRUDs + frontend + auditoria + migração + OFX + conciliação + relatórios + cronograma. Tudo em 1 arquivo.