# 04 — Backend

## 4.1 Blueprint principal (`__init__.py`)

```python
from flask import Blueprint

bp_<modulo> = Blueprint('<modulo>', __name__)

from .<modulo> import ini_<modulo>, detalhes_<x>, limpar_filtros
from .crud.pasta_insert   import bp_insert
from .crud.pasta_edit     import bp_edit
from .crud.pasta_delete   import bp_delete

bp_<modulo>.add_url_rule('/', view_func=ini_<modulo>, methods=['GET', 'POST'])
bp_<modulo>.add_url_rule('/limpar_filtros', view_func=limpar_filtros)

bp_<modulo>.register_blueprint(bp_insert, url_prefix='')
bp_<modulo>.register_blueprint(bp_edit,   url_prefix='')
```

**⚠️ IMPORTANTE:** o `url_prefix` varia por módulo.

## 4.2 View magra — só orquestra

**❌ ERRADO (faz tudo na view):**
```python
@login_required
def criar_orcamento():
    dados = request.get_json()
    # ... valida
    # ... calcula sequência
    # ... INSERT
    # ... auditoria
    return jsonify(...)
```

**✅ CORRETO (view só orquestra):**
```python
from .services import InserirOrcamentoService
from .validacoes import validar_dados_insercao, limpar_texto, calcular_valor_total

@login_required
def criar_orcamento():
    user_id = session['user_id']
    conexao = None
    try:
        payload = request.get_json() or {}

        # 1. Sanitiza
        estrutura = payload.get('estrutura') or []
        dados = {
            'titulo':        limpar_texto(payload.get('titulo'), max_len=200),
            'cliente':       limpar_texto(payload.get('cliente'), max_len=200),
            'status':        (payload.get('status') or 'rascunho').strip().lower(),
            'estrutura':     estrutura,
            'valor_total':   calcular_valor_total(estrutura),
            'data_emissao':  payload.get('data_emissao') or None,
            'data_validade': payload.get('data_validade') or None,
            'data_entrega':  payload.get('data_entrega') or None,
        }

        # 2. Valida (backend)
        erros = validar_dados_insercao(dados)
        if erros:
            return jsonify({'success': False, 'errors': erros}), 200

        # 3. Insere
        conexao, cursor = ini_conexao()
        sucesso, resultado = InserirOrcamentoService.criar_orcamento(cursor, user_id, dados)
        if not sucesso:
            conexao.rollback()
            return jsonify({'success': False, 'message': resultado}), 400

        # 4. Auditoria
        alteracoes = InserirOrcamentoService.montar_alteracoes_auditoria(dados, resultado)
        AuditoriaOrcamentosService.registrar(
            orcamento_id=resultado['id'],
            acao='criada',
            campo_alterado='multiplos',
            valor_antigo=None,
            valor_novo=json.dumps(alteracoes, ensure_ascii=False),
            conexao=conexao,
        )

        conexao.commit()
        return jsonify({
            'success': True,
            'message': f'Orçamento "{dados["titulo"]}" criado!',
            'id': resultado['id'],
            'sequencia': resultado['sequencia'],
            'numero': resultado['numero'],
        }), 201

    except Exception as e:
        if conexao:
            conexao.rollback()
        logger.exception(f"Erro ao criar user_id={user_id}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
```

## 4.3 Services — regras de negócio

**`services.py` (do insert) tem:**
- `get_proxima_sequencia(cursor, user_id)` → `MAX + 1`
- `gerar_numero(sequencia, ano)` → `ORC-2026-0004`
- `criar_<x>(cursor, user_id, dados)` → INSERT
- `montar_alteracoes_auditoria(dados, resultado)` → lista de dicts

**Regra:** service **não faz commit**. Quem faz é a view.

## 4.4 Validações backend — SEMPRE

**`validacoes.py`:**
- `limpar_texto(valor, max_len)` — sanitiza
- `parse_valor_br(valor_str)` — `"R$ 150,00"` → `150.0`
- `calcular_valor_total(estrutura)` — soma dos blocos tipo `valor`
- `validar_dados_insercao(dados)` — `[{campo, mensagem}]`

## 4.5 View HTMX — devolve HTML + HX-Trigger

```python
@login_required
def excluir_orcamento(sequencia):
    user_id = session['user_id']
    conexao, cursor = ini_conexao()
    try:
        # 1. Busca id_interno + título ANTES
        cursor.execute("""
            SELECT id, titulo FROM orcamentos
            WHERE sequencia_orcamentos = %s AND usuario_id = %s AND ativo = 1
        """, (sequencia, user_id))
        resultado = cursor.fetchone()
        if not resultado:
            return '', 404

        id_interno, titulo = resultado[0], resultado[1]

        # 2. Inativa (soft delete)
        cursor.execute(OrcamentosQueries.inativar_orcamento(), (user_id, sequencia, user_id))

        # 3. Auditoria transacional
        AuditoriaOrcamentosService.registrar(
            orcamento_id=id_interno,
            acao='inativada',
            campo_alterado='ativo',
            valor_antigo='1',
            valor_novo='0',
            conexao=conexao,
        )

        conexao.commit()

        # 4. Retorna HTML + HX-Trigger
        html = _render_tbody(user_id, cursor)
        resp = make_response(html)
        resp.headers['HX-Trigger'] = json.dumps({
            'orcamentoInativado': {'message': f'Orçamento "{titulo}" inativado!'}
        })
        return resp

    except Exception as e:
        conexao.rollback()
        logger.exception(f"Erro: {e}")
        return '', 500
```

## 4.6 Helpers duplicados em TODOS os CRUDs

```python
def _buscar_<x>_com_filtros(cursor, user_id):
    data_inicio, data_fim, tipo_data = <Modulo>Filters.processar_filtros_data()
    filtros = <Modulo>Filters.recuperar_filtros(session)
    filtros.update({
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_data': tipo_data,
    })
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
```

## 4.7 Filtros

- Data: `data_emissao` (não `created_at`)
- Tipo data: `'emissao'` (nunca `'inicio'`)
- Mostrar inativas: `'0'`, `'1'`, `'2'`

## 4.8 Sequência visual

```python
@staticmethod
def get_proxima_sequencia(cursor, user_id):
    cursor.execute("""
        SELECT COALESCE(MAX(sequencia_<modulo>), 0) + 1
        FROM <tabela>
        WHERE usuario_id = %s
    """, (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 1
```

## 4.9 Número formatado

```python
@staticmethod
def gerar_numero(sequencia, ano=None):
    if ano is None:
        ano = date.today().year
    return f'ORC-{ano}-{str(sequencia).zfill(4)}'
```

**Prefixos:** `ORC-`, `TAR-`, `TRN-`