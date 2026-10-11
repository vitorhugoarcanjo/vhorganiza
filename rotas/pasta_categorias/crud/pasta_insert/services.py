# rotas/pasta_categorias/crud/pasta_insert/services.py
# ==========================================================
# INSERIR CATEGORIA - SERVICES
# ==========================================================

import logging
from datetime import date

logger = logging.getLogger(__name__)


class InserirCategoriaService:

    @staticmethod
    def get_proxima_sequencia(cursor, usuario_id, modulo):
        """Retorna a próxima sequência visual de categorias do usuário + módulo"""
        cursor.execute("""
            SELECT COALESCE(MAX(sequencia_categorias), 0) + 1
            FROM categorias
            WHERE usuario_id = %s AND modulo = %s
        """, (usuario_id, modulo))
        res = cursor.fetchone()
        return res[0] if res else 1

    @staticmethod
    def gerar_numero(sequencia, ano=None):
        """Gera o numero formatado: CAT-2026-0001"""
        if ano is None:
            ano = date.today().year
        return f'CAT-{ano}-{str(sequencia).zfill(4)}'

    @staticmethod
    def verificar_duplicada(cursor, usuario_id, modulo, nome):
        """Verifica se já existe uma categoria com o mesmo nome (case-insensitive)"""
        cursor.execute("""
            SELECT id FROM categorias
            WHERE usuario_id = %s
              AND modulo = %s
              AND LOWER(nome) = LOWER(%s)
        """, (usuario_id, modulo, nome))
        return cursor.fetchone()

    @staticmethod
    def criar_categoria(cursor, usuario_id, dados):
        """
        Cria uma nova categoria.
        Retorna (sucesso: bool, resultado: dict|str)
        """
        try:
            nome    = dados['nome']
            cor     = dados.get('cor') or '#CCCCCC'
            modulo  = dados['modulo']

            # Verifica duplicada
            if InserirCategoriaService.verificar_duplicada(cursor, usuario_id, modulo, nome):
                return False, f'Já existe uma categoria "{nome}" nesse módulo'

            # Gera sequência + numero
            sequencia = InserirCategoriaService.get_proxima_sequencia(cursor, usuario_id, modulo)
            numero    = InserirCategoriaService.gerar_numero(sequencia)

            cursor.execute("""
                INSERT INTO categorias (
                    usuario_id, modulo, sequencia_categorias, numero,
                    nome, cor, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                RETURNING id
            """, (usuario_id, modulo, sequencia, numero, nome, cor))

            categoria_id = cursor.fetchone()[0]

            return True, {
                'categoria_id': categoria_id,
                'sequencia':    sequencia,
                'numero':       numero,
                'mensagem':     f'Categoria "{nome}" criada com sucesso!'
            }

        except Exception as e:
            msg = f"Erro ao inserir categoria: {e}"
            logger.error(msg)
            return False, msg