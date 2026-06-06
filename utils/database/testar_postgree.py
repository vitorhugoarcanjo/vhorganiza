# testar_conexao.py
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

load_dotenv()

url = os.getenv('DATABASE_URL')
print(f"URL: {url}")

try:
    parsed = urlparse(url)
    print(f"Host: {parsed.hostname}")
    print(f"Porta: {parsed.port}")
    print(f"User: {parsed.username}")
    print(f"DB: {parsed.path[1:]}")
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password,
        port=parsed.port or 5432
    )
    print("✅ Conexão OK!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")