# scripts/watch_static.py

import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============================================
# CONFIGURACAO
# ============================================

WATCH_DIRS = [
    'static/css/components',
    'static/css/core',
    'static/css/modules',
    'static/js/modules',
    'static/js/pasta_tarefas',
]

BUILD_SCRIPT = 'scripts/combine_static_tarefas.py'

# ============================================
# HANDLER
# ============================================

class BuildHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_build = 0
        self.cooldown = 2
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        src_path = event.src_path.lower()
        if any(x in src_path for x in ['.pyc', '__pycache__', '.swp', '~']):
            return
        
        if 'tarefas.min' in src_path or 'financas.min' in src_path:
            return
        
        now = time.time()
        if now - self.last_build < self.cooldown:
            return
        
        self.last_build = now
        
        print('\n' + '='*60)
        print(f'🔄 Arquivo alterado: {os.path.basename(event.src_path)}')
        print('🔨 Executando build...')
        
        try:
            result = subprocess.run(
                ['python', BUILD_SCRIPT],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print('✅ Build concluído com sucesso!')
            else:
                print('❌ Erro no build:')
                print(result.stderr)
        except Exception as e:
            print(f'❌ Erro ao executar build: {e}')
        
        print('='*60 + '\n')

# ============================================
# MAIN
# ============================================

def watch():
    print('='*60)
    print('👀 WATCH MODE - Observando mudancas...')
    print('='*60)
    
    print('\n📁 Pastas monitoradas:')
    for dir_path in WATCH_DIRS:
        if os.path.exists(dir_path):
            print(f'   📂 {dir_path}')
        else:
            print(f'   ⚠️ {dir_path} (nao encontrada)')
    
    print('\n🔄 Aguardando alteracoes... (Ctrl+C para parar)')
    print('💡 Dica: Edite qualquer arquivo CSS/JS e veja o build rodar automatico!\n')
    
    print('🔨 Build inicial...')
    subprocess.run(['python', BUILD_SCRIPT])
    print('✅ Pronto!\n')
    
    event_handler = BuildHandler()
    observer = Observer()
    
    for dir_path in WATCH_DIRS:
        if os.path.exists(dir_path):
            observer.schedule(event_handler, dir_path, recursive=True)
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('\n👋 Watch finalizado!')
    
    observer.join()

if __name__ == '__main__':
    watch()