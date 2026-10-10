# rotas/pasta_categorias/crud/categorias_financas/cat_financas.py

def insert_cat_fin(nome, cor, usuario_id, cursor):
    cursor.execute(
        'SELECT 1 FROM categorias_financas WHERE usuario_id = %s AND nome = %s',
        (usuario_id, nome)
    )
    if cursor.fetchone():
        return False, f'Nome {nome} já existe!'

    cursor.execute(
        'INSERT INTO categorias_financas (usuario_id, nome, cor) VALUES (%s, %s, %s)',
        (usuario_id, nome, cor)
    )
    return True, f'Categoria {nome} criada com sucesso!'