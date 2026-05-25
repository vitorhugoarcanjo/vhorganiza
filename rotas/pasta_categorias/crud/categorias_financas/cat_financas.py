def insert_cat_fin(nome, cor, user_id, cursor):
    cursor.execute('SELECT 1 FROM categorias_financas WHERE user_id = ? AND nome = ?', (user_id, nome))
    resultado = cursor.fetchone()

    if resultado:
        return False, f"Nome {nome} já existe!"
    
    cursor.execute('INSERT INTO categorias_financas (user_id, nome, cor) VALUES (?, ?, ?)', (user_id, nome, cor))
    return True, f"Categoria {nome} criado com sucesso!"