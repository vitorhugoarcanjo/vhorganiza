# rotas/pasta_categorias/formatters.py
# ==========================================================
# FORMATADORES DO MÓDULO DE CATEGORIAS
# ==========================================================

from utils.fomatacoes.data_reutilizavel import formatar_data


class CategoriasFormatters:

    @staticmethod
    def formatar_categorias(categorias_raw):
        """
        Recebe lista de tuplas do banco e devolve lista de dicionários.
        Ordem da query em CategoriasQueries.get_categorias_base():
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
        resultado = []

        for c in categorias_raw:
            resultado.append({
                'id':                  c[0],
                'usuario_id':          c[1],
                'modulo':              c[2],
                'sequencia':           c[3],
                'numero':              c[4] or '',
                'nome':                c[5] or 'Sem nome',
                'cor':                 c[6] or '#6c757d',
                'ativo':               c[7],
                'created_at':          str(c[8]) if c[8] else '',
                'updated_at':          str(c[9]) if c[9] else '',
            })

        return resultado

    @staticmethod
    def formatar_detalhes(categoria_raw):
        """
        Formata UMA categoria (usado no modal de editar).
        Ordem da query em CategoriasQueries.get_detalhes_categoria():
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
        if not categoria_raw:
            return None

        return {
            'id':         categoria_raw[0],
            'usuario_id': categoria_raw[1],
            'modulo':     categoria_raw[2],
            'sequencia':  categoria_raw[3],
            'numero':     categoria_raw[4] or '',
            'nome':       categoria_raw[5] or 'Sem nome',
            'cor':        categoria_raw[6] or '#6c757d',
            'ativo':      categoria_raw[7],
            'created_at': str(categoria_raw[8]) if categoria_raw[8] else '',
            'updated_at': str(categoria_raw[9]) if categoria_raw[9] else '',
        }