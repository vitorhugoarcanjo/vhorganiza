# scripts/combine_static_categorias.py
# ==========================================================
# BUILD - COMBINA JS + CSS DO MÓDULO CATEGORIAS
# ==========================================================

import os
import re
from datetime import datetime

# ==========================================================
# JS_FILES — ordem importa!
# ==========================================================
JS_FILES = [
    # Compartilhado
    'static/js/componentes/botoes_filtros.js',

    # Core (classe compartilhada)
    'static/js/modules/pasta_categorias/core/CategoriaForm.js',

    # Modais
    'static/js/modules/pasta_categorias/modals/categoria-nova.js',
    'static/js/modules/pasta_categorias/modals/categoria-editar.js',

    # Ações (excluir / reativar / auditoria)
    'static/js/modules/pasta_categorias/acoes_e_modais/pasta_excluir/excluir_categoria.js',
    'static/js/modules/pasta_categorias/acoes_e_modais/pasta_reativar/reativar_categoria.js',
    'static/js/modules/pasta_categorias/acoes_e_modais/pasta_auditoria/auditoria_categorias.js',

    # Orquestrador (por último)
    'static/js/modules/pasta_categorias/categorias.js',
]

# ==========================================================
# CSS_FILES
# ==========================================================
CSS_FILES = [
    # Core
    'static/css/core/reset.css',
    'static/css/core/responsive.css',

    # Components (compartilhado)
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',
    'static/css/components/modal.css',
    'static/css/components/modal_confirmacao.css',
    'static/css/components/modal_auditoria.css',
    'static/css/components/form.css',
    'static/js/componentes/notificacoes_globais/notificacoes_tela.css',

    # Específico do módulo
    'static/css/modules/pasta_categorias/categorias.css',
]


def resolve_imports(content, file_path):
    """Resolve @import dentro de arquivos CSS."""
    pattern = r'@import\s+url\([\'"]?([^\'"]+)[\'"]?\);?'
    def replace_import(match):
        import_path = match.group(1)
        if import_path.startswith('/static/'):
            import_path = import_path[8:]
        elif import_path.startswith('static/'):
            import_path = import_path[7:]
        full_path = os.path.join('static', import_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
    return re.sub(pattern, replace_import, content, flags=re.IGNORECASE)


def combinar():
    print("COMBINANDO ARQUIVOS (CATEGORIAS)")
    print("==================")

    # JS
    print("Combinando JS...")
    with open('static/js/modules/pasta_categorias/categorias.min.js', 'w', encoding='utf-8') as out:
        out.write(f'// COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
        for file in JS_FILES:
            if os.path.exists(file):
                out.write(f'// ==== {os.path.basename(file)} ====\n')
                with open(file, 'r', encoding='utf-8') as f:
                    out.write(f.read())
                out.write('\n\n')
                print(f"  ok {os.path.basename(file)}")
            else:
                print(f"  ⚠️ NÃO ENCONTRADO: {file}")

    # CSS
    print("\nCombinando CSS...")
    with open('static/css/modules/pasta_categorias/categorias.min.css', 'w', encoding='utf-8') as out:
        out.write(f'/* COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")} */\n\n')
        for file in CSS_FILES:
            if os.path.exists(file):
                out.write(f'/* ===== {os.path.basename(file)} ===== */\n')
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = resolve_imports(content, file)
                    out.write(content)
                out.write('\n\n')
                print(f"  ok {os.path.basename(file)}")
            else:
                print(f"  ⚠️ NÃO ENCONTRADO: {file}")

    print("\n✅ PRONTO! Arquivos combinados:")
    print("   static/js/modules/pasta_categorias/categorias.min.js")
    print("   static/css/modules/pasta_categorias/categorias.min.css")


if __name__ == '__main__':
    combinar()