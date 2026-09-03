# 🚀 DEPLOY TERNEIRASPRO - GUIA RÁPIDO

## 📍 **INFORMAÇÃO IMPORTANTE:**
- **Nome da pasta:** TERNEIRAS (não TerneirasPro)
- **Caminho local:** /home/victor/Documentos/victor/Documentos/TERNEIRAS

---

# 🐍 **DEPLOY 1: PYTHONANYWHERE**

## **Passo 1: Preparar conta**
1. Criar conta: https://www.pythonanywhere.com
2. Escolher plano: Gratuito ou Hacker ($5/mês com HTTPS)

## **Passo 2: Upload do projeto**

### **Opção A: Via Git (RECOMENDADO)**
```bash
# No PythonAnywhere Bash Console:
cd ~
git clone SEU_REPOSITORIO_GIT TERNEIRAS
cd TERNEIRAS
```

### **Opção B: Via Upload Manual**
1. Compactar projeto localmente:
```bash
cd /home/victor/Documentos/victor/Documentos
tar -czf terneiras.tar.gz TERNEIRAS/
```

2. Upload via painel Files → Upload
3. Extrair no PythonAnywhere:
```bash
cd ~
tar -xzf terneiras.tar.gz
cd TERNEIRAS
```

## **Passo 3: Configurar .env**
```bash
cd ~/TERNEIRAS
cp .env.production.template .env
nano .env
```

**Preencher:**
```env
SECRET_KEY=SUA_CHAVE_SUPER_SEGURA_AQUI
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost,127.0.0.1
DATABASE_NAME=/home/seu-username/TERNEIRAS/db.sqlite3
TIME_ZONE=America/Sao_Paulo
CSRF_TRUSTED_ORIGINS=https://seu-username.pythonanywhere.com
```

**Gerar SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## **Passo 4: Executar deploy automático**
```bash
chmod +x deploy_pythonanywhere.sh
./deploy_pythonanywhere.sh
```

**O script vai:**
- ✅ Criar venv Python 3.12
- ✅ Instalar dependências
- ✅ Aplicar migrations
- ✅ Coletar static files
- ✅ Verificar configurações

## **Passo 5: Configurar Web App**

### **5.1 Criar Web App:**
- Web → Add a new web app
- Manual configuration
- Python 3.12

### **5.2 Configurar Virtualenv:**
```
/home/seu-username/venv
```

### **5.3 Configurar Source code:**
```
/home/seu-username/TERNEIRAS
```

### **5.4 Editar WSGI file:**
Arquivo: `/var/www/seu_username_pythonanywhere_com_wsgi.py`

Conteúdo:
```python
import os
import sys

# Adicionar projeto ao path
path = '/home/seu-username/TERNEIRAS'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### **5.5 Configurar Static Files:**
- URL: `/static/`
- Directory: `/home/seu-username/TERNEIRAS/staticfiles/`

### **5.6 Configurar Media Files:**
- URL: `/media/`
- Directory: `/home/seu-username/TERNEIRAS/media/`

## **Passo 6: Criar dados iniciais**
```bash
cd ~/TERNEIRAS
source ../venv/bin/activate
python manage.py createsuperuser
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

## **Passo 7: Reload e testar**
```bash
# No painel Web → Reload
# Ou:
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

**Testar:** https://seu-username.pythonanywhere.com

---

# 🍓 **DEPLOY 2: RASPBERRY PI**

## **Passo 1: Preparar Raspberry Pi**

### **1.1 Instalar Raspberry Pi OS**
- Raspberry Pi Imager
- OS: 64-bit recomendado
- Habilitar SSH nas configurações

### **1.2 Primeiro boot**
```bash
# Descobrir IP do Pi
nmap -sn 192.168.1.0/24

# Conectar via SSH
ssh pi@IP_DO_RASPBERRY
```

### **1.3 Atualizar sistema**
```bash
sudo apt update && sudo apt upgrade -y
sudo raspi-config
# Expand Filesystem + Locale pt_BR + Timezone America/Sao_Paulo
sudo reboot
```

## **Passo 2: Instalar dependências**
```bash
ssh pi@IP_DO_RASPBERRY

sudo apt install -y \
    git \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev
```

## **Passo 3: Clonar projeto**
```bash
cd ~
git clone SEU_REPOSITORIO_GIT TERNEIRAS
cd TERNEIRAS
```

**OU enviar via SCP:**
```bash
# No seu computador:
cd /home/victor/Documentos/victor/Documentos
tar -czf terneiras.tar.gz TERNEIRAS/
scp terneiras.tar.gz pi@IP_DO_RASPBERRY:~

# No Raspberry:
tar -xzf terneiras.tar.gz
cd TERNEIRAS
```

## **Passo 4: Configurar PostgreSQL**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql << EOF
CREATE DATABASE terneiraspro;
CREATE USER terneiraspro WITH PASSWORD 'senha_forte_aqui';
ALTER ROLE terneiraspro SET client_encoding TO 'utf8';
ALTER ROLE terneiraspro SET default_transaction_isolation TO 'read committed';
ALTER ROLE terneiraspro SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE terneiraspro TO terneiraspro;
\q
EOF
```

