# scripts/verificar_variaveis.py
# ==========================================================
# Verifica se variáveis 'user_id' ainda existem após a
# refatoração (fora de session/comentário/log).
# Lista TODOS os lugares que precisam trocar.
# ==========================================================

import os
import re

PASTAS = [
    'rotas/pasta_financas',
    'rotas/pasta_tarefas',
    'rotas/pasta_dashboard',
    'rotas/auditoria_geral',
    'rotas/logs',
    'rotas/middleware',
]

# Padrões que NUNCA devem ser tocados (não são problema)
PADROES_IGNORADOS = [
    r"session\['user_id'\]",          # session['user_id']
    r'session\.get\(["\']user_id',    # session.get('user_id')
    r"session\[['\"]user_id",         # session["user_id"]
    r'^\s*#',                          # Comentário
    r'logger\.',                       # Linha de log
    r'logging\.',                      # Linha de log
    r"['\"]user_id['\"]\s*:",         # Dicionário {'user_id': ...}
    r'\bidx_\w*user_id\b',            # Nome de índice
    r'/user_id/',                       # URL com /user_id/
    r'<int:user_id>',                   # Rota com <int:user_id>
    r'data-transacao-id',               # Atributo HTML
]


def deve_ignorar(linha):
    """Retorna True se a linha deve ser ignorada."""
    for padrao in PADROES_IGNORADOS:
        if re.search(padrao, linha):
            return True
    return False


def analisar_arquivo(caminho):
    """
    Retorna lista de problemas no arquivo.
    Cada problema: {'linha': int, 'texto': str}
    """
    problemas = []

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        for i, linha in enumerate(linhas, 1):
            # Pula linhas que devem ser ignoradas
            if deve_ignorar(linha):
                continue

            # Se a linha contém 'user_id' (fora dos casos ignorados)
            if re.search(r'\buser_id\b', linha):
                problemas.append({
                    'linha': i,
                    'texto': linha.strip(),
                })

    except Exception as e:
        print(f'❌ Erro em {caminho}: {e}')

    return problemas


def main():
    print('=' * 80)
    print('VERIFICANDO VARIÁVEIS user_id RESIDUAIS')
    print('=' * 80)

    total_problemas = 0
    arquivos_com_problema = []

    for pasta in PASTAS:
        if not os.path.exists(pasta):
            continue

        for root, dirs, files in os.walk(pasta):
            if '__pycache__' in root:
                continue

            for file in files:
                if not file.endswith('.py'):
                    continue

                caminho = os.path.join(root, file)
                problemas = analisar_arquivo(caminho)

                if problemas:
                    arquivos_com_problema.append({
                        'caminho': caminho,
                        'problemas': problemas,
                    })
                    total_problemas += len(problemas)

    # ==========================================================
    # OUTPUT
    # ==========================================================
    if not arquivos_com_problema:
        print('\n✅ NENHUM user_id RESIDUAL ENCONTRADO!')
        print('Sistema 100% padronizado.\n')
        return

    print(f'\n⚠️  {len(arquivos_com_problema)} arquivo(s) com problema')
    print(f'⚠️  {total_problemas} linha(s) para revisar\n')

    for arq in arquivos_com_problema:
        print(f'\n📝 {arq["caminho"]}')
        for p in arq['problemas']:
            print(f'   L{p["linha"]}: {p["texto"]}')

    print('\n' + '=' * 80)
    print('PRÓXIMOS PASSOS:')
    print('1. Revisa cada linha listada')
    print('2. Troca "user_id" por "usuario_id" SE for variável/coluna')
    print('3. Se for session ou comentário, ignora (já filtrado)')
    print('4. Roda de novo pra confirmar')
    print('=' * 80)


if __name__ == '__main__':
    main()