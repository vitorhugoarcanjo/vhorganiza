# ==========================================================
# INSERIR TRANSAÇÃO - SERVICES
# ==========================================================

from datetime import datetime, timedelta
import json
from utils.database.conexao_global import ini_conexao

class InserirTransacaoService:
    
    @staticmethod
    def get_proxima_sequencia(cursor, user_id):
        """Retorna a próxima sequência para o usuário"""
        cursor.execute("""
            SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 
            FROM transacoes WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def buscar_categorias(cursor, user_id):
        """Busca categorias do usuário"""
        cursor.execute("""
            SELECT id, nome FROM categorias_financas
            WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    
    @staticmethod
    def criar_transacao_simples(cursor, user_id, dados):
        """Cria uma transação sem parcelas"""
        sequencia = InserirTransacaoService.get_proxima_sequencia(cursor, user_id)
        
        cursor.execute("""
            INSERT INTO transacoes (
                user_id, sequencia_transacoes, tipo,
                valor_total, descricao, categoria_id,
                data_emissao, data_vencimento,
                total_parcelas, numero_parcela, status, ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
        """, (
            user_id, sequencia, dados['tipo'],
            dados['valor_total'], dados['descricao'], dados['categoria_id'],
            dados['data_emissao'], dados['data_vencimento'],
            1, 1
        ))
        
        return sequencia
    
    @staticmethod
    def criar_transacao_parcelada(cursor, user_id, dados):
        """Cria uma transação com múltiplas parcelas"""
        total_parcelas = dados['total_parcelas']
        intervalo_dias = dados['intervalo_dias'] or 30
        primeiro_vencimento = dados['primeiro_vencimento'] or dados['data_vencimento'] or dados['data_emissao']
        
        # Calcula valores das parcelas
        if dados.get('valores_parcelas') and len(dados['valores_parcelas']) > 0:
            valores_parcelas = dados['valores_parcelas']
        else:
            valor_por_parcela = dados['valor_total'] / total_parcelas
            valores_parcelas = [valor_por_parcela] * total_parcelas
        
        # 🔥 1. Cria a transação PAI
        sequencia_pai = InserirTransacaoService.get_proxima_sequencia(cursor, user_id)
        
        cursor.execute("""
            INSERT INTO transacoes (
                user_id, sequencia_transacoes, tipo,
                valor_total, descricao, categoria_id,
                data_emissao, data_vencimento,
                total_parcelas, intervalo_dias, status, ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
        """, (
            user_id, sequencia_pai, dados['tipo'],
            dados['valor_total'], dados['descricao'], dados['categoria_id'],
            dados['data_emissao'], primeiro_vencimento,
            total_parcelas, intervalo_dias
        ))
        
        # 🔥 2. Cria cada parcela filha
        for i in range(1, total_parcelas + 1):
            if i == 1:
                data_venc_parcela = primeiro_vencimento
            else:
                data_base = datetime.strptime(primeiro_vencimento, '%Y-%m-%d')
                data_venc_parcela = (data_base + timedelta(days=(i-1) * intervalo_dias)).strftime('%Y-%m-%d')
            
            valor_parcela = valores_parcelas[i-1]
            sequencia_parcela = InserirTransacaoService.get_proxima_sequencia(cursor, user_id)
            
            cursor.execute("""
                INSERT INTO transacoes (
                    user_id, sequencia_transacoes, tipo,
                    valor_total, valor_parcela, descricao, categoria_id,
                    data_emissao, data_vencimento,
                    total_parcelas, numero_parcela, sequencia_parcela,
                    transacao_pai_id, status, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
            """, (
                user_id, sequencia_parcela, dados['tipo'],
                valor_parcela, valor_parcela, 
                f"{dados['descricao']} - Parcela {i}/{total_parcelas}", 
                dados['categoria_id'],
                dados['data_emissao'], data_venc_parcela,
                total_parcelas, i, i,
                sequencia_pai
            ))
        
        return sequencia_pai, total_parcelas
    
    @staticmethod
    def registrar_auditoria(transacao_id, descricao, total_parcelas=None):
        """Registra auditoria da criação"""
        try:
            from rotas.auditoria_geral.pasta_financas.services_auditoria import AuditoriaFinanceiraService
            
            if total_parcelas and total_parcelas > 1:
                acao = 'criada_parcelada'
                valor_novo = json.dumps({
                    'descricao': descricao,
                    'total_parcelas': total_parcelas
                }, ensure_ascii=False)
            else:
                acao = 'criada'
                valor_novo = json.dumps([
                    {'campo': 'transação', 'depois': descricao}
                ], ensure_ascii=False)
            
            AuditoriaFinanceiraService.registrar(
                transacao_id=transacao_id,
                acao=acao,
                campo_alterado='multiplos',
                valor_antigo=None,
                valor_novo=valor_novo
            )
        except Exception as e:
            print(f"Erro na auditoria: {e}")