## **Passo 5: Configurar projeto**
```bash
cd ~/TERNEIRAS

# Criar venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configurar .env
nano .env
```

**Conteúdo do .env:**
```env
SECRET_KEY=SUA_CHAVE_SUPER_FORTE_AQUI
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,IP_DO_RASPBERRY,*.local,fazenda.local

DATABASE_URL=postgresql://terneiraspro:senha_forte_aqui@localhost/terneiraspro

TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

STATIC_ROOT=/home/pi/TERNEIRAS/staticfiles
MEDIA_ROOT=/home/pi/TERNEIRAS/media
```

```bash
# Aplicar configurações
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

## **Passo 6: Configurar Gunicorn**
```bash
nano ~/TERNEIRAS/gunicorn.conf.py
```

```python
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
timeout = 60
keepalive = 2
max_requests = 1000
preload_app = True
user = "pi"
pythonpath = "/home/pi/TERNEIRAS"
```

## **Passo 7: Configurar Supervisor**
```bash
sudo nano /etc/supervisor/conf.d/terneiraspro.conf
```

```ini
[program:terneiraspro]
command=/home/pi/TERNEIRAS/venv/bin/gunicorn --config /home/pi/TERNEIRAS/gunicorn.conf.py gestao_terneiras.wsgi:application
directory=/home/pi/TERNEIRAS
user=pi
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/pi/terneiras.log
environment=DJANGO_SETTINGS_MODULE="gestao_terneiras.settings"
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start terneiraspro
sudo supervisorctl status terneiraspro
```

## **Passo 8: Configurar Nginx**
```bash
sudo nano /etc/nginx/sites-available/terneiraspro
```

```nginx
server {
    listen 80;
    server_name IP_DO_RASPBERRY localhost fazenda.local;
    
    client_max_body_size 50M;
    
    location /static/ {
        alias /home/pi/TERNEIRAS/staticfiles/;
        expires 1y;
    }
    
    location /media/ {
        alias /home/pi/TERNEIRAS/media/;
        expires 1y;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/terneiraspro /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## **Passo 9: Configurar auto-start**
```bash
sudo systemctl enable postgresql
sudo systemctl enable nginx
sudo systemctl enable supervisor
```

## **Passo 10: Testar acesso**
```bash
# Verificar serviços
sudo systemctl status postgresql nginx supervisor
sudo supervisorctl status terneiraspro

# Testar acesso
curl -I http://localhost/
```

**URLs de acesso:**
- Local no Pi: http://localhost
- Rede local: http://IP_DO_RASPBERRY
- Nome amigável: http://fazenda.local (configurar no roteador)

---

## ✅ **CHECKLIST FINAL**

### **PythonAnywhere:**
- [ ] Conta criada e confirmada
- [ ] Projeto enviado para ~/TERNEIRAS
- [ ] .env configurado
- [ ] Script deploy_pythonanywhere.sh executado
- [ ] Web app configurado no painel
- [ ] WSGI file editado
- [ ] Static files configurados
- [ ] Superusuário criado
- [ ] Dados iniciais carregados
- [ ] Site funcionando em https://seu-username.pythonanywhere.com

### **Raspberry Pi:**
- [ ] Raspberry Pi OS instalado
- [ ] Sistema atualizado
- [ ] PostgreSQL instalado e configurado
- [ ] Projeto clonado em ~/TERNEIRAS
- [ ] .env configurado
- [ ] Migrations aplicadas
- [ ] Gunicorn configurado
- [ ] Supervisor configurado e rodando
- [ ] Nginx configurado e rodando
- [ ] Auto-start habilitado
- [ ] Site funcionando em http://IP_DO_RASPBERRY

---

## 🚨 **TROUBLESHOOTING RÁPIDO**

### **PythonAnywhere - Erro 502:**
```bash
# Ver logs
less /var/log/seu-username.pythonanywhere.com.error.log

# Verificar WSGI
cd ~/TERNEIRAS
source ../venv/bin/activate
python manage.py check
```

### **Raspberry Pi - Aplicação não responde:**
```bash
sudo supervisorctl restart terneiraspro
sudo systemctl reload nginx
tail -f /home/pi/terneiras.log
```

### **Estáticos não carregam:**
```bash
cd ~/TERNEIRAS
source venv/bin/activate
python manage.py collectstatic --noinput
```

---

## 📞 **PRÓXIMOS PASSOS**

Após deploy bem-sucedido:
1. Fazer primeiro acesso e configurar propriedade
2. Criar usuários da equipe
3. Configurar backup automático
4. Documentar credenciais de acesso
5. Treinar equipe com MANUAL_DO_USUARIO.md

**Sistema pronto para produção!** 🎉