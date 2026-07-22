import os
import re
from datetime import datetime

# ==========================
# LISTA PARA COMBINAR OS ARQUIVOS CSS E JS ------- EVITAR LENTIDÃO
# ==========================

JS_FILES = [
    # 1. MODAIS
    'static/js/modules/pasta_tarefas/modais/pasta_excluir/modal_excluir_global.js',
    'static/js/modules/pasta_tarefas/modais/pasta_excluir/btn_excluir.js',
    'static/js/modules/pasta_tarefas/modais/concluir_tarefas.js',
    'static/js/modules/pasta_tarefas/modais/detalhes_completo.js',
    
    # 2. TOTALIZADORES
    'static/js/modules/pasta_tarefas/totalizadores/totalizadores.js',
    
    # 3. ORDENAÇÃO
    'static/js/modules/pasta_tarefas/ordenacao_colunas/ordenacao.js',

]


CSS_FILES = [
    # exemplo: 'static/tela_base_telas_unificadas/estrutura_global.css',
    # ========================================= #
    # COMPONENTS
    # ========================================= #
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',

    # ========================================= #
    # CORE
    # ========================================= #
    'static/css/core/reset.css',
    'static/css/core/responsive.css',


    # ========================================= #
    # AJUSTAR OS CSS DOS MODAIS...
    # ========================================= #
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
            print(f'    📄 Resolvendo @import: {import_path}')
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f'    ⚠️ @import não encontrado: {import_path}')
            return ''  # Remove o @import se não encontrar
    
    # Substitui todos os @import
    return re.sub(pattern, replace_import, content, flags=re.IGNORECASE)


# ==========================
# COMBINAR
# ==========================
def combinar():
    print('='*60)
    print('🚀 COMBINANDO ARQUIVOS (COM RESOLUÇÃO DE @import)')
    print('='*60)

    # JS
    print('\n📦 Combinando JS...')
    with open('static/js/modules/pasta_tarefas/tarefas.min.js', 'w', encoding='utf-8') as out:
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

    # CSS (com resolução de @import)
    print('\n📦 Combinando CSS...')
    with open('static/css/modules/pasta_tarefas/tarefas.min.css', 'w', encoding='utf-8') as out:
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
                
                print(f'  ✅ {name}')
            else:
                print(f'  ⚠️ {file} não encontrado')
    
    print('\n' + '='*60)
    print('✅ PRONTO! Arquivos combinados:')
    print('  📄 static/js/tarefas.min.js')
    print('  📄 static/css/tarefas.min.css')
    print('='*60)


if __name__ == '__main__':
    combinar()