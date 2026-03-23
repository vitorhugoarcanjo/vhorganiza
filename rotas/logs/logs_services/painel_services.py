import os
import sqlite3
import time
import traceback
from datetime import datetime
from flask import request, session
import json

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

class LogService:
    """Serviço para gerenciar logs do sistema"""
    
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(caminho_banco)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def registrar_erro(mensagem, arquivo=None, linha=None, stack_trace=None):
        """Registra um erro no banco"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO logs_erros (mensagem, arquivo, linha, user_id, rota, metodo, stack_trace)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                mensagem[:500],
                arquivo,
                linha,
                session.get('user_id'),  # ← mudou para user_id
                request.path if request else None,
                request.method if request else None,
                stack_trace[:1000] if stack_trace else None
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao registrar log de erro: {e}")
            return False
    
    @staticmethod
    def registrar_acesso(user_id, ip, user_agent, rota, metodo, status_code, tempo_resposta):
        """Registra um acesso no banco"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO logs_acesso (user_id, ip, user_agent, rota, metodo, status_code, tempo_resposta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                ip[:45],
                user_agent[:500] if user_agent else None,
                rota[:255],
                metodo[:10],
                status_code,
                tempo_resposta
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao registrar log de acesso: {e}")
            return False
    
    @staticmethod
    def registrar_acao(user_id, acao, tabela_afetada, registro_id, dados_antes=None, dados_depois=None):
        """Registra uma ação do usuário"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            dados_antes_json = json.dumps(dados_antes) if dados_antes else None
            dados_depois_json = json.dumps(dados_depois) if dados_depois else None
            
            cursor.execute("""
                INSERT INTO logs_acao (user_id, acao, tabela_afetada, registro_id, dados_antes, dados_depois, ip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                acao[:100],
                tabela_afetada[:50],
                registro_id,
                dados_antes_json,
                dados_depois_json,
                request.remote_addr if request else None
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao registrar log de ação: {e}")
            return False
    
    @staticmethod
    def listar_erros(limite=100, offset=0, filtro=None):
        """Lista erros com paginação e filtro"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT le.*, u.nome as usuario_nome 
                FROM logs_erros le
                LEFT JOIN cadastre_se u ON le.user_id = u.id
            """
            params = []
            
            if filtro:
                query += " WHERE le.mensagem LIKE ?"
                params.append(f"%{filtro}%")
            
            query += " ORDER BY le.data_hora DESC LIMIT ? OFFSET ?"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            erros = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM logs_erros")
            total = cursor.fetchone()['total']
            
            conn.close()
            return {'dados': erros, 'total': total}
        except Exception as e:
            print(f"Erro ao listar erros: {e}")
            return {'dados': [], 'total': 0}
    
    @staticmethod
    def obter_erro_por_id(erro_id):
        """Obtém detalhes de um erro específico"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT le.*, u.nome as usuario_nome 
                FROM logs_erros le
                LEFT JOIN cadastre_se u ON le.user_id = u.id
                WHERE le.id = ?
            """, (erro_id,))
            
            erro = cursor.fetchone()
            conn.close()
            return erro
        except Exception as e:
            print(f"Erro ao obter erro: {e}")
            return None
        
    @staticmethod
    def estatisticas():
        """Retorna estatísticas dos logs"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            # Total de erros
            cursor.execute("SELECT COUNT(*) as total FROM logs_erros")
            total_erros = cursor.fetchone()['total']
            
            # Total de acessos (páginas carregadas)
            cursor.execute("SELECT COUNT(*) as total FROM logs_acesso")
            total_acessos = cursor.fetchone()['total']
            
            # Total de usuários únicos (que já acessaram)
            cursor.execute("SELECT COUNT(DISTINCT user_id) as total FROM logs_acesso WHERE user_id IS NOT NULL")
            total_usuarios = cursor.fetchone()['total']
            
            # Usuários ativos nos últimos 7 dias (acessaram)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as total FROM logs_acesso 
                WHERE data_hora >= date('now', '-7 days') AND user_id IS NOT NULL
            """)
            usuarios_ativos = cursor.fetchone()['total']
            
            # Novos cadastros nos últimos 7 dias
            cursor.execute("""
                SELECT COUNT(*) as total FROM cadastre_se 
                WHERE data_criacao >= date('now', '-7 days')
            """)
            novos_cadastros = cursor.fetchone()['total']
            
            # Erros nos últimos 7 dias
            cursor.execute("""
                SELECT COUNT(*) as total FROM logs_erros 
                WHERE data_hora >= date('now', '-7 days')
            """)
            erros_7dias = cursor.fetchone()['total']
            
            conn.close()
            
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
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
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
                WHERE data_hora >= ? AND data_hora < ?
            """, (data_inicio, data_fim))
            total_acessos = cursor.fetchone()[0]
            
            # Usuários únicos
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM logs_acesso 
                WHERE data_hora >= ? AND data_hora < ? AND user_id IS NOT NULL
            """, (data_inicio, data_fim))
            usuarios_unicos = cursor.fetchone()[0]
            
            # Total de erros
            cursor.execute("""
                SELECT COUNT(*) FROM logs_erros 
                WHERE data_hora >= ? AND data_hora < ?
            """, (data_inicio, data_fim))
            total_erros = cursor.fetchone()[0]
            
            # Rotas mais acessadas (top 10)
            cursor.execute("""
                SELECT rota, COUNT(*) as total 
                FROM logs_acesso 
                WHERE data_hora >= ? AND data_hora < ?
                GROUP BY rota 
                ORDER BY total DESC 
                LIMIT 10
            """, (data_inicio, data_fim))
            rotas = [{"rota": r[0], "total": r[1]} for r in cursor.fetchall()]
            
            # Verificar se já existe resumo para este mês
            cursor.execute("""
                SELECT id FROM logs_resumo_mensal 
                WHERE ano = ? AND mes = ?
            """, (ano, mes))
            existe = cursor.fetchone()
            
            if existe:
                # Atualiza existente
                cursor.execute("""
                    UPDATE logs_resumo_mensal 
                    SET total_acessos = ?, usuarios_unicos = ?, total_erros = ?, rotas_mais_acessadas = ?
                    WHERE ano = ? AND mes = ?
                """, (total_acessos, usuarios_unicos, total_erros, json.dumps(rotas), ano, mes))
            else:
                # Insere novo
                cursor.execute("""
                    INSERT INTO logs_resumo_mensal (ano, mes, total_acessos, usuarios_unicos, total_erros, rotas_mais_acessadas)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ano, mes, total_acessos, usuarios_unicos, total_erros, json.dumps(rotas)))
            
            conn.commit()
            conn.close()
            
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
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            data_inicio = f"{ano}-{mes:02d}-{dia:02d}"
            data_fim = f"{ano}-{mes:02d}-{dia+1:02d}" if dia < 31 else f"{ano}-{mes+1:02d}-01"
            
            cursor.execute("""
                SELECT COUNT(*) FROM logs_acesso 
                WHERE data_hora >= ? AND data_hora < ?
            """, (data_inicio, data_fim))
            total_acessos = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM logs_erros 
                WHERE data_hora >= ? AND data_hora < ?
            """, (data_inicio, data_fim))
            total_erros = cursor.fetchone()[0]
            
            conn.close()
            
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
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            # ANTES DE REMOVER, GERA RESUMO DO MÊS PASSADO SE NECESSÁRIO
            from datetime import datetime, timedelta
            data_corte = datetime.now() - timedelta(days=dias)
            
            # Verifica se precisa gerar resumo do mês passado
            mes_passado = data_corte.replace(day=1)
            cursor.execute("""
                SELECT id FROM logs_resumo_mensal 
                WHERE ano = ? AND mes = ?
            """, (mes_passado.year, mes_passado.month))
            
            if not cursor.fetchone():
                LogService.gerar_resumo_mensal(mes_passado.year, mes_passado.month)
            
            # Remove logs antigos
            cursor.execute(f"""
                DELETE FROM logs_acesso 
                WHERE data_hora < datetime('now', '-{dias} days')
            """)
            
            cursor.execute(f"""
                DELETE FROM logs_erros 
                WHERE data_hora < datetime('now', '-{dias} days')
            """)
            
            cursor.execute(f"""
                DELETE FROM logs_acao 
                WHERE data_hora < datetime('now', '-{dias} days')
            """)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao limpar logs antigos: {e}")
            return False
    
    @staticmethod
    def obter_relatorio_anual(ano):
        """Retorna relatório anual completo a partir dos resumos mensais"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mes, total_acessos, usuarios_unicos, total_erros, rotas_mais_acessadas
                FROM logs_resumo_mensal
                WHERE ano = ?
                ORDER BY mes
            """, (ano,))
            
            dados = cursor.fetchall()
            conn.close()
            
            # Calcular totais anuais
            total_acessos_ano = sum(d['total_acessos'] for d in dados)
            usuarios_unicos_ano = sum(d['usuarios_unicos'] for d in dados)
            total_erros_ano = sum(d['total_erros'] for d in dados)
            
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
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    la.*,
                    strftime('%d/%m/%Y %H:%M:%S', la.data_hora, 'localtime') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
            """
            params = []
            
            if filtro:
                query += " WHERE la.rota LIKE ? OR u.nome LIKE ? OR u.email LIKE ?"
                params.append(f"%{filtro}%")
                params.append(f"%{filtro}%")
                params.append(f"%{filtro}%")
            
            query += " ORDER BY la.data_hora DESC LIMIT ? OFFSET ?"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            acessos = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM logs_acesso")
            total = cursor.fetchone()['total']
            
            conn.close()
            return {'dados': acessos, 'total': total}
        except Exception as e:
            print(f"Erro ao listar acessos: {e}")
            return {'dados': [], 'total': 0}

    @staticmethod
    def obter_acesso_por_id(acesso_id):
        """Obtém detalhes de um acesso específico"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    la.*,
                    strftime('%d/%m/%Y %H:%M:%S', la.data_hora, 'localtime') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
                WHERE la.id = ?
            """, (acesso_id,))
            
            acesso = cursor.fetchone()
            conn.close()
            return acesso
        except Exception as e:
            print(f"Erro ao obter acesso: {e}")
            return None

    @staticmethod
    def obter_acessos_por_usuario(user_id, limite=100):
        """Retorna acessos de um usuário específico"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    la.*,
                    strftime('%d/%m/%Y %H:%M:%S', la.data_hora, 'localtime') as data_hora_br,
                    u.nome as usuario_nome, 
                    u.email as usuario_email, 
                    u.telefone as usuario_telefone
                FROM logs_acesso la
                LEFT JOIN cadastre_se u ON la.user_id = u.id
                WHERE la.user_id = ?
                ORDER BY la.data_hora DESC
                LIMIT ?
            """, (user_id, limite))
            
            acessos = cursor.fetchall()
            conn.close()
            return acessos
        except Exception as e:
            print(f"Erro ao obter acessos do usuário: {e}")
            return []

    @staticmethod
    def obter_nome_usuario(user_id):
        """Retorna apenas o nome do usuário pelo ID"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT nome FROM cadastre_se WHERE id = ?", (user_id,))
            resultado = cursor.fetchone()
            conn.close()
            
            return resultado['nome'] if resultado else None
        except Exception as e:
            print(f"Erro ao obter nome do usuário: {e}")
            return None

    @staticmethod
    def obter_dados_usuario(user_id):
        """Retorna todos os dados do usuário (nome, email, telefone)"""
        try:
            conn = LogService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT nome, email, telefone FROM cadastre_se WHERE id = ?", (user_id,))
            resultado = cursor.fetchone()
            conn.close()
            
            return {
                'nome': resultado['nome'] if resultado else None,
                'email': resultado['email'] if resultado else None,
                'telefone': resultado['telefone'] if resultado else None
            } if resultado else {'nome': None, 'email': None, 'telefone': None}
        except Exception as e:
            print(f"Erro ao obter dados do usuário: {e}")
            return {'nome': None, 'email': None, 'telefone': None}