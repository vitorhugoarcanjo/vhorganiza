# ==========================================================
# EDITAR TRANSAÇÃO - SERVICES (Corrigido)
# ==========================================================

from datetime import datetime, timedelta
import json
from utils.fomatacoes.data_reutilizavel import formatar_moeda_br

class EditarTransacaoService:
    
    @staticmethod
    def buscar_transacao_por_sequencia(cursor, sequencia, user_id):
        """Busca os dados principais da transação pela sequência visual"""
        cursor.execute("""
            SELECT 
                t.id,
                t.sequencia_transacoes,
                t.tipo,
                t.valor_total,
                t.descricao,
                t.data_emissao,
                t.categoria_id,
                c.nome AS categoria_nome,
                c.cor AS categoria_cor,
                t.data_vencimento,
                t.total_parcelas,
                t.intervalo_dias,
                t.transacao_pai_id,
                t.numero_parcela
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.sequencia_transacoes = %s AND t.user_id = %s AND t.ativo = 1
        """, (sequencia, user_id))
        return cursor.fetchone()

    @staticmethod
    def buscar_transacao_por_id(cursor, transacao_id, user_id):
        """Busca os dados principais da transação pelo ID interno"""
        cursor.execute("""
            SELECT 
                t.id,
                t.sequencia_transacoes,
                t.tipo,
                t.valor_total,
                t.descricao,
                t.data_emissao,
                t.categoria_id,
                c.nome AS categoria_nome,
                c.cor AS categoria_cor,
                t.data_vencimento,
                t.total_parcelas,
                t.intervalo_dias,
                t.transacao_pai_id,
                t.numero_parcela
            FROM transacoes t
            LEFT JOIN categorias_financas c ON c.id = t.categoria_id
            WHERE t.id = %s AND t.user_id = %s AND t.ativo = 1
        """, (transacao_id, user_id))
        return cursor.fetchone()
    
    @staticmethod
    def buscar_parcelas_filhas(cursor, pai_id):
        """Busca as parcelas filhas usando o ID interno do Pai"""
        cursor.execute("""
            SELECT sequencia_transacoes, numero_parcela, data_vencimento, valor_total, id
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (pai_id,))
        return cursor.fetchall()
    
    @staticmethod
    def buscar_categorias(cursor, user_id):
        """Busca categorias do usuário"""
        cursor.execute("""
            SELECT id, nome, cor
            FROM categorias_financas
            WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    
    @staticmethod
    def get_pai_da_parcela(cursor, sequencia, user_id):
        """
        Se a transação clicada for filha, retorna os dados do Pai (para preencher o topo) 
        e o ID do pai. Se for à vista ou o próprio pai, retorna ela mesma.
        """
        transacao = EditarTransacaoService.buscar_transacao_por_sequencia(cursor, sequencia, user_id)
        if not transacao:
            return None, None
        
        # Índice 12 = transacao_pai_id (que guarda o ID do pai)
        transacao_pai_id = transacao[12]
        
        if transacao_pai_id:
            pai = EditarTransacaoService.buscar_transacao_por_id(cursor, transacao_pai_id, user_id)
            return pai, transacao_pai_id
            
        # Se não tem pai, ela própria é a transação principal/pai (ou à vista). Retornamos seu próprio ID (Índice 0)
        return transacao, transacao[0]
    
    @staticmethod
    def formatar_transacao_para_modal(transacao_raw, parcelas_raw):
        """Formata os dados para o modal"""
        if not transacao_raw:
            return None
        
        transacao_lista = list(transacao_raw)
        transacao_lista[3] = formatar_moeda_br(transacao_lista[3])  # valor_total formatado (agora no índice 3 por causa do id)
        transacao = tuple(transacao_lista)
        
        parcelas = []
        for p in parcelas_raw:
            parcelas.append({
                'sequencia': p[0],
                'numero': p[1],
                'data_vencimento': p[2].strftime('%Y-%m-%d') if p[2] else '',
                'valor': float(p[3]) if p[3] else 0.0,
                'id': p[4]
            })
        
        return {
            'transacao': transacao,
            'parcelas': parcelas,
            'total_parcelas': transacao[10] or 1, # Índice 10 = total_parcelas
            'parcelas_json': json.dumps(parcelas, default=str) if parcelas else '[]'
        }
    
    @staticmethod
    def atualizar_transacao(cursor, conexao, sequencia_ou_id, user_id, dados):
        """Atualiza a transação principal (pai ou única) e suas parcelas"""
        
        # Descobre se estamos atualizando pelo ID do pai ou pela sequência
        transacao_atual = EditarTransacaoService.buscar_transacao_por_sequencia(cursor, sequencia_ou_id, user_id)
        if not transacao_atual:
            # Tenta buscar pelo ID caso venha direto do pai
            transacao_atual = EditarTransacaoService.buscar_transacao_por_id(cursor, sequencia_ou_id, user_id)
            if not transacao_atual:
                return {'success': False, 'error': 'Transação não encontrada'}
        
        pai_id_real = transacao_atual[0]   # ID interno
        tipo = transacao_atual[2]          # Tipo
        
        # Extrai dados do form
        descricao = dados.get('descricao', '').strip()
        valor = float(dados.get('valor_total', 0.0))
        data_emissao = dados.get('data_emissao') or None
        data_vencimento = dados.get('data_vencimento') or None
        categoria_id = dados.get('categoria_id') or None
        total_parcelas = int(dados.get('total_parcelas', 1))
        
        # Busca dados atuais para auditoria
        dados_antes = (
            transacao_atual[4], transacao_atual[3], transacao_atual[5], 
            transacao_atual[9], transacao_atual[6], transacao_atual[7], transacao_atual[10]
        )
        total_parcelas_antes = transacao_atual[10] or 1
        
        # Atualiza transação principal (Pai ou única) usando o ID real
        cursor.execute("""
            UPDATE transacoes 
            SET descricao = %s, 
                valor_total = %s, 
                data_emissao = %s,
                data_vencimento = %s,
                categoria_id = %s,
                total_parcelas = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (descricao, valor, data_emissao, data_vencimento, categoria_id, total_parcelas, pai_id_real, user_id))
        
        # Gerencia parcelas filhas se for parcelado
        if total_parcelas > 1 or total_parcelas_antes > 1:
            EditarTransacaoService._gerenciar_parcelas(
                cursor, pai_id_real, user_id, tipo, 
                descricao, valor, total_parcelas, total_parcelas_antes,
                dados.get('intervaloDias', 30), 
                dados.get('primeiroVencimento', data_vencimento or data_emissao),
                dados.get('parcelas', []),
                data_emissao
            )
        
        return {
            'success': True,
            'dados_antes': dados_antes,
            'descricao': descricao,
            'valor': valor,
            'data_emissao': data_emissao,
            'data_vencimento': data_vencimento,
            'categoria_id': categoria_id
        }
    
    @staticmethod
    def _gerenciar_parcelas(cursor, pai_id, user_id, tipo, descricao, valor, 
                            total_parcelas, total_parcelas_antes, intervalo_dias, 
                            primeiro_vencimento, parcelas_input, data_emissao):
        """Gerencia criação/atualização/remoção de parcelas usando o pai_id correto"""
        
        # Busca parcelas existentes filhas deste Pai
        cursor.execute("""
            SELECT id, sequencia_transacoes, numero_parcela, valor_total, data_vencimento
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (pai_id,))
        parcelas_existentes = cursor.fetchall()
        
        if total_parcelas > 1:
            if parcelas_input and len(parcelas_input) > 0:
                valores_parcelas = []
                for p in parcelas_input:
                    try:
                        val = float(p['valor'])
                    except (ValueError, TypeError):
                        val = valor / total_parcelas
                    valores_parcelas.append(val)
            else:
                valor_por_parcela = round(valor / total_parcelas, 2)
                valores_parcelas = [valor_por_parcela] * total_parcelas
                diferenca = round(valor - sum(valores_parcelas), 2)
                if diferenca != 0:
                    valores_parcelas[-1] = round(valores_parcelas[-1] + diferenca, 2)
            
            # Inativa parcelas extras se reduziu o número de parcelas
            if len(parcelas_existentes) > total_parcelas:
                cursor.execute("""
                    UPDATE transacoes 
                    SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                    WHERE transacao_pai_id = %s AND ativo = 1 AND numero_parcela > %s
                """, (pai_id, total_parcelas))
            
            if not primeiro_vencimento:
                primeiro_vencimento = datetime.now().strftime('%Y-%m-%d')
            elif isinstance(primeiro_vencimento, (datetime, datetime.date)):
                primeiro_vencimento = primeiro_vencimento.strftime('%Y-%m-%d')
            
            data_base = datetime.strptime(str(primeiro_vencimento)[:10], '%Y-%m-%d')
            
            for i in range(1, total_parcelas + 1):
                if i == 1:
                    data_venc_parcela = primeiro_vencimento
                else:
                    data_venc_parcela = (data_base + timedelta(days=(i - 1) * int(intervalo_dias or 30))).strftime('%Y-%m-%d')
                
                valor_parcela = valores_parcelas[i-1] if i <= len(valores_parcelas) else (valor / total_parcelas)
                parcela_existente = next((p for p in parcelas_existentes if p[2] == i), None)
                
                if parcela_existente:
                    cursor.execute("""
                        UPDATE transacoes 
                        SET valor_total = %s, 
                            valor_parcela = %s,
                            data_vencimento = %s,
                            descricao = %s,
                            data_alteracao = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (valor_parcela, valor_parcela, data_venc_parcela, 
                          f'{descricao} ({i}/{total_parcelas})', parcela_existente[0]))
                else:
                    sequencia_parcela = EditarTransacaoService._get_proxima_sequencia(cursor, user_id)
                    cursor.execute("""
                        INSERT INTO transacoes (
                            user_id, sequencia_transacoes, tipo,
                            valor_total, valor_parcela, descricao, categoria_id,
                            data_emissao, data_vencimento,
                            total_parcelas, numero_parcela, sequencia_parcela,
                            transacao_pai_id, status, ativo
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', 1)
                    """, (user_id, sequencia_parcela, tipo, valor_parcela, valor_parcela, 
                          f'{descricao} ({i}/{total_parcelas})', None,
                          data_emissao, data_venc_parcela, total_parcelas, i, i, pai_id))
            
            # Atualiza o intervalo no pai
            cursor.execute("""
                UPDATE transacoes 
                SET intervalo_dias = %s 
                WHERE id = %s AND user_id = %s
            """, (intervalo_dias, pai_id, user_id))
            
        elif total_parcelas_antes > 1 and total_parcelas == 1:
            cursor.execute("""
                UPDATE transacoes 
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                WHERE transacao_pai_id = %s AND ativo = 1
            """, (pai_id,))
    
    @staticmethod
    def _get_proxima_sequencia(cursor, user_id):
        cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = %s", (user_id,))
        return cursor.fetchone()[0]