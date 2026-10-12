# rotas\pasta_login\pasta_cadastre_se\autenticador_email\config_email.py

class EmailConfig:
    # Configurações SMTP
    MAIL_SERVER = 'smtp.gmail.com'      # Altere conforme seu provedor
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'vhorganiza@gmail.com'  # Seu email
    MAIL_PASSWORD = 'adyu byct dnbo ncaw'    # Senha de app do Gmail
    
    # Remetente
    MAIL_DEFAULT_SENDER = 'vhorganiza@gmail.com'
    
    # Configurações do código
    CODIGO_TAMANHO = 6
    CODIGO_EXPIRACAO_MINUTOS = 15
    MAX_TENTATIVAS = 5