# Deploy TerneirasPro no Raspberry Pi

## Requisitos Mínimos
- **Raspberry Pi 4** (4GB RAM recomendado)
- **MicroSD 32GB+** (Classe 10)
- **Raspberry Pi OS** (64-bit recomendado)
- **Conexão com Internet** (WiFi ou Ethernet)

## Passo 1: Preparar o Raspberry Pi

### 1.1 Instalar Raspberry Pi OS
```bash
# Baixar Raspberry Pi Imager
# Gravar imagem no SD card
# Inserir no Pi e ligar
```

### 1.2 Configurar SSH e VNC (opcional)
```bash
sudo raspi-config
# Interface Options > SSH > Enable
# Interface Options > VNC > Enable (para acesso remoto)
```

### 1.3 Atualizar sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

## Passo 2: Instalar Dependências

### 2.1 Python 3.12
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y
```

### 2.2 Dependências do sistema
```bash
sudo apt install -y \
  git \
  nginx \
  supervisor \
  postgresql \
  postgresql-contrib \
  python3-pip \
  build-essential \
  libpq-dev \
  libjpeg-dev \
  zlib1g-dev
```

## Passo 3: Configurar PostgreSQL

### 3.1 Criar banco e usuário
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE terneiraspro;
CREATE USER terneiraspro WITH PASSWORD 'senha_segura_aqui';
ALTER ROLE terneiraspro SET client_encoding TO 'utf8';
ALTER ROLE terneiraspro SET default_transaction_isolation TO 'read committed';
ALTER ROLE terneiraspro SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE terneiraspro TO terneiraspro;
\q
```

### 3.2 Configurar PostgreSQL para aceitar conexões
```bash
sudo nano /etc/postgresql/13/main/pg_hba.conf
# Adicionar linha:
# local   terneiraspro    terneiraspro                    md5

sudo systemctl restart postgresql
```

## Passo 4: Clonar e Configurar Projeto

### 4.1 Criar usuário para aplicação
```bash
sudo adduser terneiraspro
sudo usermod -aG sudo terneiraspro
su - terneiraspro
```

### 4.2 Clonar repositório
```bash
cd /home/terneiraspro
git clone https://github.com/SEU_USUARIO/TERNEIRASPRO.git
cd TERNEIRASPRO
```

### 4.3 Criar ambiente virtual
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Configurar variáveis de ambiente
```bash
cp .env.production.template .env.raspberry
```

### 4.5 Editar .env.raspberry
```bash
nano .env.raspberry
```

```env
# .env.raspberry
SECRET_KEY=SUA_CHAVE_SECRETA_MUITO_FORTE_AQUI
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,IP_DO_RASPBERRY,*.local

# PostgreSQL
DATABASE_URL=postgresql://terneiraspro:senha_segura_aqui@localhost/terneiraspro

# Arquivos estáticos
STATIC_ROOT=/home/terneiraspro/TERNEIRASPRO/staticfiles
MEDIA_ROOT=/home/terneiraspro/TERNEIRASPRO/media

# Configurações de produção
USE_TZ=True
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br
```

### 4.6 Aplicar migrações e configurar
```bash
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=gestao_terneiras.settings
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

## Passo 5: Configurar Gunicorn

### 5.1 Instalar Gunicorn
```bash
pip install gunicorn
```

### 5.2 Testar Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 gestao_terneiras.wsgi
```

### 5.3 Criar arquivo de configuração
```bash
nano /home/terneiraspro/TERNEIRASPRO/gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

## Passo 6: Configurar Supervisor

### 6.1 Criar arquivo de configuração
```bash
sudo nano /etc/supervisor/conf.d/terneiraspro.conf
```

```ini
[program:terneiraspro]
command=/home/terneiraspro/TERNEIRASPRO/venv/bin/gunicorn --config /home/terneiraspro/TERNEIRASPRO/gunicorn.conf.py gestao_terneiras.wsgi
directory=/home/terneiraspro/TERNEIRASPRO
user=terneiraspro
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/terneiraspro.log
environment=DJANGO_SETTINGS_MODULE="gestao_terneiras.settings"
```

### 6.2 Ativar e iniciar
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start terneiraspro
sudo supervisorctl status terneiraspro
```

## Passo 7: Configurar Nginx

### 7.1 Criar configuração do site
```bash
sudo nano /etc/nginx/sites-available/terneiraspro
```

```nginx
server {
    listen 80;
    server_name IP_DO_RASPBERRY localhost;
    
    client_max_body_size 50M;
    
    location /static/ {
        alias /home/terneiraspro/TERNEIRASPRO/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/terneiraspro/TERNEIRASPRO/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 7.2 Ativar site
```bash
sudo ln -s /etc/nginx/sites-available/terneiraspro /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove site padrão
sudo nginx -t  # Testar configuração
sudo systemctl reload nginx
```

## Passo 8: Configurar Auto-início

### 8.1 Habilitar serviços no boot
```bash
sudo systemctl enable nginx
sudo systemctl enable supervisor
sudo systemctl enable postgresql
```

### 8.2 Criar script de atualização
```bash
nano /home/terneiraspro/update_terneiraspro.sh
```

```bash
#!/bin/bash
cd /home/terneiraspro/TERNEIRASPRO
source venv/bin/activate

echo "Fazendo backup do banco..."
sudo -u postgres pg_dump terneiraspro > backup_$(date +%Y%m%d_%H%M%S).sql

echo "Baixando atualizações..."
git pull origin main

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Aplicando migrações..."
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Reiniciando aplicação..."
sudo supervisorctl restart terneiraspro

echo "Atualização concluída!"
```

```bash
chmod +x /home/terneiraspro/update_terneiraspro.sh
```

## Passo 9: Teste Final

### 9.1 Verificar serviços
```bash
sudo systemctl status nginx
sudo systemctl status supervisor
sudo systemctl status postgresql
sudo supervisorctl status terneiraspro
```

### 9.2 Acessar sistema
- **Local**: http://localhost
- **Rede**: http://IP_DO_RASPBERRY
- **Login**: admin / sua_senha_criada

## Passo 10: Configurações Opcionais

### 10.1 SSL/HTTPS com Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu_dominio.com
```

### 10.2 Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 10.3 Backup automático
```bash
crontab -e
# Adicionar linha para backup diário às 2h:
# 0 2 * * * /usr/bin/sudo -u postgres pg_dump terneiraspro > /home/terneiraspro/backup_$(date +\%Y\%m\%d).sql
```

## Monitoramento

### Logs importantes
```bash
# Logs da aplicação
sudo tail -f /var/log/supervisor/terneiraspro.log

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Status dos serviços
sudo supervisorctl status
sudo systemctl status nginx postgresql
```

## Troubleshooting

### Problemas comuns
1. **Erro 502**: Verificar se Gunicorn está rodando
2. **Arquivos estáticos não carregam**: Verificar STATIC_ROOT e collectstatic
3. **Erro de banco**: Verificar configurações PostgreSQL
4. **Permissões**: Verificar ownership dos arquivos

### Comandos úteis
```bash
# Reiniciar tudo
sudo supervisorctl restart terneiraspro
sudo systemctl reload nginx

# Ver logs
sudo journalctl -u supervisor
sudo journalctl -u nginx

# Testar conexão com banco
sudo -u postgres psql terneiraspro
```