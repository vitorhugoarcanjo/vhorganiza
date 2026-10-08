import os
import re
from datetime import datetime

# ==========================
# LISTA PARA COMBINAR OS ARQUIVOS CSS E JS ------- EVITAR LENTIDÃO
# ==========================

JS_FILES = [
    # ========================================= #
    # CORE - GLOBAL
    # ========================================= #
    'static/js/componentes/botoes_filtros.js',

    # ========================================= #
    # CORE (classe base compartilhada)
    # ========================================= #
    'static/js/modules/pasta_tarefas/core/TarefaForm.js',

    # ========================================= #
    # COMPONENTS (sincronização HTMX)
    # ========================================= #
    'static/js/modules/pasta_tarefas/components/totalizadores.js',
    'static/js/modules/pasta_tarefas/components/ordenacao.js',

    # ========================================= #
    # MODAIS (nova / editar)
    # ========================================= #
    'static/js/modules/pasta_tarefas/modals/tarefa-nova.js',
    'static/js/modules/pasta_tarefas/modals/tarefa-editar.js',

    # ========================================= #
    # AÇÕES E MODAIS (excluir / concluir / detalhes)
    # ========================================= #
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_excluir/excluir_tarefa.js',
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_concluir/concluir_tarefa.js',
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_detalhes/detalhes_tarefa.js',
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_reabrir/reabrir_tarefa.js',
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_reativar/reativar_tarefa.js',
    'static/js/modules/pasta_tarefas/acoes_e_modais/pasta_auditoria/auditoria_tarefa.js',

    # ========================================= #
    # ORQUESTRADOR (por último — depende de tudo)
    # ========================================= #
    'static/js/modules/pasta_tarefas/tarefas.js',
]

CSS_FILES = [
    # ========================================= #
    # CORE
    # ========================================= #
    'static/css/core/reset.css',
    'static/css/core/responsive.css',

    # ========================================= #
    # COMPONENTS (MESMA LISTA DO FINANÇAS)
    # ========================================= #
    'static/css/components/buttons.css',
    'static/css/components/filters.css',
    'static/css/components/footer.css',
    'static/css/components/tables.css',
    'static/css/components/modal.css',
    'static/css/components/modal_confirmacao.css',
    'static/css/components/modal_detalhes.css',
    'static/css/components/form.css',
    'static/css/components/modal_auditoria.css',

    # ========================================= #
    # ESPECÍFICO DO TAREFAS
    # ========================================= #
    # (nada por enquanto — quando tiver, adiciona aqui)
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
    with open('static/js/modules/pasta_tarefas/tarefas.min.js', 'w', encoding='utf-8') as out:
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
                
                print(f'  ok {name}')
            else:
                print(f'  falha {file} não encontrado')
    
    print('\n' + '='*60)
    print('ok PRONTO! Arquivos combinados:')
    print('static/js/tarefas.min.js')
    print('static/css/tarefas.min.css')
    print('='*60)


if __name__ == '__main__':
    combinar()