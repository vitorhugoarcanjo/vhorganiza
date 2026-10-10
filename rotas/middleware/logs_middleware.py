# rotas/middleware/logs_middleware.py
import time
from flask import request, session, g
from rotas.logs.logs_services.painel_services import LogService

# ============================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================

# Rotas que NÃO DEVEM ser logadas (internas e estáticas)
ROTAS_IGNORADAS = [
    '/static',
    '/favicon.ico',
    '/robots.txt',
    '/painel_logs',
    '/logs_erros',
    '/painel_acessos',
    '/logs_ataques',
]

# Rotas LEGÍTIMAS do sistema (nunca serão marcadas como ataque)
ROTAS_LEGITIMAS = [
    '/config/',
    '/config/perfil',
    '/config/seguranca',
    '/financas/',
    '/tarefas/',
    '/dashboard/',
    '/pos_login/',
    '/login/',
    '/recuperar/',
    '/cadastre_se/',
    '/categorias/',
    '/nova_transacao/',
    '/edit_transacoes/',
    '/deletar_transacao/',
    '/quitar_transacao/',
    '/insert_tarefas/',
    '/editar_tarefa/',
]

# PADRÕES DE ATAQUE (mais específicos para evitar falsos positivos)
PADROES_ATAQUE = [
    # Arquivos sensíveis (com extensões ou caminhos específicos)
    '.env', '.git', '.svn', '.htaccess', '.htpasswd',
    'wp-config.php', 'config.php', 'config.yml', 'config.yaml', 'config.json', 'config.xml',
    # WordPress e CMS
    'wp-admin', 'wp-login', 'wp-includes', 'wp-content', 'wp-load.php',
    'wlwmanifest.xml', 'xmlrpc.php', 'wp-json',
    # Outros CMS e frameworks
    'joomla', 'drupal', 'magento', 'moodle', 'prestashop', 'laravel',
    # Scanners comuns
    'Dr0v', 'backup.zip', 'backup.tar', 'dump.sql', 'database.sql',
    # Pastas sensíveis
    'phpmyadmin', 'mysql', 'adminer', 'phpinfo.php',
    # URLs de ataque comuns
    '/admin/', '/login.php', '/setup.php', '/install.php', '/shell.php',
    'c99.php', 'r57.php', 'webshell', 'cmd.php'
]

def get_client_ip():
    """
    Obtém o IP real do cliente considerando proxies reversos.
    Suporta Nginx, Cloudflare, e outros proxies comuns.
    """
    headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',      # Cloudflare
        'True-Client-IP',        # Akamai
        'X-Forwarded-For'
    ]
    
    for header in headers:
        ip = request.headers.get(header)
        if ip:
            # Pega o primeiro IP se for uma lista (X-Forwarded-For)
            return ip.split(',')[0].strip()
    
    return request.remote_addr


def is_legitimate_route(path):
    """Verifica se a rota é legítima do sistema"""
    for rota in ROTAS_LEGITIMAS:
        if path.startswith(rota):
            return True
    return False


def is_attack_pattern(path):
    """Verifica se o caminho corresponde a um padrão de ataque"""
    for padrao in PADROES_ATAQUE:
        if padrao in path:
            return padrao
    return None


def log_acesso_middleware(app):
    """Middleware para registrar logs de acesso e ataques"""
    
    @app.before_request
    def before_request():
        """Registra o tempo de início da requisição"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Registra o acesso ou ataque após a resposta"""
        if not hasattr(g, 'start_time'):
            return response
        
        tempo_resposta = int((time.time() - g.start_time) * 1000)
        caminho = request.path.lower()
        
        # ============================================
        # 1. IGNORA ROTAS INTERNAS
        # ============================================
        for rota in ROTAS_IGNORADAS:
            if request.path.startswith(rota):
                return response
        
        # ============================================
        # 2. IGNORA REDIRECIONAMENTOS COMUNS
        # ============================================
        if response.status_code == 302 and request.path == '/pos_login/':
            return response
        
        # ============================================
        # 3. FILTRA MÉTODOS HTTP
        # ============================================
        if request.method not in ['GET', 'POST']:
            return response
        
        # ============================================
        # 4. OBTÉM DADOS DA REQUISIÇÃO
        # ============================================
        user_id = session.get('user_id')
        ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        # ============================================
        # 5. VERIFICA SE É ATAQUE (apenas se não for rota legítima)
        # ============================================
        ataque_detectado = None
        
        if not is_legitimate_route(caminho):
            ataque_detectado = is_attack_pattern(caminho)
        
        # ============================================
        # 6. REGISTRA NO BANCO DE DADOS
        # ============================================
        if ataque_detectado:
            # Registra como tentativa de ataque
            LogService.registrar_ataque(
                ip=ip,
                rota=request.path[:255],
                metodo=request.method,
                user_agent=user_agent,
                padrao=ataque_detectado
            )
        else:
            # Registra como acesso normal
            LogService.registrar_acesso(
                usuario_id=user_id,
                ip=ip,
                user_agent=user_agent,
                rota=request.path[:255],
                metodo=request.method,
                status_code=response.status_code,
                tempo_resposta=tempo_resposta
            )
        
        return response