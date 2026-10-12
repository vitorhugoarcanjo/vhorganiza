# scripts/combine_static_pos_login.py
# ==========================================================
# BUILD — TELA PÓS-LOGIN ("Meu Dia")
# Combina CSS compartilhado + específico do pós-login
# ==========================================================

import os
import re
from datetime import datetime

JS_FILES = [
    # ========================================= #
    # ESPECÍFICO DO PÓS-LOGIN
    # ========================================= #
    # 'static/js/modules/pasta_pos_login/pos_login.js',
]

CSS_FILES = [
    # ========================================= #
    # CORE
    # ========================================= #
    'static/css/core/reset.css',

    # ========================================= #
    # COMPONENTS (COMPARTILHADO)
    # ========================================= #
    'static/css/components/buttons.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',

    # ========================================= #
    # ESPECÍFICO DO PÓS-LOGIN
    # ========================================= #
    'static/css/modules/pasta_pos_login/pos_login.css',
]


def resolve_imports(content, file_path):
    pattern = r'@import\s+url\([\'"]?([^\'"]+)[\'"]?\);?'
    def replace_import(match):
        import_path = match.group(1)
        if import_path.startswith('/static/'):
            import_path = import_path[8:]
        elif import_path.startswith('static/'):
            import_path = import_path[7:]
        full_path = os.path.join('static', import_path)
        if os.path.exists(full_path):
            print(f'    📄 Resolvendo @import: {import_path}')
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        print(f'    ⚠️ @import não encontrado: {import_path}')
        return ''
    return re.sub(pattern, replace_import, content, flags=re.IGNORECASE)


def combinar():
    print('=' * 60)
    print('🚀 COMBINANDO ARQUIVOS — PÓS-LOGIN')
    print('=' * 60)

    # JS
    print('\n📦 Combinando JS...')
    with open('static/js/modules/pasta_pos_login/pos_login.min.js', 'w', encoding='utf-8') as out:
        out.write(f'// COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
        for file in JS_FILES:
            if os.path.exists(file):
                name = os.path.basename(file)
                out.write(f'// ==== {name} ====\n')
                with open(file, 'r', encoding='utf-8') as f:
                    out.write(f.read())
                    out.write('\n\n')
                print(f'  ✅ {name}')
            else:
                print(f'  ⚠️ {file} não encontrado')

    # CSS
    print('\n📦 Combinando CSS...')
    with open('static/css/modules/pasta_pos_login/pos_login.min.css', 'w', encoding='utf-8') as out:
        out.write(f'/* COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")} */\n\n')
        for file in CSS_FILES:
            if os.path.exists(file):
                name = os.path.basename(file)
                out.write(f'/* ===== {name} ===== */\n')
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = resolve_imports(content, file)
                    out.write(content)
                    out.write('\n\n')
                print(f'  ✅ {name}')
            else:
                print(f'  ⚠️ {file} não encontrado')

    print('\n' + '=' * 60)
    print('✅ PRONTO! Arquivos combinados:')
    print('  📄 static/js/modules/pasta_pos_login/pos_login.min.js')
    print('  📄 static/css/modules/pasta_pos_login/pos_login.min.css')
    print('=' * 60)


if __name__ == '__main__':
    combinar()