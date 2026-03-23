# definir_master.py
import sqlite3
import os

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

def definir_usuario_master(email):
    conn = sqlite3.connect(caminho_banco)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, email FROM cadastre_se WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    
    if usuario:
        cursor.execute("UPDATE cadastre_se SET is_master = 1 WHERE id = ?", (usuario[0],))
        conn.commit()
        print(f"✅ Usuário '{usuario[1]}' ({email}) agora é MASTER!")
        
        # Mostra quem é master
        cursor.execute("SELECT id, nome, email FROM cadastre_se WHERE is_master = 1")
        masters = cursor.fetchall()
        print("\n👑 Usuários MASTER atuais:")
        for m in masters:
            print(f"   - {m[1]} ({m[2]})")
    else:
        print(f"❌ Usuário com email '{email}' não encontrado.")
    
    conn.close()

if __name__ == "__main__":
    email = input("Digite o email do usuário que será MASTER: ")
    definir_usuario_master(email)