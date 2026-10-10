# scripts/refatorar_user_id.py
# ==========================================================
# Refatora 'user_id' → 'usuario_id' (SÓ EM SQL)
# ----------------------------------------------------------
# ⚠️ CONSERVADOR: só troca padrões SQL específicos
# ⚠️ NÃO troca: session, URLs, variáveis, comentários, f-strings
# ⚠️ FAZ BACKUP antes de cada mudança
# ⚠️ PRINTA cada troca pra você conferir
# ==========================================================

import os
import re
import shutil
from datetime import datetime

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
PASTAS = [
    'rotas/pasta_financas',
    'rotas/pasta_tarefas',
    'rotas/pasta_dashboard',
    'rotas/auditoria_geral',
    'rotas/logs',
    # 'rotas/pasta_categorias',   # 🔥 Refatora separado (vai mudar muito)
    # 'rotas/pasta_login',        # ❌ NÃO — usa user_id como URL/session
    # 'rotas/pasta_orcamentos',   # ❌ SQL já usa usuario_id (variáveis ok)
]

# Padrões que DEVEM ser trocados (SÓ estes)
PADROES_TROCA = [
    # WHERE user_id → WHERE usuario_id
    (r'\bWHERE\s+user_id\b', 'WHERE usuario_id'),
    (r'\bAND\s+user_id\b', 'AND usuario_id'),
    (r'\bOR\s+user_id\b', 'OR usuario_id'),

    # user_id = %s → usuario_id = %s
    (r'\buser_id\s*=\s*%s', 'usuario_id = %s'),

    # user_id INTEGER (CREATE TABLE)
    (r'\buser_id\s+INTEGER\b', 'usuario_id INTEGER'),

    # FOREIGN KEY (user_id) REFERENCES
    (r'FOREIGN\s+KEY\s*\(\s*user_id\s*\)', 'FOREIGN KEY (usuario_id)'),

    # UNIQUE(user_id, ...
    (r'UNIQUE\s*\(\s*user_id\s*,', 'UNIQUE(usuario_id,'),

    # (user_id, ... (tupla SQL)
    (r'\(\s*user_id\s*,', '(usuario_id,'),

    # , user_id, ... (meio da tupla)
    (r',\s*user_id\s*,', ', usuario_id,'),

    # , user_id) (fim da tupla)
    (r',\s*user_id\s*\)', ', usuario_id)'),

    # (user_id) (tupla com 1)
    (r'\(\s*user_id\s*\)', '(usuario_id)'),

    # user_id, (primeiro da tupla)
    (r'\buser_id\s*,', 'usuario_id,'),

    # Aliases de tabela
    (r'\bt\.user_id\b', 't.usuario_id'),
    (r'\bo\.user_id\b', 'o.usuario_id'),
    (r'\bla\.user_id\b', 'la.usuario_id'),
    (r'\bc\.user_id\b', 'c.usuario_id'),

    # user_id ordenação
    (r'ORDER\s+BY\s+user_id\b', 'ORDER BY usuario_id'),
    (r'GROUP\s+BY\s+user_id\b', 'GROUP BY usuario_id'),
]


# ==========================================================
# FUNÇÕES
# ==========================================================
def fazer_backup(caminho, backup_dir):
    """Copia arquivo pro backup."""
    destino = os.path.join(backup_dir, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copy2(caminho, destino)


def refatorar_linha(linha):
    """Aplica todos os padrões numa linha. Retorna (nova_linha, trocou)."""
    # 🔥 Pula linhas com comentário
    if linha.strip().startswith('#'):
        return linha, False

    # 🔥 Pula linhas com session (session['user_id'] / session.get('user_id'))
    if "session['user_id']" in linha or 'session.get(\'user_id\')' in linha:
        return linha, False

    # 🔥 Pula linhas com f-strings de texto (sem SQL)
    if 'f"' in linha or "f'" in linha:
        # Se tem SELECT/INSERT/UPDATE/DELETE na mesma linha, ainda troca
        if not re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|WHERE|FROM)\b', linha, re.I):
            return linha, False

    nova = linha
    for padrao, substituto in PADROES_TROCA:
        nova = re.sub(padrao, substituto, nova)

    return nova, nova != linha


def processar_arquivo(caminho, backup_dir):
    """Processa 1 arquivo. Retorna lista de trocas."""
    trocas = []

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        novas_linhas = []
        mudou = False

        for i, linha in enumerate(linhas, 1):
            nova_linha, trocou = refatorar_linha(linha)
            novas_linhas.append(nova_linha)

            if trocou:
                mudou = True
                trocas.append({
                    'linha': i,
                    'antes': linha.rstrip(),
                    'depois': nova_linha.rstrip()
                })

        if mudou:
            fazer_backup(caminho, backup_dir)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.writelines(novas_linhas)

        return trocas

    except Exception as e:
        print(f'❌ Erro em {caminho}: {e}')
        return []


# ==========================================================
# MAIN
# ==========================================================
def main():
    print('=' * 70)
    print('REFATORANDO user_id → usuario_id (SÓ EM SQL)')
    print('=' * 70)

    backup_dir = f'backup_refatoracao_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(backup_dir, exist_ok=True)
    print(f'📁 Backup em: {backup_dir}\n')

    total_arquivos = 0
    total_trocas = 0
    arquivos_mudados = []

    for pasta in PASTAS:
        if not os.path.exists(pasta):
            print(f'⚠️  Pasta não existe: {pasta}')
            continue

        for root, dirs, files in os.walk(pasta):
            if '__pycache__' in root:
                continue

            for file in files:
                if not file.endswith('.py'):
                    continue

                caminho = os.path.join(root, file)
                trocas = processar_arquivo(caminho, backup_dir)

                if trocas:
                    total_arquivos += 1
                    total_trocas += len(trocas)
                    arquivos_mudados.append(caminho)

                    print(f'\n📝 {caminho}')
                    print(f'   {len(trocas)} troca(s):')
                    for t in trocas[:3]:  # Mostra só as 3 primeiras
                        print(f'   L{t["linha"]}: {t["antes"][:70]}')
                        print(f'        → {t["depois"][:70]}')
                    if len(trocas) > 3:
                        print(f'   ... +{len(trocas) - 3} troca(s)')

    print('\n' + '=' * 70)
    print(f'✅ {total_arquivos} arquivo(s) refatorado(s)')
    print(f'✅ {total_trocas} troca(s) no total')
    print(f'📁 Backup em: {backup_dir}')
    print('=' * 70)

    print('\n⚠️  PRÓXIMOS PASSOS:')
    print('1. Roda: git diff')
    print('2. Revisa cada troca')
    print('3. Roda: python app.py')
    print('4. Testa CADA módulo (Finanças, Tarefas, Orçamentos)')
    print('5. Se funcionar: git add . && git commit')
    print('6. Se quebrar: git reset --hard HEAD')
    print('\n⚠️  RESTAURAR DO BACKUP SE PRECISAR:')
    print(f'   cp -r {backup_dir}/* .')


if __name__ == '__main__':
    main()