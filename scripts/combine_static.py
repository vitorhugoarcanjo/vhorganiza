import os
import re
from datetime import datetime

# ==========================
# LISTA PARA COMBINAR OS ARQUIVOS CSS E JS ------- EVITAR LENTIDÃO
# ==========================

JS_FILES = [

    # ========================
    # FINANCAS
    # ========================
    # Modais
    'static/js/pasta_financas/modais/detalhes_completo.js',
    'static/js/pasta_financas/modais/pasta_excluir/excluir_financas.js',
    'static/js/pasta_financas/modais/pasta_estornar/modal_estornar_quitado.js',
    'static/js/pasta_financas/modais/pasta_estornar/modal_reativar_inativo.js',
    
    # Ações
    'static/js/pasta_financas/pasta_quitar/btn_quitar.js',
    'static/js/pasta_financas/totalizadores/totalizadores.js',
    'static/js/pasta_financas/pasta_filtros/botoes_outros_filtros.js',
    
    # Menu
    'static/js/pasta_financas/menu_click/click_direito.js',
    'static/js/pasta_financas/menu_click/menu_vinculos/vinculos.js',

    # ========================
    # TAREFAS - FUTURO PÓS AJUSTAR FINANCAS
    # ========================


    # ========================
    # COMPONENTES GLOBAIS
    # ========================
    'static/js/componentes/notificacoes_globais/notificacoes_tela.js',
    'static/js/componentes/data_global/click_data.js',
    'static/js/pos_login/btn_logout.js',
]


CSS_FILES = [
    'static/tela_base_telas_unificadas/estrutura_global.css',
    'static/pasta_tarefas/import_css.css',  # ← Esse tem @import
    'static/pasta_financas/modais/detalhes_completo.css',
    'static/pasta_financas/modais/modal_estornar.css',
    'static/pasta_financas/modais/modal_excluir.css',
    'static/js/pasta_financas/menu_click/click_direito.css',
    'static/js/componentes/notificacoes_globais/notificacoes_tela.css',
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
    with open('static/js/financas.min.js', 'w', encoding='utf-8') as out:
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
    with open('static/css/financas.min.css', 'w', encoding='utf-8') as out:
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
    print('  📄 static/js/financas.min.js')
    print('  📄 static/css/financas.min.css')
    print('='*60)


if __name__ == '__main__':
    combinar()