import os
import sqlite3
from script_migrar_bd import migrar_transacoes_com_backup

caminho_banco = os.path.join(os.getcwd(), 'instance', 'banco_de_dados.db')

def rodar():
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    migrar_transacoes_com_backup(cursor, caminho_banco)

    conexao.commit()
    conexao.close()

    print("🚀 Migração executada com sucesso!")

if __name__ == "__main__":
    rodar()