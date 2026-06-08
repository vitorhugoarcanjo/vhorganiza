import time
import traceback
from datetime import datetime
from flask import request, session
from utils.database.conexao_global import ini_conexao
import json
from psycopg2.extras import RealDictCursor


class LogService:
    """Serviço para gerenciar logs do sistema"""
    
    @staticmethod
    def get_db_connection():
        return ini_conexao()
    
    @staticmethod
    def registrar_erro(mensagem, arquivo=None, linha=None, stack_trace=None):
        """Registra um erro no banco"""
        try:
            conexao, cursor = LogService.get_db_connection()

            user_id = session.get('user_id') if session else None
            rota = request.path if request else None
            metodo = request.method if request else None

            
            cursor.execute("""
                INSERT INTO logs_erros (mensagem, arquivo, linha, user_id, rota, metodo, stack_trace)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                mensagem[:500],
                arquivo,
                linha,
                user_id,  # ← mudou para user_id
                rota,
                metodo,
                stack_trace[:1000] if stack_trace else None
            ))
            conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao registrar log de erro: {e}")
            return False
    
    @staticmethod
    def registrar_acesso(user_id, ip, user_agent, rota, metodo, status_code, tempo_resposta):
        """Registra um acesso no banco"""
        try:
            # ROTAS IGNORADAS 
            rotas_ignoradas = [
                '/static/',
                '/favicon.ico',
                '/tarefas/detalhes/',
                '/tarefas/limpar_filtros/',
                '/tarefas/',
                '/categorias/',
                '/financas/',
                '/config/',
                '/dashboard',
            ]

            # VALIDAÇÃO DAS ROTAS IGNORADAS
            if any(rota.startswith(r) for r in rotas_ignoradas):
                return True

            conexao, cursor = LogService.get_db_connection()
            
            
            cursor.execute("""
                INSERT INTO logs_acesso (user_id, ip, user_agent, rota, metodo, status_code, tempo_resposta)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                ip[:45],
                user_agent[:500] if user_agent else None,
                rota[:255],
                metodo[:10],
                status_code,
                tempo_resposta
            ))
            conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao registrar log de acesso: {e}")
            return False
    
    @staticmethod
    def registrar_acao(user_id, acao, tabela_afetada, registro_id, dados_antes=None, dados_depois=None):
        """Registra uma ação do usuário"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            dados_antes_json = json.dumps(dados_antes) if dados_antes else None
            dados_depois_json = json.dumps(dados_depois) if dados_depois else None
            
            cursor.execute("""
                INSERT INTO logs_acao (user_id, acao, tabela_afetada, registro_id, dados_antes, dados_depois, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                acao[:100],
                tabela_afetada[:50],
                registro_id,
                dados_antes_json,
                dados_depois_json,
                request.remote_addr if request else None
            ))
            conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao registrar log de ação: {e}")
            return False
    
    @staticmethod
    def listar_erros(limite=100, offset=0, filtro=None):
        """Lista erros com paginação e filtro"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            # Usa cursor que retorna dicionários
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT le.*, u.nome as usuario_nome 
                FROM logs_erros le
                LEFT JOIN cadastre_se u ON le.user_id = u.id
            """
            params = []
            
            if filtro:
                query += " WHERE le.mensagem LIKE %s"
                params.append(f"%{filtro}%")
            
            query += " ORDER BY le.data_hora DESC LIMIT %s OFFSET %s"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            erros = cursor.fetchall()
            
            # Para o total, ainda precisa do cursor normal ou usar o mesmo
            cursor.execute("SELECT COUNT(*) as total FROM logs_erros")
            total = cursor.fetchone()['total']
            
            return {'dados': erros, 'total': total}
        except Exception as e:
            print(f"Erro ao listar erros: {e}")
            return {'dados': [], 'total': 0}
    
    @staticmethod
    def obter_erro_por_id(erro_id):
        """Obtém detalhes de um erro específico"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT le.*, u.nome as usuario_nome 
                FROM logs_erros le
                LEFT JOIN cadastre_se u ON le.user_id = u.id
                WHERE le.id = %s
            """, (erro_id,))
            erro = cursor.fetchone()
            return erro
        
        except Exception as e:
            print(f"Erro ao obter erro: {e}")
            return None 


        
    @staticmethod
    def estatisticas():
        """Retorna estatísticas dos logs"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            # Total de erros
            cursor.execute("SELECT COUNT(*) as total FROM logs_erros")
            total_erros = cursor.fetchone()[0]
            
            # Total de acessos (páginas carregadas)
            cursor.execute("SELECT COUNT(*) as total FROM logs_acesso")
            total_acessos = cursor.fetchone()[0]
            
            # Total de usuários únicos (que já acessaram)
            cursor.execute("SELECT COUNT(DISTINCT user_id) as total FROM logs_acesso WHERE user_id IS NOT NULL")
            total_usuarios = cursor.fetchone()[0]
            
            # Usuários ativos nos últimos 7 dias (acessaram)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as total FROM logs_acesso 
                WHERE data_hora >= CURRENT_DATE - INTERVAL '7 days' AND user_id IS NOT NULL
            """)
            usuarios_ativos = cursor.fetchone()[0]
            
            # Novos cadastros nos últimos 7 dias
            cursor.execute("""
                SELECT COUNT(*) as total FROM cadastre_se 
                WHERE data_criacao >= CURRENT_DATE - INTERVAL '7 days'
            """)
            novos_cadastros = cursor.fetchone()[0]
            
            # Erros nos últimos 7 dias
            cursor.execute("""
                SELECT COUNT(*) as total FROM logs_erros 
                WHERE data_hora >= CURRENT_DATE - INTERVAL '7 days'
            """)
            erros_7dias = cursor.fetchone()[0]
            
            
            return {
                'total_erros': total_erros,
                'total_acessos': total_acessos,
                'total_usuarios': total_usuarios,
                'usuarios_ativos': usuarios_ativos,
                'novos_cadastros': novos_cadastros,
                'erros_7dias': erros_7dias
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_erros': 0,
                'total_acessos': 0,
                'total_usuarios': 0,
                'usuarios_ativos': 0,
                'novos_cadastros': 0,
                'erros_7dias': 0
            }
            

    # ============================================
    # MÉTODOS DE RESUMO E LIMPEZA
    # ============================================
    
    @staticmethod
    def gerar_resumo_mensal(ano, mes):
        """Gera resumo de um mês específico"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            # Data início e fim do mês
            data_inicio = f"{ano}-{mes:02d}-01"
            # Último dia do mês
            if mes == 12:
                data_fim = f"{ano+1}-01-01"
            else:
                data_fim = f"{ano}-{mes+1:02d}-01"
            
            # Total de acessos no mês
            cursor.execute("""
                SELECT COUNT(*) FROM logs_acesso 
                WHERE data_hora >= %s AND data_hora < %s
            """, (data_inicio, data_fim))
            total_acessos = cursor.fetchone()[0]
            
            # Usuários únicos
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM logs_acesso 
                WHERE data_hora >= %s AND data_hora < %s AND user_id IS NOT NULL
            """, (data_inicio, data_fim))
            usuarios_unicos = cursor.fetchone()[0]
            
            # Total de erros
            cursor.execute("""
                SELECT COUNT(*) FROM logs_erros 
                WHERE data_hora >= %s AND data_hora < %s
            """, (data_inicio, data_fim))
            total_erros = cursor.fetchone()[0]
            
            # Rotas mais acessadas (top 10)
            cursor.execute("""
                SELECT rota, COUNT(*) as total 
                FROM logs_acesso 
                WHERE data_hora >= %s AND data_hora < %s
                GROUP BY rota 
                ORDER BY total DESC 
                LIMIT 10
            """, (data_inicio, data_fim))
            rotas = [{"rota": r[0], "total": r[1]} for r in cursor.fetchall()]
            
            # Verificar se já existe resumo para este mês
            cursor.execute("""
                SELECT id FROM logs_resumo_mensal 
                WHERE ano = %s AND mes = %s
            """, (ano, mes))
            existe = cursor.fetchone()
            
            if existe:
                # Atualiza existente
                cursor.execute("""
                    UPDATE logs_resumo_mensal 
                    SET total_acessos = %s, usuarios_unicos = %s, total_erros = %s, rotas_mais_acessadas = %s
                    WHERE ano = %s AND mes = %s
                """, (total_acessos, usuarios_unicos, total_erros, json.dumps(rotas), ano, mes))
            else:
                # Insere novo
                cursor.execute("""
                    INSERT INTO logs_resumo_mensal (ano, mes, total_acessos, usuarios_unicos, total_erros, rotas_mais_acessadas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (ano, mes, total_acessos, usuarios_unicos, total_erros, json.dumps(rotas)))
            
            conexao.commit()
            
            return {
                'ano': ano,
                'mes': mes,
                'total_acessos': total_acessos,
                'usuarios_unicos': usuarios_unicos,
                'total_erros': total_erros,
                'rotas_mais_acessadas': rotas
            }
        except Exception as e:
            print(f"Erro ao gerar resumo mensal: {e}")
            return None
    
    @staticmethod
    def gerar_resumo_diario(ano, mes, dia):
        """Gera resumo de um dia específico"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            data_inicio = f"{ano}-{mes:02d}-{dia:02d}"
            data_fim = f"{ano}-{mes:02d}-{dia+1:02d}" if dia < 31 else f"{ano}-{mes+1:02d}-01"
            
            cursor.execute("""
                SELECT COUNT(*) FROM logs_acesso 
                WHERE data_hora >= %s AND data_hora < %s
            """, (data_inicio, data_fim))
            total_acessos = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM logs_erros 
                WHERE data_hora >= %s AND data_hora < %s
            """, (data_inicio, data_fim))
            total_erros = cursor.fetchone()[0]
            
            
            return {
                'data': f"{ano}-{mes:02d}-{dia:02d}",
                'total_acessos': total_acessos,
                'total_erros': total_erros
            }
        except Exception as e:
            print(f"Erro ao gerar resumo diario: {e}")
            return None
    
    @staticmethod
    def limpar_logs_antigos(dias=30):
        """Remove logs mais antigos que X dias (preserva resumos)"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            # ANTES DE REMOVER, GERA RESUMO DO MÊS PASSADO SE NECESSÁRIO
            from datetime import datetime, timedelta
            data_corte = datetime.now() - timedelta(days=dias)
            
            # Verifica se precisa gerar resumo do mês passado
            mes_passado = data_corte.replace(day=1)
            cursor.execute("""
                SELECT id FROM logs_resumo_mensal 
                WHERE ano = %s AND mes = %s
            """, (mes_passado.year, mes_passado.month))
            
            if not cursor.fetchone():
                LogService.gerar_resumo_mensal(mes_passado.year, mes_passado.month)
            
            # Remove logs antigos
            cursor.execute(f"""
                DELETE FROM logs_acesso 
                WHERE data_hora < CURRENT_TIMESTAMP - INTERVAL '{dias} days'
            """)
            
            cursor.execute(f"""
                DELETE FROM logs_erros 
                WHERE data_hora < CURRENT_TIMESTAMP - INTERVAL '{dias} days'
            """)
            
            cursor.execute(f"""
                DELETE FROM logs_acao 
                WHERE data_hora < CURRENT_TIMESTAMP - INTERVAL '{dias} days'
            """)    
            conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao limpar logs antigos: {e}")
            return False
    
    @staticmethod
    def obter_relatorio_anual(ano):
        """Retorna relatório anual completo a partir dos resumos mensais"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            cursor.execute("""
                SELECT mes, total_acessos, usuarios_unicos, total_erros, rotas_mais_acessadas
                FROM logs_resumo_mensal
                WHERE ano = %s
                ORDER BY mes
            """, (ano,))
            dados = cursor.fetchall()
            
            # Calcular totais anuais
            total_acessos_ano = sum(row[1] for row in dados) if dados else 0
            usuarios_unicos_ano = sum(row[2] for row in dados) if dados else 0
            total_erros_ano = sum(row[3] for row in dados) if dados else 0
            
            return {
                'ano': ano,
                'meses': dados,
                'total_acessos': total_acessos_ano,
                'usuarios_unicos': usuarios_unicos_ano,
                'total_erros': total_erros_ano
            }
        except Exception as e:
            print(f"Erro ao obter relatório anual: {e}")
            return None
        

    @staticmethod
    def listar_acessos(limite=100, offset=0, filtro=None):
        """Lista acessos com paginação e filtro"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            # Habilita dicionários no cursor
            from psycopg2.extras import RealDictCursor
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    la.*,
                    TO_CHAR(la.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
            """
            params = []
            
            if filtro:
                query += " WHERE la.rota LIKE %s OR u.nome LIKE %s OR u.email LIKE %s"
                params.extend([f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"])
            
            query += " ORDER BY la.data_hora DESC LIMIT %s OFFSET %s"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            acessos = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM logs_acesso")
            total = cursor.fetchone()['total']  # Agora é dicionário
            
            return {'dados': acessos, 'total': total}
        except Exception as e:
            print(f"Erro ao listar acessos: {e}")
            return {'dados': [], 'total': 0}

    @staticmethod
    def obter_acesso_por_id(acesso_id):
        """Obtém detalhes de um acesso específico"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            # Adiciona o RealDictCursor aqui também
            from psycopg2.extras import RealDictCursor
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    la.*,
                    TO_CHAR(la.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
                WHERE la.id = %s
            """, (acesso_id,))
            acesso = cursor.fetchone()
            return acesso
        
        except Exception as e:
            print(f"Erro ao obter acesso: {e}")
            return None

    @staticmethod
    def obter_acessos_por_usuario(user_id, limite=100):
        """Retorna acessos de um usuário específico"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            from psycopg2.extras import RealDictCursor
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    la.*,
                    TO_CHAR(la.data_hora AT TIME ZONE 'America/Cuiaba', 'DD/MM/YYYY HH24:MI:SS') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
                WHERE la.user_id = %s
                ORDER BY la.data_hora DESC
                LIMIT %s
            """, (user_id, limite))
            acessos = cursor.fetchall()
            return acessos
        
        except Exception as e:
            print(f"Erro ao obter acessos do usuário: {e}")
            return []

    @staticmethod
    def obter_nome_usuario(user_id):
        """Retorna apenas o nome do usuário pelo ID"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            cursor.execute("SELECT nome FROM cadastre_se WHERE id = %s", (user_id,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        
        except Exception as e:
            print(f"Erro ao obter nome do usuário: {e}")
            return None

    @staticmethod
    def obter_dados_usuario(user_id):
        """Retorna todos os dados do usuário (nome, email, telefone)"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            cursor.execute("SELECT nome, email, telefone FROM cadastre_se WHERE id = %s", (user_id,))
            resultado = cursor.fetchone()
            return {
                'nome': resultado[0] if resultado else None,
                'email': resultado[1] if resultado else None,
                'telefone': resultado[2] if resultado else None,
            } if resultado else {'nome': None, 'email': None, 'telefone': None}
        
        except Exception as e:
            print(f"Erro ao obter dados do usuário: {e}")
            return {'nome': None, 'email': None, 'telefone': None}
        
    @staticmethod
    def listar_ataques(limite=100):
        """Lista tentativas de ataque"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            # Usa cursor que retorna dicionários
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM logs_ataques 
                ORDER BY data_hora DESC 
                LIMIT %s
            """, (limite,))
            ataques = cursor.fetchall()
            return ataques
        
        except Exception as e:
            print(f"Erro ao listar ataques: {e}")
            return []

    @staticmethod
    def obter_ataque_por_id(ataque_id):
        """Obtém detalhes de uma tentativa de ataque"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            cursor = conexao.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM logs_ataques 
                WHERE id = %s
            """, (ataque_id,))
            ataque = cursor.fetchone()
            return ataque
        
        except Exception as e:
            print(f"Erro ao obter ataque: {e}")
            return None
        
    @staticmethod
    def registrar_ataque(ip, rota, metodo, user_agent, padrao):
        """Registra uma tentativa de ataque"""
        try:
            conexao, cursor = LogService.get_db_connection()
            
            
            cursor.execute("""
                INSERT INTO logs_ataques (ip, rota, metodo, user_agent, padrao_detectado)
                VALUES (%s, %s, %s, %s, %s)
            """, (ip, rota, metodo, user_agent, padrao))
            conexao.commit()
            return True
        
        except Exception as e:
            print(f"Erro ao registrar ataque: {e}")
            return False
