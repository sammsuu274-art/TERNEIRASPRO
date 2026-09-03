# 🔧 TROUBLESHOOTING — Deployment TerneirasPro no PythonAnywhere

> Guia de diagnóstico e solução de problemas comuns

---

## 📍 MAPA DE TROUBLESHOOTING

Selecione o erro que você está recebendo:

| Erro | Código | Página de solução |
|---|---|---|
| 502 Bad Gateway | HTTP 502 | [Seção 1](#1-502-bad-gateway) |
| 500 Internal Server Error | HTTP 500 | [Seção 2](#2-500-internal-server-error) |
| 404 Not Found | HTTP 404 | [Seção 3](#3-404-not-found) |
| CSS/JS não carregam | 404 em `/static/` | [Seção 4](#4-cssjsimagens-não-carregam-404) |
| Login não funciona | Erro 500 ao logar | [Seção 5](#5-login-não-funciona) |
| Banco vazio | Sem dados após deploy | [Seção 6](#6-banco-de-dados-vazio) |
| Página em branco | Sem erro aparente | [Seção 7](#7-página-em-branco) |
| Arquivo não encontrado | `FileNotFoundError` | [Seção 8](#8-arquivo-não-encontrado) |
| Permissão negada | `PermissionError` | [Seção 9](#9-permissão-negada) |
| Erro de memória | `MemoryError` | [Seção 10](#10-erro-de-memória) |

---

## 1. 502 Bad Gateway

### ❌ Sintoma
```
502 Bad Gateway

The server returned an invalid or incomplete response.
```

### 🔍 Diagnóstico

Este erro geralmente significa que o servidor não consegue se comunicar com a aplicação Django. Pode ser:
- Arquivo WSGI não encontrado ou inválido
- Erro na inicialização do Django
- Variável de ambiente não configurada

### 🛠️ Solução

**Passo 1: Verificar arquivo WSGI**

```bash
# Conferir que arquivo existe
ls -la /var/www/seu_username_pythonanywhere_com_wsgi.py

# Verificar conteúdo básico
head -20 /var/www/seu_username_pythonanywhere_com_wsgi.py
```

Deve retornar:
```python
import sys
import os
project_home = '/home/seu_username/TerneirasPro'
```

**Se arquivo não existe:**
1. Ir para **Web → Web app → Code**
2. Clicar em link do arquivo WSGI
3. Copiar conteúdo correto (ver GUIA_IMPLEMENTACAO_PARA_EQUIPE.md seção 5)
4. Salvar

**Passo 2: Verificar error log**

```bash
tail -30 /var/log/seu_username.pythonanywhere.com.error.log
```

Procurar por mensagens como:
```
ModuleNotFoundError: No module named 'gestao_terneiras'
ImportError: cannot import name 'settings'
```

**Se aparecer:**
```
ModuleNotFoundError: No module named 'gestao_terneiras'
```

Significa que o path do projeto está incorreto no WSGI. Verificar:
```
project_home = '/home/seu_username/TerneirasPro'
```

Deve apontar para a raiz do projeto (onde está `manage.py`).

**Passo 3: Testar WSGI localmente**

```bash
source ~/venv/bin/activate
cd ~/TerneirasPro
python -c "
import sys
sys.path.insert(0, '/home/seu_username/TerneirasPro')
sys.path.insert(0, '/home/seu_username/venv/lib/python3.12/site-packages')
from gestao_terneiras.wsgi import application
print('WSGI OK')
"
```

Se erro, mensagem dirá o problema.

**Passo 4: Recarregar aplicação**

Depois de fazer correções:
```bash
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

Aguardar 30 segundos e testar.

---

## 2. 500 Internal Server Error

### ❌ Sintoma
```
500 Internal Server Error

The server encountered an unexpected condition.
```

### 🔍 Diagnóstico

Erro genérico que pode ter múltiplas causas:
- Erro em código Django
- Banco de dados não inicializado
- Arquivo .env não encontrado
- Import não resolvido
- Erro em middleware

### 🛠️ Solução

**Passo 1: Verificar error log**

```bash
tail -50 /var/log/seu_username.pythonanywhere.com.error.log
```

Ler toda a mensagem de erro. Procurar por:
- `FileNotFoundError` — arquivo não encontrado
- `ImportError` — módulo não encontrado
- `KeyError` — variável de ambiente faltando
- `DatabaseError` — erro no banco

**Passo 2: Se erro de variável de ambiente**

```
KeyError: 'SECRET_KEY'
```

Significa `.env` não existe. Criar:

```bash
cd ~/TerneirasPro
ls -la .env
```

Se não existe, criar:
```bash
cat > .env << 'EOF'
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost
EOF
```

Depois recarregar.

**Passo 3: Se erro de banco de dados**

```
django.db.utils.OperationalError: database is locked
```

Significa banco está corrompido. Solução:

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Backup do banco atual
cp db.sqlite3 db.sqlite3.corrupted

# Deletar banco corrompido
rm db.sqlite3

# Criar novo banco
python manage.py migrate

# Se tiver dados importantes, restaurar depois
```

**Passo 4: Se erro de module import**

```
ImportError: cannot import name 'PropriedadeMiddleware' from 'core.middleware'
```

Significa arquivo de middleware não existe ou está quebrado. Verificar:

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Testar import do middleware
python -c "from core.middleware import PropriedadeMiddleware; print('OK')"
```

Se erro, verificar arquivo:
```bash
cat core/middleware.py | head -20
```

Se vazio ou corrompido, restaurar do repositório.

**Passo 5: Se erro em view**

```
SyntaxError: invalid syntax in /home/seu_username/TerneirasPro/accounts/views.py line 42
```

Há erro de sintaxe em Python. Verificar arquivo:

```bash
python -m py_compile ~/TerneirasPro/accounts/views.py
```

Se erro, será mostrado o problema. Corrigir e testar novamente.

---

## 3. 404 Not Found

### ❌ Sintoma
```
404 Page Not Found

The requested URL / was not found on this server.
```

### 🔍 Diagnóstico

Pode ser:
- ROOT_URLCONF incorreto
- urls.py não carrega corretamente
- rota não definida

### 🛠️ Solução

**Passo 1: Verificar se Django inicia**

```bash
source ~/venv/bin/activate
cd ~/TerneirasPro
python manage.py runserver
```

Se rodar sem erro, Django está OK. Se erro, ver mensagem.

**Passo 2: Verificar urls.py**

```bash
cat ~/TerneirasPro/gestao_terneiras/urls.py | head -30
```

Deve ter:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    ...
]
```

**Passo 3: Se URL root não responde**

Rota `/` deve estar definida. Verificar:

```bash
python manage.py show_urls 2>/dev/null | grep "^/$"
```

Se não aparecer, adicionar em `core/urls.py`:

```python
path('', views.dashboard, name='dashboard'),
```

---

## 4. CSS/JS/Imagens não carregam (404)

### ❌ Sintoma
```
CSS não carrega - arquivo visto em 404 em navegador
console.log mostra: GET /static/css/... 404

Na página: tudo sem estilos, branco/cinza
```

### 🔍 Diagnóstico

Arquivos estáticos não foram coletados corretamente.

### 🛠️ Solução

**Passo 1: Verificar que pasta staticfiles existe**

```bash
ls -la ~/TerneirasPro/staticfiles/ | head -10
```

Deve ter arquivos como `admin/`, `bootstrap/`, etc. Se vazio:

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py collectstatic --noinput --clear
```

Aguardar mensagem:
```
42 static files copied to '/home/seu_username/TerneirasPro/staticfiles'
```

**Passo 2: Verificar mapeamento no PythonAnywhere**

1. **Web → Web app → Static files**
2. Conferir que tem entrada:
   ```
   URL: /static/
   Directory: /home/seu_username/TerneirasPro/staticfiles
   ```

Se não tiver, adicionar.

**Passo 3: Recarregar aplicação**

```bash
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

Aguardar 30 segundos.

**Passo 4: Testar acesso direto**

```bash
curl https://seu-username.pythonanywhere.com/static/ -I
```

Deve retornar:
```
HTTP/1.1 200 OK
```

Se 404, mapeamento está errado.

---

## 5. Login não funciona

### ❌ Sintoma
```
Depois de clicar em login, erro 500
Ou: Fica na tela de login infinitamente
Ou: Diz "Usuário ou senha incorretos" mesmo com admin/admin123
```

### 🔍 Diagnóstico

Problema pode ser em:
- Banco de dados (usuário não existe)
- SESSION_COOKIE_HTTPONLY (em ambiente de teste)
- Hash de senha corrompido

### 🛠️ Solução

**Passo 1: Verificar que banco existe e tem usuários**

```bash
source ~/venv/bin/activate
cd ~/TerneirasPro

# Listar usuários
python manage.py shell -c "
from accounts.models import Usuario
for user in Usuario.objects.all():
    print(f'{user.username} - is_active: {user.is_active}')
"
```

Se nenhum usuário, criar:

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@test.com  
# Password: admin123
# Password (again): admin123
```

**Passo 2: Se hash corrompido**

```bash
python manage.py shell -c "
from accounts.models import Usuario
user = Usuario.objects.get(username='admin')
user.set_password('admin123')
user.save()
print('Senha resetada')
"
```

**Passo 3: Testar login local**

```bash
python manage.py runserver
# Acessar: http://localhost:8000/accounts/login/
# Tentar login: admin / admin123
```

Se funciona localmente mas não em produção, pode ser configuração de cookie.

**Passo 4: Verificar session storage**

No `settings.py` deve ter:
```python
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
```

Se não tiver, adicionar.

---

## 6. Banco de dados vazio

### ❌ Sintoma
```
Sistema abre, mas sem dados
Dashboard mostra "sem dados"
Nenhum animal no banco
```

### 🔍 Diagnóstico

Pode ser:
- Banco novo foi criado mas não populado
- Banco antigo não foi copiado
- Dados não foram migrados

### 🛠️ Solução

**Opção 1: Se tinha banco local e quer copiar**

```bash
# No seu computador, copiar banco para PythonAnywhere
scp ~/db.sqlite3 seu_username@ssh.pythonanywhere.com:~/TerneirasPro/

# Ou via PythonAnywhere files UI:
# 1. Download local db.sqlite3
# 2. Delete versão antiga em PythonAnywhere
# 3. Upload nova versão
# 4. Recarregar app

# Depois verificar
curl https://seu-username.pythonanywhere.com | grep "Sem dados"
```

**Opção 2: Criar dados de teste**

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate

# Aplicar migrations
python manage.py migrate

# Seed de dados (se projeto tem)
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1

# Criar primeiro acesso
# Acessar /primeiro-acesso/ via navegador e preencher
```

---

## 7. Página em branco

### ❌ Sintoma
```
Navegador mostra página completamente em branco
Sem erro visível
Sem CSS ou JS carregando
Arquivo está sendo servido (200 OK)
```

### 🔍 Diagnóstico

Geralmente:
- Template não encontrado
- Erro em template (Jinja2)
- DEBUG=True mostraria erro, DEBUG=False esconde

### 🛠️ Solução

**Passo 1: Ativar DEBUG temporariamente (APENAS PARA DIAGNÓSTICO)**

```bash
cd ~/TerneirasPro
cat > .env << 'EOF'
SECRET_KEY=sua-chave-aqui
DEBUG=True
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost
EOF
```

Recarregar aplicação e acessar novamente. Agora erro será visível.

**Passo 2: Ler erro que aparece**

Se disser:
```
TemplateDoesNotExist: dashboard.html
```

Verificar que arquivo existe:

```bash
ls ~/TerneirasPro/templates/dashboard.html
```

Se não existe, restaurar do repositório.

**Passo 3: Voltar DEBUG=False**

Depois de corrigir:

```bash
cat > .env << 'EOF'
SECRET_KEY=sua-chave-aqui
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost
EOF
```

Recarregar.

---

## 8. Arquivo não encontrado

### ❌ Sintoma
```
FileNotFoundError: [Errno 2] No such file or directory: 'db.sqlite3'
```

### 🔍 Diagnóstico

Django procura arquivo em caminho relativo mas arquivo não existe lá.

### 🛠️ Solução

**Passo 1: Verificar caminho no settings.py**

```bash
grep "DATABASES" -A 5 ~/TerneirasPro/gestao_terneiras/settings.py
```

Deve mostrar:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Passo 2: BASE_DIR deve ser correto**

```bash
python -c "
import sys
sys.path.insert(0, '/home/seu_username/TerneirasPro')
from gestao_terneiras.settings import BASE_DIR
print(BASE_DIR)
"
```

Deve retornar:
```
/home/seu_username/TerneirasPro
```

**Passo 3: Se caminho errado, arquivo pode estar em lugar diferente**

```bash
find ~/ -name "db.sqlite3" 2>/dev/null
```

Se encontrar em lugar inesperado, mover para lugar correto:

```bash
mv ~/caminho-errado/db.sqlite3 ~/TerneirasPro/db.sqlite3
```

---

## 9. Permissão negada

### ❌ Sintoma
```
PermissionError: [Errno 13] Permission denied: '/home/seu_username/TerneirasPro/db.sqlite3'
```

### 🔍 Diagnóstico

Arquivo ou diretório não tem permissões corretas.

### 🛠️ Solução

**Passo 1: Verificar permissões atuais**

```bash
ls -la ~/TerneirasPro/db.sqlite3
```

Deve mostrar algo como:
```
-rw-r--r-- 1 seu_username seu_username 572000 Aug 15 10:00 db.sqlite3
```

**Passo 2: Se permissões incorretas, corrigir**

```bash
# Dar permissão de leitura/escrita
chmod 664 ~/TerneirasPro/db.sqlite3

# Dar permissão ao diretório também
chmod 755 ~/TerneirasPro

# Transferir propriedade se necessário
chown seu_username:seu_username ~/TerneirasPro/db.sqlite3
```

**Passo 3: Testar que funciona**

```bash
python -c "
import sqlite3
conn = sqlite3.connect('/home/seu_username/TerneirasPro/db.sqlite3')
print('OK')
"
```

---

## 10. Erro de memória

### ❌ Sintoma
```
MemoryError
Killed (processo finalizado abruptamente)
502 Bad Gateway após alguns minutos
```

### 🔍 Diagnóstico

Aplicação está usando mais memória que PythonAnywhere disponibiliza.

### 🛠️ Solução

**Passo 1: Verificar limite de memória**

No PythonAnywhere, plano FREE:
- 512 MB RAM por app
- SQLite (arquivo) é OK

**Passo 2: Verificar consumo atual**

No painel:
```
Web → Web app → CPU/Concurrency section
```

Se memória próxima de limite, problema pode ser:
- Query muito grande (buscar todos os animais sem paginar)
- Cache desativado
- Gráficos processando muitos dados

**Passo 3: Otimizar queries**

Em `views.py`, verificar:

```python
# ❌ Ruim - carrega TODOS os dados
animals = Animal.objects.all()

# ✅ Melhor - paginar
from django.core.paginator import Paginator
paginator = Paginator(animals, 20)
page = paginator.get_page(1)
```

**Passo 4: Fazer upgrade**

Se problema persistir, considerar plano pago (PythonAnywhere Hacker):
- 1 GB RAM
- CPU melhor
- Suporte prioritário

---

## 🔗 CHECKLIST DE TROUBLESHOOTING

Use quando nada acima funcionar:

```
[ ] Erro log lido completamente: tail -50 /var/log/seu_username.pythonanywhere.com.error.log
[ ] Arquivo WSGI verificado e correto
[ ] Path do projeto correto no WSGI (/home/seu_username/TerneirasPro)
[ ] Venv verificado: source ~/venv/bin/activate && python --version
[ ] .env existe: cat ~/TerneirasPro/.env
[ ] SECRET_KEY tem valor: grep SECRET_KEY .env
[ ] Migrations aplicadas: python manage.py showmigrations
[ ] Estáticos coletados: ls ~/TerneirasPro/staticfiles/ | wc -l (muitos arquivos?)
[ ] Mapeamento estático OK: Web → Static files
[ ] Reload feito: Web → Reload ou touch /var/www/...wsgi.py
[ ] Django healthcheck: python manage.py check --deploy
[ ] Pip check: pip check (No broken requirements)
[ ] DEBUG=False no .env (produção)
[ ] ALLOWED_HOSTS contém domínio correto
```

Se ainda não funcionar:

```bash
# Último recurso - informações de debug
source ~/venv/bin/activate
cd ~/TerneirasPro
python -c "
import django
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'check', '--deploy'])
"
```

---

## 📞 Quando procurar ajuda

Se nenhuma solução acima funcionar:

1. Reunir informações:
   ```bash
   python --version
   pip list | grep Django
   tail -100 /var/log/seu_username.pythonanywhere.com.error.log > error_log.txt
   ```

2. Consultar:
   - [PythonAnywhere Help](https://help.pythonanywhere.com)
   - [Django Docs](https://docs.djangoproject.com/en/4.2/)
   - [DOCUMENTACAO_AGENTE.md](./DOCUMENTACAO_AGENTE.md) seção "Problemas Conhecidos"

3. Se bug do projeto:
   - Abrir issue em repositório
   - Incluir erro_log.txt
   - Descrever exatamente o que fez

---

**FIM DO GUIDE DE TROUBLESHOOTING**

