# 13 — Comandos

## 13.1 Build

```bash
# Build por módulo
python scripts/combine_static_financas.py
python scripts/combine_static_tarefas.py
python scripts/combine_static_orcamentos.py
```

## 13.2 Rodar Flask

```bash
python app.py
```

**Debug:** `Ctrl+C` pra parar.

## 13.3 Git

```bash
# Antes de sair do PC
git status
git add .
git commit -m "wip: salvando antes de sair"
git push origin <branch>

# Ao chegar no outro PC
git pull
```

## 13.4 Deploy (VPS)

```bash
# Conectar
ssh usuario@vhorganiza.com.br

# Ir pro projeto
cd /var/www/vhorganiza

# Atualizar código
git fetch origin
git reset --hard origin/main
git clean -fd

# Limpar cache Python
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Reiniciar
sudo systemctl restart gestao_financeira

# Confirmar
sudo systemctl status gestao_financeira
```

## 13.5 Debug em prod

```bash
# Ver logs em tempo real
sudo journalctl -u gestao_financeira -f

# Ver últimas 50 linhas
sudo journalctl -u gestao_financeira -n 50

# Ver logs de hoje
sudo journalctl -u gestao_financeira --since today
```

## 13.6 Python / venv

```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar uma lib específica
pip install weasyprint

# Congelar dependências
pip freeze > requirements.txt
```

## 13.7 PostgreSQL (PgAdmin ou psql)

```sql
-- Conectar
psql -h localhost -U usuario -d vhorganiza

-- Listar tabelas
\dt

-- Ver estrutura
\d+ orcamentos

-- Query simples
SELECT id, sequencia_orcamentos, numero, titulo FROM orcamentos LIMIT 10;
```

## 13.8 WeasyPrint (instalação Linux)

```bash
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
                    libfontconfig1 libcairo2 libgdk-pixbuf-2.0-0
pip install weasyprint
```

## 13.9 Atalhos úteis (bash)

```bash
# Buscar texto no projeto
grep -rn "termo" --include="*.py" --include="*.js"

# Buscar em templates
grep -rn "termo" templates/

# Listar arquivos por extensão
find . -name "*.py" | wc -l

# Remover pycache
find . -type d -name __pycache__ -exec rm -rf {} +
```

## 13.10 Atalhos (PowerShell — Windows)

```powershell
# Buscar texto
Select-String -Path ".\**\*.py" -Pattern "termo"

# Listar arquivos
Get-ChildItem -Recurse -Filter "*.py"

# Hash de arquivo
Get-FileHash arquivo.txt -Algorithm MD5

# Remover pycache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

## 13.11 Checklist antes de dormir

```bash
# 1. Commit
git status
git add .
git commit -m "wip: <o que fez>"
git push origin <branch>

# 2. Se tem algo não commitado, tá perdendo tempo
```

**Regra 2099:** sempre `git push` antes de sair.