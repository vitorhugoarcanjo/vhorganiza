# scripts/combine_all.py
# ==========================================================
# BUILD MASTER — Roda TODOS os combine_static_* de uma vez
# ==========================================================
#
# Uso:
#   python scripts/combine_all.py
#
# Ou, se quiser rodar só alguns módulos:
#   python scripts/combine_all.py tarefas financas
# ==========================================================

import os
import sys
import subprocess
from datetime import datetime


# ==========================================================
# CONFIGURAÇÃO — ADICIONA AQUI OS MÓDULOS CONFORME CRESCEM
# ==========================================================
MODULOS = [
    'tarefas',
    'financas',
    'orcamentos',
    'categorias',
    'pos_login',
    'dashboard',
]


def rodar_combine(modulo):
    """Roda o script combine_static_<modulo>.py"""
    script_path = f'scripts/combine_static_{modulo}.py'

    if not os.path.exists(script_path):
        print(f'  ⚠️  {script_path} não existe — pulando')
        return False

    print(f'\n{"=" * 60}')
    print(f'🚀 RODANDO: {modulo}')
    print(f'{"=" * 60}')

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,   # mostra output em tempo real
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f'  ❌ Erro no módulo {modulo}: {e}')
        return False
    except Exception as e:
        print(f'  ❌ Erro inesperado em {modulo}: {e}')
        return False


def main():
    print('=' * 60)
    print(f'🏗️  BUILD MASTER — {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    print('=' * 60)

    # Se passou módulos pela linha de comando, usa só esses
    if len(sys.argv) > 1:
        modulos_para_rodar = sys.argv[1:]
        print(f'📦 Rodando só: {", ".join(modulos_para_rodar)}')
    else:
        modulos_para_rodar = MODULOS
        print(f'📦 Rodando todos: {", ".join(modulos_para_rodar)}')

    sucessos = []
    falhas = []

    for modulo in modulos_para_rodar:
        ok = rodar_combine(modulo)
        if ok:
            sucessos.append(modulo)
        else:
            falhas.append(modulo)

    # ==========================================================
    # RESUMO FINAL
    # ==========================================================
    print('\n' + '=' * 60)
    print('📊 RESUMO FINAL')
    print('=' * 60)

    if sucessos:
        print(f'\n✅ Sucesso ({len(sucessos)}):')
        for m in sucessos:
            print(f'   • {m}')

    if falhas:
        print(f'\n❌ Falhas ({len(falhas)}):')
        for m in falhas:
            print(f'   • {m}')

    print('\n' + '=' * 60)
    if not falhas:
        print('✅ TUDO PRONTO! Pode subir.')
    else:
        print(f'⚠️  {len(falhas)} módulo(s) falharam. Verifica os erros acima.')
    print('=' * 60)

    # Retorna código de erro se alguma falhou
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()