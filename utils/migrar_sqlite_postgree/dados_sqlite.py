# verificar_tarefas.py
import sqlite3

conn = sqlite3.connect('instance/banco_de_dados.db')
cursor = conn.cursor()

# Tarefas com categoria_id que não existe em categorias_tarefas
cursor.execute("""
    SELECT COUNT(*) 
    FROM tarefas t
    LEFT JOIN categorias_tarefas c ON t.categoria_id = c.id
    WHERE t.categoria_id IS NOT NULL AND c.id IS NULL
""")
print(f"Tarefas com categoria inválida: {cursor.fetchone()[0]}")

# Tarefas sem categoria
cursor.execute("SELECT COUNT(*) FROM tarefas WHERE categoria_id IS NULL")
print(f"Tarefas sem categoria: {cursor.fetchone()[0]}")

# Total
cursor.execute("SELECT COUNT(*) FROM tarefas")
print(f"Total tarefas: {cursor.fetchone()[0]}")

conn.close()