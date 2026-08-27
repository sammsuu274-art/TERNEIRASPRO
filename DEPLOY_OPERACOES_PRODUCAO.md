# 🔄 OPERAÇÕES EM PRODUÇÃO — TerneirasPro no PythonAnywhere

> Procedimentos operacionais para manutenção e atualização após deployment inicial

---

## 📋 ÍNDICE

1. [Rotinas diárias](#1-rotinas-diárias)
2. [Backup e recuperação](#2-backup-e-recuperação)
3. [Atualizar código](#3-atualizar-código)
4. [Atualizar dependências](#4-atualizar-dependências)
5. [Monitoramento](#5-monitoramento)
6. [Performance](#6-otimização-de-performance)
7. [Segurança](#7-segurança-em-produção)
8. [Recuperação de desastres](#8-recuperação-de-desastres)

---

## 1. ROTINAS DIÁRIAS

### 1.1 Verificação matinal

**Executar quando iniciar trabalho:**

```bash
# Entrar no PythonAnywhere Bash Console

# Verificar status da aplicação
curl https://seu-username.pythonanywhere.com -I

# Resultado esperado:
# HTTP/1.1 200 OK
# ou
# HTTP/1.1 302 Redirect (login)

# Se 502 ou 500, algo está errado
```

Se erro:

```bash
# Verificar error log
tail -20 /var/log/seu_username.pythonanywhere.com.error.log

# Procurar por "error" ou "exception"
```

### 1.2 Verificação de diskspace

```bash
# Ver quanto espaço está usando
df -h ~

# Resultado esperado:
# Usado: <50% (deve ter espaço livre)

# Se >90%, fazer limpeza
du -sh ~/* | sort -hr
```

### 1.3 Verificar última modificação de db.sqlite3

```bash
stat ~/TerneirasPro/db.sqlite3 | grep Modify

# Mostrar quando banco foi atualizado pela última vez
# Deve ser recente (hoje ou ontem)
```

---

## 2. BACKUP E RECUPERAÇÃO

### 2.1 Fazer backup manual

**Recomendado:** Antes de qualquer mudança

```bash
# Criar backup com timestamp
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Verificar que foi criado
ls -lh ~/db.sqlite3.backup.* | head -5

# Resultado deve mostrar arquivo recente
```

### 2.2 Backup automático (script)

**Criar arquivo `~/backup_terneiras.sh`:**

```bash
#!/bin/bash

BACKUP_DIR="$HOME/backups"
DB_PATH="$HOME/TerneirasPro/db.sqlite3"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db.sqlite3.backup.$TIMESTAMP"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Fazer cópia
cp $DB_PATH $BACKUP_FILE

# Manter apenas últimos 30 backups
find $BACKUP_DIR -name "*.backup.*" -type f | sort -r | tail -n +31 | xargs rm -f

echo "Backup criado: $BACKUP_FILE"
```

**Usar:**

```bash
chmod +x ~/backup_terneiras.sh
~/backup_terneiras.sh

# Testar cron (executar todo dia às 2 da manhã)
# Adicionar a crontab:
# 0 2 * * * ~/backup_terneiras.sh
```

### 2.3 Download de backup para seu computador

**No seu computador:**

```bash
# Download do backup mais recente
scp seu_username@ssh.pythonanywhere.com:~/backups/db.sqlite3.backup.* ~/backups/

# Verificar
ls -lh ~/backups/
```

### 2.4 Restaurar de backup

**Se banco foi corrompido ou danificado:**

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Listar backups disponíveis
ls -lh ~/db.sqlite3.backup.*

# Escolher qual restaurar (ex: mais recente que funcionava)
BACKUP_FILE="~/db.sqlite3.backup.20260815_100000"

# Fazer cópia de segurança do banco corrompido
cp db.sqlite3 db.sqlite3.corrupted

# Restaurar
cp $BACKUP_FILE db.sqlite3

# Verificar que foi restaurado
ls -lh db.sqlite3

# Recarregar aplicação
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

# Testar
curl https://seu-username.pythonanywhere.com
```

---

## 3. ATUALIZAR CÓDIGO

### 3.1 Atualizar via Git (recomendado)

**Se projeto está em repositório:**

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Ver branch atual
git status

# Puxar atualizações
git pull origin main
# (ou a branch que usa)

# Se houve mudanças em models, aplicar migrations
python manage.py migrate

# Se houve mudanças em static, recoletar
python manage.py collectstatic --noinput

# Recarregar aplicação
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

# Testar
curl https://seu-username.pythonanywhere.com
```

### 3.2 Atualizar via upload de arquivos

**Se não usa Git:**

1. Download dos arquivos locais (seu computador)
2. Upload para PythonAnywhere via Web Files
3. Descompactar sobre os arquivos antigos (manter db.sqlite3)
4. Rodar migrations se necessário
5. Recarregar aplicação

```bash
# No PythonAnywhere, depois de upload:
cd ~/TerneirasPro

# Se houve mudanças em models
python manage.py migrate

# Recoletar estáticos
python manage.py collectstatic --noinput

# Recarregar
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

### 3.3 Rollback (desfazer atualização)

**Se atualização quebrou algo:**

```bash
cd ~/TerneirasPro

# Opção 1: Com Git
git revert HEAD  # Desfaz último commit
git pull

# Opção 2: Manual
# Restaurar arquivos de backup anterior
rm -rf ~/TerneirasPro
cp -r ~/TerneirasPro.backup ~/TerneirasPro

# Recarregar
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

---

## 4. ATUALIZAR DEPENDÊNCIAS

### 4.1 Atualizar requirements.txt

**Se há novo pacote ou versão atualizada:**

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Método 1: Atualizar dentro do venv existente
pip install -r requirements.txt --upgrade

# Método 2: Atualizar pacote específico
pip install Django==4.2.17  # nova versão

# Verificar integridade
pip check

# Salvar novas versões (se estiver em Git)
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Atualizar dependências"
git push
```

### 4.2 Adicionar novo pacote

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Instalar novo pacote
pip install novo-pacote==1.0.0

# Adicionar ao requirements.txt
echo "novo-pacote==1.0.0" >> requirements.txt

# Ou regenerar inteiro
pip freeze > requirements.txt

# Testar
python manage.py check

# Se OK, fazer commit
git add requirements.txt
git commit -m "Adicionar novo-pacote"
```

### 4.3 Verificar segurança das dependências

```bash
# Instalar checker de segurança
pip install safety

# Verificar
safety check

# Resultado esperado: nenhum vulnerability encontrado
```

---

## 5. MONITORAMENTO

### 5.1 Monitorar espaço em disco

```bash
# Usar em cron (todo dia às 8 da manhã)
# 0 8 * * * ~/check_disk_space.sh

# Arquivo ~/check_disk_space.sh:
#!/bin/bash
USAGE=$(df ~ | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt 80 ]; then
    echo "ALERTA: Disco em 80%+ de uso" > /tmp/disk_alert.txt
    # Notificar (se tiver email configurado)
fi
```

### 5.2 Monitorar erros em log

```bash
# Ver últimos 10 erros
tail -100 /var/log/seu_username.pythonanywhere.com.error.log | grep -i error | tail -10

# Salvar erros do último dia
grep "$(date +%d/%b/%Y)" /var/log/seu_username.pythonanywhere.com.error.log | grep -i error > ~/erros_hoje.log

cat ~/erros_hoje.log
```

### 5.3 Monitorar acessos

```bash
# Quantos acessos hoje?
grep "$(date +%d/%b/%Y)" /var/log/seu_username.pythonanywhere.com.access.log | wc -l

# Acessos por hora
grep "$(date +%d/%b/%Y)" /var/log/seu_username.pythonanywhere.com.access.log | awk '{print $4}' | sort | uniq -c

# Erros (status 4xx, 5xx)
grep "$(date +%d/%b/%Y)" /var/log/seu_username.pythonanywhere.com.access.log | grep -E " [45][0-9]{2} " | wc -l
```

---

## 6. OTIMIZAÇÃO DE PERFORMANCE

### 6.1 Verificar performance da query

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Ativar query logging (em settings.py, temporário):
cat >> .env << 'EOF'
QUERY_LOG=1
EOF

# Testar query lenta
python manage.py shell -c "
from django.db import connection
from django.test.utils import CaptureQueriesContext

# Sua query aqui
from animais.models import Animal
list(Animal.objects.all()[:100])

# Ver queries executadas
for query in connection.queries:
    print(query['sql'][:100] + '...')
"

# Desativar logging depois
```

### 6.2 Criar índices

Se query muito lenta, pode precisar índice:

```bash
# Em models.py, adicionar:
class Animal(models.Model):
    nome = models.CharField(max_length=100, db_index=True)
    
# Depois:
python manage.py makemigrations
python manage.py migrate
```

### 6.3 Implementar cache

```python
# Em views.py:
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache por 5 minutos
def dashboard(request):
    ...
```

---

## 7. SEGURANÇA EM PRODUÇÃO

### 7.1 Rotação de SECRET_KEY

**Recomendado:** A cada 6 meses

```bash
cd ~/TerneirasPro

# Gerar nova chave
NEW_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Atualizar .env
sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$NEW_KEY/" .env

# Verificar que foi atualizada
grep SECRET_KEY .env

# Recarregar aplicação
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

### 7.2 Verificar HTTPS

```bash
# Certificado deve ser emitido automaticamente pelo PythonAnywhere
# Verificar se ativo

curl -I https://seu-username.pythonanywhere.com | grep -i "https\|ssl"

# Resultado deve mostrar HTTPS/1.1
```

### 7.3 Audit de permissões

```bash
# Verificar quem pode acessar arquivos
ls -la ~/TerneirasPro/ | grep -E "^-rw"

# Ninguém de fora deveria conseguir ler .env
ls -la ~/TerneirasPro/.env
# Resultado: -rw------- (600) — apenas owner lê
```

### 7.4 Verificar headers de segurança

```bash
# Conferir se headers de segurança estão sendo enviados
curl -I https://seu-username.pythonanywhere.com | grep -E "Strict|X-Frame|X-Content"

# Esperado:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
```

Se não aparecer, adicionar em `settings.py`:

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {...}
X_FRAME_OPTIONS = 'DENY'
```

---

## 8. RECUPERAÇÃO DE DESASTRES

### 8.1 Banco corrompido

```bash
# Indicadores:
# - "database is locked" repetido
# - 500 errors ao abrir qualquer página
# - SELECT queries retornam erro

cd ~/TerneirasPro
source ~/venv/bin/activate

# Tentar reparo automático do SQLite
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
conn.execute('PRAGMA integrity_check;')
results = conn.fetchall()
for row in results:
    print(row)
"

# Se disser "ok", banco está OK
# Se tiver erro, restaurar de backup
```

### 8.2 Disco cheio

```bash
# Indicadores:
# - "No space left on device"
# - 502 Bad Gateway constante

# 1. Limpar logs antigos
rm -f /var/log/seu_username.pythonanywhere.com.error.log.*

# 2. Limpar cache de Python
find ~ -type d -name __pycache__ -exec rm -rf {} +
find ~ -type f -name "*.pyc" -delete

# 3. Verificar tamanho
du -sh ~/* | sort -hr

# 4. Se ainda cheio, fazer upgrade de conta PythonAnywhere
```

### 8.3 Venv corrompido

```bash
# Indicadores:
# - "command not found: python"
# - ImportError após pip install

# Solução:
rm -rf ~/venv
python3.12 -m venv ~/venv
source ~/venv/bin/activate
pip install -r ~/TerneirasPro/requirements.txt

# Recarregar
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

### 8.4 Arquivo de projeto deletado acidentalmente

```bash
# Se tem Git:
cd ~/TerneirasPro
git checkout HEAD -- nome_do_arquivo

# Se não tem Git:
# Restaurar do backup/repositório
cp ~/backup/arquivo_importante ~/TerneirasPro/
```

---

## 📋 CHECKLIST DE OPERAÇÕES

### Antes de partir de férias

```
[ ] Fazer backup do banco
[ ] Verificar que app está online
[ ] Verificar espaço em disco (>50% livre)
[ ] Verificar que não há erros recentes em log
[ ] Testar login funciona
[ ] Testar criar novo registro
[ ] Documentar qualquer problema conhecido
[ ] Deixar contato de emergência documentado
```

### Semana

```
[ ] Segunda-feira: Verificação matinal
[ ] Quarta-feira: Verificar espaço em disco
[ ] Sexta-feira: Fazer backup
[ ] Anytime: Monitorar erros em log
```

### Mês

```
[ ] Revisar error log completo do mês
[ ] Fazer análise de performance
[ ] Atualizar segurança (patches)
[ ] Documentar qualquer mudança
```

### Trimestre

```
[ ] Revisar tamanho de database
[ ] Considerar arquivar dados antigos
[ ] Atualizar dependências (pip)
[ ] Fazer teste completo de restore
```

### Semestre

```
[ ] Rotação de SECRET_KEY
[ ] Revisar logs de segurança
[ ] Atualizar documentação
[ ] Planar upgrades (se necessário)
```

---

## 🔗 REFERÊNCIA RÁPIDA

### Comandos de operação diária

```bash
# Status
curl https://seu-username.pythonanywhere.com -I

# Backup
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup.$(date +%Y%m%d)

# Ver erros
tail -50 /var/log/seu_username.pythonanywhere.com.error.log

# Recarregar
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

# Testar conexão
python -c "import sqlite3; sqlite3.connect('/home/seu_username/TerneirasPro/db.sqlite3')"

# Espaço
df -h ~
```

---

**FIM DO GUIDE DE OPERAÇÕES**

Próxima consulta: Se precisar fazer update, ver [Atualizar código](#3-atualizar-código)

