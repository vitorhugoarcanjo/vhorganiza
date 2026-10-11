# rotas/pasta_categorias/crud/pasta_edit/services.py
# ==========================================================
# EDITAR CATEGORIA - SERVICES
# ==========================================================

import logging

logger = logging.getLogger(__name__)


class EditarCategoriaService:

    @staticmethod
    def buscar_categoria_por_id(cursor, categoria_id, usuario_id):
        """
        Retorna tupla:
          0  id
          1  usuario_id
          2  modulo
          3  sequencia_categorias
          4  numero
          5  nome
          6  cor
          7  ativo
          8  created_at
          9  updated_at
        """
        cursor.execute("""
            SELECT id, usuario_id, modulo, sequencia_categorias, numero,
                   nome, cor, ativo, created_at, updated_at
            FROM categorias
            WHERE id = %s AND usuario_id = %s
        """, (categoria_id, usuario_id))
        return cursor.fetchone()

    @staticmethod
    def verificar_duplicada(cursor, usuario_id, modulo, nome, categoria_id):
        """Verifica se OUTRA categoria tem o mesmo nome"""
        cursor.execute("""
            SELECT id FROM categorias
            WHERE usuario_id = %s
              AND modulo = %s
              AND LOWER(nome) = LOWER(%s)
              AND id != %s
        """, (usuario_id, modulo, nome, categoria_id))
        return cursor.fetchone()

    @staticmethod
    def atualizar_categoria(cursor, categoria_id, usuario_id, dados):
        """Atualiza a categoria. Retorna dados_antes/dados_depois pra auditoria."""
        categoria_atual = EditarCategoriaService.buscar_categoria_por_id(cursor, categoria_id, usuario_id)
        if not categoria_atual:
            return {'success': False, 'error': 'Categoria não encontrada'}

        # Verifica duplicada (nome mudou?)
        novo_nome = dados['nome']
        nome_atual = categoria_atual[5]
        if novo_nome.lower() != nome_atual.lower():
            if EditarCategoriaService.verificar_duplicada(
                cursor, usuario_id, categoria_atual[2], novo_nome, categoria_id
            ):
                return {'success': False, 'error': f'Já existe uma categoria "{novo_nome}" nesse módulo'}

        # Dados ANTES
        dados_antes = {
            'nome': categoria_atual[5],
            'cor':  categoria_atual[6],
        }

        # Dados DEPOIS
        dados_depois = {
            'nome': novo_nome,
            'cor':  dados['cor'],
        }

        cursor.execute("""
            UPDATE categorias
            SET nome = %s,
                cor = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_id = %s
        """, (novo_nome, dados['cor'], categoria_id, usuario_id))

        return {
            'success': True,
            'id_interno': categoria_id,
            'modulo': categoria_atual[2],
            'dados_antes': dados_antes,
            'dados_depois': dados_depois,
        }