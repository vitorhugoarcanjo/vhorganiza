import os
import re
from datetime import datetime

# ==========================
# LISTA PARA COMBINAR OS ARQUIVOS CSS E JS ------- EVITAR LENTIDÃO
# ==========================

JS_FILES = [
    # ========================================= #
    # CORE - VARIÁVEIS, TEMAS, TEMPLATES
    # ========================================= #
    'static/js/modules/pasta_orcamentos/core/variaveis.js',
    'static/js/modules/pasta_orcamentos/core/temas.js',
    'static/js/modules/pasta_orcamentos/core/templates.js',
    'static/js/modules/pasta_orcamentos/core/pdf.js',
    'static/js/modules/pasta_orcamentos/core/pdf-preview.js',

    # ========================================= #
    # COMPONENTS - SEÇÕES
    # ========================================= #
    'static/js/modules/pasta_orcamentos/components/secoes-types.js',
    'static/js/modules/pasta_orcamentos/components/secoes-render.js',
    'static/js/modules/pasta_orcamentos/components/secoes-preview.js',
    'static/js/modules/pasta_orcamentos/components/secoes-manager.js',
    'static/js/modules/pasta_orcamentos/components/secoes-form.js',
    
    # ========================================= #
    # MODAIS
    # ========================================= #
    'static/js/modules/pasta_orcamentos/modals/modal_novo_orcamento.js',
    'static/js/modules/pasta_orcamentos/modals/modal_editar_orcamento.js',
    'static/js/modules/pasta_orcamentos/modals/modal_excluir_orcamento.js',
    
    # ========================================= #
    # MAIN
    # ========================================= #
    'static/js/modules/pasta_orcamentos/orcamento.js',
]


CSS_FILES = [
    # ========================================= #
    # COMPONENTS - GLOBAL
    # ========================================= #
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',

    # ========================================= #
    # CORE - GLOBAL
    # ========================================= #
    'static/css/core/reset.css',
    'static/css/core/responsive.css',

    # ========================================= #
    # MODALS - BASE (COMPARTILHADO)
    # ========================================= #
    'static/css/modules/pasta_orcamentos/modals/modal_base.css',

    # ========================================= #
    # MODALS - ESPECÍFICOS
    # ========================================= #
    'static/css/modules/pasta_orcamentos/modals/modal_novo_orcamento.css',
    'static/css/modules/pasta_orcamentos/modals/modal_editar_orcamento.css',
    'static/css/modules/pasta_orcamentos/modals/modal_excluir_orcamento.css',
    'static/css/modules/pasta_orcamentos/modals/modal_secao.css',
    'static/css/modules/pasta_orcamentos/modals/modal_preview.css',

    # ========================================= #
    # COMPONENTS - ORCAMENTOS
    # ========================================= #
    'static/css/modules/pasta_orcamentos/components/secoes.css',
    'static/css/modules/pasta_orcamentos/components/secoes_valor.css',
]

# ==========================
# FUNÇÃO PARA RESOLVER @import
# ==========================
def resolve_imports(content, file_path):
    """
    Resolve @import dentro de arquivos CSS
    Substitui @import pelo conteúdo do arquivo importado
    """
    
    # Padrão para encontrar @import
    # Exemplos: @import url('/static/pasta_tarefas/estrutura_global_v1.css');
    #           @import url("caminho.css");
    #           @import 'caminho.css';
    pattern = r'@import\s+url\([\'"]?([^\'"]+)[\'"]?\);?'
    
    def replace_import(match):
        import_path = match.group(1)
        
        # Remove /static/ do início se tiver
        if import_path.startswith('/static/'):
            import_path = import_path[8:]  # Remove '/static/'
        elif import_path.startswith('static/'):
            import_path = import_path[7:]  # Remove 'static/'
        
        # Tenta encontrar o arquivo
        full_path = os.path.join('static', import_path)
        
        if os.path.exists(full_path):
            print(f'Resolvendo @import: {import_path}')
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f'@import não encontrado: {import_path}')
            return ''  # Remove o @import se não encontrar
    
    # Substitui todos os @import
    return re.sub(pattern, replace_import, content, flags=re.IGNORECASE)


# ==========================
# COMBINAR
# ==========================
def combinar():
    print('='*60)
    print('COMBINANDO ARQUIVOS (COM RESOLUÇÃO DE @import)')
    print('='*60)

    # JS
    print('\nCombinando JS...')
    with open('static/js/modules/pasta_orcamentos/orcamento.min.js', 'w', encoding='utf-8') as out:
        out.write(f'// COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
        for file in JS_FILES:
            if os.path.exists(file):
                name = os.path.basename(file)
                out.write(f'// ==== {name} ====\n')
                with open(file, 'r', encoding='utf-8') as f:
                    out.write(f.read())
                    out.write('\n\n')
                print(f' ok {name}')
            else:
                print(f' falha {file} não encontrado')

    # CSS (com resolução de @import)
    print('\nCombinando CSS...')
    with open('static/css/modules/pasta_orcamentos/orcamento.min.css', 'w', encoding='utf-8') as out:
        out.write(f'/* COMBINADO - {datetime.now().strftime("%d/%m/%Y %H:%M")} */\n\n')
        
        for file in CSS_FILES:
            if os.path.exists(file):
                name = os.path.basename(file)
                out.write(f'/* ===== {name} ===== */\n')
                
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 🔥 RESOLVE @import
                    content = resolve_imports(content, file)
                    
                    out.write(content)
                    out.write('\n\n')
                
                print(f'  ok {name}')
            else:
                print(f'  falha {file} não encontrado')
    
    print('\n' + '='*60)
    print('ok PRONTO! Arquivos combinados:')
    print('static/js/modules/orcamento.min.js')
    print('static/css/modules/orcamento.min.css')
    print('='*60)


if __name__ == '__main__':
    combinar()