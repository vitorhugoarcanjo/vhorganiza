from flask import Blueprint

bp_orcamentos = Blueprint('orcamentos', __name__, url_prefix='/orcamentos')

# IMPORTA AS VIEWS
from .orcamentos import ini_orcamento
from .crud.cadastrar import criar_orcamento
from .crud.editar import salvar_estrutura
from .crud.excluir import excluir_orcamento
from .crud.listar import listar_todos
from .crud.pdf import gerar_pdf
from .crud.limpar_filtros import limpar_filtros
from .crud.dados import get_dados_orcamento

# REGISTRA AS ROTAS
bp_orcamentos.add_url_rule('/', view_func=ini_orcamento, methods=['GET'])
bp_orcamentos.add_url_rule('/criar', view_func=criar_orcamento, methods=['POST'])
bp_orcamentos.add_url_rule('/<int:id>/salvar-estrutura', view_func=salvar_estrutura, methods=['POST'])
bp_orcamentos.add_url_rule('/<int:id>/excluir', view_func=excluir_orcamento, methods=['DELETE'])
bp_orcamentos.add_url_rule('/todos', view_func=listar_todos, methods=['GET'])
bp_orcamentos.add_url_rule('/<int:id>/pdf', view_func=gerar_pdf, methods=['GET'])
bp_orcamentos.add_url_rule('/limpar-filtros', view_func=limpar_filtros, methods=['GET'])
bp_orcamentos.add_url_rule('/<int:id>/dados', view_func=get_dados_orcamento, methods=['GET'])