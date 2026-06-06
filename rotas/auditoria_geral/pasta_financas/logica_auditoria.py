from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from rotas.middleware.autenticacao import login_required
from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
from utils.database.conexao_global import ini_conexao

bp_auditoria_financas = Blueprint('auditoria_financas', __name__)

@bp_auditoria_financas.route('/transacao/<int:transacao_id>')
@login_required
def historico_transacao(transacao_id):
    """Ver histórico de alterações de uma transação"""
    
    # Pega os parâmetros da URL para manter os filtros
    mostrar_inativas = request.args.get('mostrar_inativas', '0')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo_data = request.args.get('tipo_data', 'emissao')
    
    # Busca dados da transação para exibir no cabeçalho
    conexao, cursor = ini_conexao()
    cursor.execute("""
        SELECT sequencia_transacoes, descricao, tipo, valor_total
        FROM transacoes
        WHERE sequencia_transacoes = %s AND user_id = %s
    """, (transacao_id, session['user_id']))
    
    transacao = cursor.fetchone()
    
    if not transacao:
        flash('Transação não encontrada', 'danger')
        return redirect(url_for('financas.inifinancas'))
    
    # Usa o método formatado do service
    historico = AuditoriaFinanceiraService.listar_por_transacao_formatado(transacao_id)
    
    return render_template('pasta_auditoria/pasta_financas/auditoria_financas.html', 
                          historico=historico,
                          transacao=transacao,
                          transacao_id=transacao_id,
                          mostrar_inativas=mostrar_inativas,
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          tipo_data=tipo_data)