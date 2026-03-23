from flask import render_template, Blueprint, request
from rotas.middleware.autenticacao import login_required
from rotas.middleware.permissoes import requer_master
from rotas.logs.logs_services.painel_services import LogService

bp_painel_acessos = Blueprint('painel_acessos', __name__, url_prefix='/painel_acessos')

@bp_painel_acessos.route('/')
@login_required
@requer_master
def logs_acessos():
    """Lista de acessos ao sistema"""
    pagina = request.args.get('pagina', 1, type=int)
    limite = 20
    offset = (pagina - 1) * limite
    filtro = request.args.get('filtro', '')
    usuario_id = request.args.get('usuario_id', type=int)  # ← filtro por ID
    
    # Se tiver filtro por usuário, usa o método específico
    if usuario_id:
        # Busca todos acessos do usuário
        todos_acessos = LogService.obter_acessos_por_usuario(usuario_id, limite=1000)
        total = len(todos_acessos)
        # Aplica paginação manual
        acessos = todos_acessos[offset:offset + limite]
        
        # Busca nome do usuário para exibir
        usuario_nome = LogService.obter_nome_usuario(usuario_id)
    else:
        # Senão, usa o listar_acessos normal com filtro de texto
        resultados = LogService.listar_acessos(limite, offset, filtro)
        acessos = resultados['dados']
        total = resultados['total']
        usuario_nome = None
    
    return render_template(
        'logs/pasta_logs_acessos/logs_acessos.html',
        acessos=acessos,
        total=total,
        pagina=pagina,
        limite=limite,
        filtro=filtro,
        usuario_id=usuario_id,
        usuario_nome=usuario_nome
    )

@bp_painel_acessos.route('/<int:acesso_id>')
@login_required
@requer_master
def detalhe_acesso(acesso_id):
    """Detalhe de um acesso específico"""
    acesso = LogService.obter_acesso_por_id(acesso_id)
    
    if not acesso:
        return "Acesso não encontrado", 404
    
    return render_template('logs/pasta_logs_acessos/logs_acessos_detalhado.html', acesso=acesso)