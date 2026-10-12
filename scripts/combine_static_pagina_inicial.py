# scripts/combine_static_pagina_inicial.py
# ==========================================================
# BUILD — PÁGINA INICIAL (pré-login)
# Combina: base_pre + notificações + pagina_inicial
# ==========================================================

import os
import re
from datetime import datetime

JS_FILES = [
    'static/js/componentes/notificacoes_globais/notificacoes_tela.js',
]

CSS_FILES = [
    'static/css/core/base_pre_acesso.css',
    'static/js/componentes/notificacoes_globais/notificacoes_tela.css',
    'static/css/modules/pasta_pre_login/pagina_inicial.css',
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


def garantir_pasta(caminho_arquivo):
    pasta = os.path.dirname(caminho_arquivo)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)
        print(f'  📁 Pasta criada: {pasta}')


def combinar():
    print('=' * 60)
    print('🚀 COMBINANDO — PÁGINA INICIAL')
    print('=' * 60)

    js_out  = 'static/js/modules/pasta_pre_login/pagina_inicial.min.js'
    css_out = 'static/css/modules/pasta_pre_login/pagina_inicial.min.css'

    garantir_pasta(js_out)
    garantir_pasta(css_out)

    print('\n📦 Combinando JS...')
    with open(js_out, 'w', encoding='utf-8') as out:
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

    print('\n📦 Combinando CSS...')
    with open(css_out, 'w', encoding='utf-8') as out:
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
    print('✅ PRONTO!')
    print(f'  📄 {js_out}')
    print(f'  📄 {css_out}')
    print('=' * 60)


if __name__ == '__main__':
    combinar()