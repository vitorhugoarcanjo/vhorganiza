def insert_cat_tarefa(nome, cor, user_id, cursor):
    cursor.execute('SELECT 1 FROM categorias_tarefas WHERE user_id = %s AND nome = %s', (user_id, nome))
    resultado = cursor.fetchone()

    if resultado:
        return False, f"Nome {nome} já existe!"
    
    cursor.execute('INSERT INTO categorias_tarefas (user_id, nome, cor) VALUES (%s, %s, %s)', (user_id, nome, cor))
    return True, f"Categoria {nome} criado com sucesso!"
