# ==========================================================
# EDITAR TRANSAÇÃO - SERVICES
# ==========================================================

from datetime import datetime, timedelta
import json
from utils.fomatacoes.data_reutilizavel import formatar_moeda_br

class EditarTransacaoService:
    
    @staticmethod
    def buscar_transacao(cursor, sequencia, user_id):
        """Busca os dados da transação para edição"""
        cursor.execute("""
            SELECT 
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
    def buscar_parcelas(cursor, sequencia_pai):
        """Busca as parcelas filhas de um pai"""
        cursor.execute("""
            SELECT sequencia_transacoes, numero_parcela, data_vencimento, valor_total
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (sequencia_pai,))
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
        """Se for parcela filha, retorna os dados do pai e o ID real do pai"""
        transacao = EditarTransacaoService.buscar_transacao(cursor, sequencia, user_id)
        if not transacao:
            return None, None
        
        # ÍNDICE 11 = transacao_pai_id
        transacao_pai_id = transacao[11]
        if transacao_pai_id:
            pai = EditarTransacaoService.buscar_transacao(cursor, transacao_pai_id, user_id)
            return pai, transacao_pai_id
            
        return transacao, sequencia
    
    @staticmethod
    def formatar_transacao_para_modal(transacao_raw, parcelas_raw):
        """Formata os dados para o modal"""
        if not transacao_raw:
            return None
        
        transacao_lista = list(transacao_raw)
        transacao_lista[2] = formatar_moeda_br(transacao_lista[2])  # valor_total formatado para exibição
        transacao = tuple(transacao_lista)
        
        parcelas = []
        for p in parcelas_raw:
            parcelas.append({
                'numero': p[1],
                'data_vencimento': p[2].strftime('%Y-%m-%d') if p[2] else '',
                'valor': float(p[3]) if p[3] else 0.0,
                'sequencia': p[0]
            })
        
        return {
            'transacao': transacao,
            'parcelas': parcelas,
            'total_parcelas': transacao[9] or 1,
            'parcelas_json': json.dumps(parcelas, default=str) if parcelas else '[]'
        }
    
    @staticmethod
    def atualizar_transacao(cursor, conexao, sequencia, user_id, dados):
        """Atualiza a transação e suas parcelas"""
        
        # Busca tipo original
        cursor.execute("""
            SELECT tipo FROM transacoes
            WHERE sequencia_transacoes = %s AND user_id = %s AND ativo = 1
        """, (sequencia, user_id))
        
        tipo_result = cursor.fetchone()
        if not tipo_result:
            return {'success': False, 'error': 'Transação não encontrada'}
        
        tipo = tipo_result[0]
        
        # Extrai dados
        descricao = dados.get('descricao', '').strip()
        valor = dados.get('valor_total', 0.0)
        data_emissao = dados.get('data_emissao') or None
        data_vencimento = dados.get('data_vencimento') or None
        categoria_id = dados.get('categoria_id') or None
        total_parcelas = int(dados.get('total_parcelas', 1))
        
        # Busca dados atuais para auditoria
        cursor.execute("""
            SELECT t.descricao, t.valor_total, t.data_emissao, t.data_vencimento, 
                   t.categoria_id, ct.nome AS categoria_nome, t.total_parcelas
            FROM transacoes t
            LEFT JOIN categorias_financas ct ON t.categoria_id = ct.id
            WHERE t.sequencia_transacoes = %s AND t.user_id = %s
        """, (sequencia, user_id))
        
        dados_antes = cursor.fetchone()
        if not dados_antes:
            return {'success': False, 'error': 'Dados não encontrados'}
        
        total_parcelas_antes = dados_antes[6] if dados_antes else 1
        
        # Atualiza transação principal
        cursor.execute("""
            UPDATE transacoes 
            SET descricao = %s, 
                valor_total = %s, 
                data_emissao = %s,
                data_vencimento = %s,
                categoria_id = %s,
                total_parcelas = %s,
                data_alteracao = CURRENT_TIMESTAMP
            WHERE sequencia_transacoes = %s AND user_id = %s
        """, (descricao, valor, data_emissao, data_vencimento, categoria_id, total_parcelas, sequencia, user_id))
        
        # Gerencia parcelas
        EditarTransacaoService._gerenciar_parcelas(
            cursor, sequencia, user_id, tipo, 
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
    def _gerenciar_parcelas(cursor, sequencia, user_id, tipo, descricao, valor, 
                            total_parcelas, total_parcelas_antes, intervalo_dias, 
                            primeiro_vencimento, parcelas_input, data_emissao):
        """Gerencia criação/atualização/remoção de parcelas"""
        
        # Busca parcelas existentes
        cursor.execute("""
            SELECT sequencia_transacoes, numero_parcela, valor_total, data_vencimento
            FROM transacoes
            WHERE transacao_pai_id = %s AND ativo = 1
            ORDER BY numero_parcela
        """, (sequencia,))
        parcelas_existentes = cursor.fetchall()
        
        if total_parcelas > 1:
            # Calcula valores das parcelas
            if parcelas_input and len(parcelas_input) > 0:
                valores_parcelas = []
                for p in parcelas_input:
                    try:
                        val = float(p['valor']) if isinstance(p['valor'], (int, float)) else float(p['valor'])
                    except (ValueError, TypeError):
                        val = valor / total_parcelas
                    valores_parcelas.append(val)
            else:
                valores_parcelas = [valor / total_parcelas] * total_parcelas
            
            # Remove parcelas extras (se reduziu o número de parcelas)
            if len(parcelas_existentes) > total_parcelas:
                cursor.execute("""
                    UPDATE transacoes 
                    SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                    WHERE transacao_pai_id = %s AND ativo = 1 AND numero_parcela > %s
                """, (sequencia, total_parcelas))
            
            # Garante que primeiro_vencimento seja uma string válida ou usa a data atual
            if not primeiro_vencimento:
                primeiro_vencimento = datetime.now().strftime('%Y-%m-%d')
            elif isinstance(primeiro_vencimento, (datetime, datetime.date)):
                primeiro_vencimento = primeiro_vencimento.strftime('%Y-%m-%d')
            
            # Atualiza ou cria parcelas
            for i in range(1, total_parcelas + 1):
                if i == 1:
                    data_venc_parcela = primeiro_vencimento
                else:
                    try:
                        data_base = datetime.strptime(str(primeiro_vencimento)[:10], '%Y-%m-%d')
                    except ValueError:
                        data_base = datetime.now()
                    data_venc_parcela = (data_base + timedelta(days=(i - 1) * int(intervalo_dias or 30))).strftime('%Y-%m-%d')
                
                valor_parcela = valores_parcelas[i-1] if i <= len(valores_parcelas) else (valor / total_parcelas)
                parcela_existente = next((p for p in parcelas_existentes if p[1] == i), None)
                
                if parcela_existente:
                    cursor.execute("""
                        UPDATE transacoes 
                        SET valor_total = %s, 
                            valor_parcela = %s,
                            data_vencimento = %s,
                            descricao = %s,
                            data_alteracao = CURRENT_TIMESTAMP
                        WHERE sequencia_transacoes = %s
                    """, (valor_parcela, valor_parcela, data_venc_parcela, 
                          f'{descricao} - Parcela {i}/{total_parcelas}', parcela_existente[0]))
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
                          f'{descricao} - Parcela {i}/{total_parcelas}', None,
                          data_emissao, data_venc_parcela, total_parcelas, i, i, sequencia))
            
            # Atualiza intervalo na transação pai
            cursor.execute("""
                UPDATE transacoes 
                SET intervalo_dias = %s 
                WHERE sequencia_transacoes = %s AND user_id = %s
            """, (intervalo_dias, sequencia, user_id))
            
        elif total_parcelas_antes > 1 and total_parcelas == 1:
            # Se alterou de parcelado para parcela única, inativa todas as parcelas filhas
            cursor.execute("""
                UPDATE transacoes 
                SET ativo = 0, excluido_em = CURRENT_TIMESTAMP 
                WHERE transacao_pai_id = %s AND ativo = 1
            """, (sequencia,))
    
    @staticmethod
    def _get_proxima_sequencia(cursor, user_id):
        cursor.execute("SELECT COALESCE(MAX(sequencia_transacoes), 0) + 1 FROM transacoes WHERE user_id = %s", (user_id,))
        return cursor.fetchone()[0]