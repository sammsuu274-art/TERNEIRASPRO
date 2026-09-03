# Deploy TerneirasPro no Raspberry Pi

## 🍓 SERVIDOR LOCAL DA FAZENDA

### Por que Raspberry Pi?
- **Servidor local** - funciona sem internet
- **Baixo custo** - investimento único ~R$ 800
- **Baixo consumo** - energia mínima  
- **Acesso via rede local** - todos os dispositivos da fazenda
- **Backup automático** - dados seguros na propriedade

---

## 🛠️ **REQUISITOS MÍNIMOS**

### Hardware:
- **Raspberry Pi 4** (4GB RAM recomendado, mín. 2GB)
- **MicroSD Card 64GB+** (Classe 10 ou superior)
- **Fonte oficial** 5V 3A
- **Case com ventilação** (resfriamento)
- **Cabo de rede** (Ethernet recomendado para estabilidade)

### Software:
- **Raspberry Pi OS** 64-bit (Debian 12 based)
- **Python 3.11+** (incluído no OS)
- **PostgreSQL** 15+ (banco de produção)

---

## 📦 **PREPARAÇÃO DO RASPBERRY PI**

### **ETAPA 1: Instalar Sistema Operacional**

1. **Baixar Raspberry Pi Imager:**
   - Site oficial: https://www.raspberrypi.com/software/
   - Instalar no seu computador

2. **Gravar imagem:**
   - Escolher: "Raspberry Pi OS (64-bit)" 
   - Configurações avançadas (⚙️):
     - ✅ Enable SSH
     - ✅ Username: `pi`, Password: sua_senha
     - ✅ Configure WiFi (se necessário)
     - ✅ Set locale: Brazil, pt_BR, America/Sao_Paulo
   - Gravar no SD card

3. **Primeiro boot:**
   - Inserir SD card no Pi
   - Conectar cabo de rede (recomendado)
   - Ligar
   - Aguardar ~3 minutos

4. **Conectar via SSH:**
   ```bash
   # Descobrir IP do Pi:
   nmap -sn 192.168.1.0/24  # ou usar roteador
   
   # Conectar:
   ssh pi@IP_DO_PI
   ```

---

### **ETAPA 2: Configurar Sistema**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Configurações do sistema
sudo raspi-config
# Opções importantes:
# - Interface Options > SSH: Enable
# - Interface Options > VNC: Enable (acesso remoto GUI)
# - Advanced > Expand Filesystem
# - Localisation > Change Locale: pt_BR.UTF-8
# - Localisation > Change Timezone: America/Sao_Paulo

# Reiniciar
sudo reboot
```

---

### **ETAPA 3: Instalar Dependências**

```bash
# Conectar novamente após reboot
ssh pi@IP_DO_PI

# Instalar pacotes essenciais
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
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    htop \
    curl \
    wget \
    unzip
```

---

### **ETAPA 4: Configurar PostgreSQL**

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql << EOF
CREATE DATABASE terneiraspro;
CREATE USER terneiraspro WITH PASSWORD 'senha_muito_forte_aqui';
ALTER ROLE terneiraspro SET client_encoding TO 'utf8';
ALTER ROLE terneiraspro SET default_transaction_isolation TO 'read committed';
ALTER ROLE terneiraspro SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE terneiraspro TO terneiraspro;
\q
EOF

# Configurar autenticação
sudo sed -i "s/#local_replication/local   terneiraspro    terneiraspro                    md5\nlocal_replication/" /etc/postgresql/15/main/pg_hba.conf

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Testar conexão
psql -h localhost -U terneiraspro -d terneiraspro -c "SELECT version();"
```

---

### **ETAPA 5: Preparar Aplicação**

```bash
# Criar usuário para aplicação
sudo adduser --system --group --home /home/terneiraspro terneiraspro
sudo usermod -a -G www-data terneiraspro

# Trocar para usuário da aplicação
sudo su - terneiraspro

# Clonar projeto
git clone https://github.com/SEU_USUARIO/TERNEIRASPRO.git
cd TERNEIRASPRO

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependências
pip install -r requirements.txt

# Instalar Gunicorn
pip install gunicorn psycopg2-binary
```

---

### **ETAPA 6: Configurar Ambiente de Produção**

```bash
# Ainda como usuário terneiraspro
cd /home/terneiraspro/TERNEIRASPRO

# Criar arquivo .env
nano .env
```

Conteúdo do `.env` para Raspberry Pi:
```env
# Configurações de Produção Raspberry Pi
SECRET_KEY=SUA_CHAVE_SUPER_SECRETA_MINIMO_50_CARACTERES_AQUI
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,IP_DO_RASPBERRY,*.local,fazenda.local

# PostgreSQL
DATABASE_URL=postgresql://terneiraspro:senha_muito_forte_aqui@localhost/terneiraspro

# Configurações regionais
USE_TZ=True
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# Arquivos
STATIC_ROOT=/home/terneiraspro/TERNEIRASPRO/staticfiles
MEDIA_ROOT=/home/terneiraspro/TERNEIRASPRO/media

# Logs
LOGGING_LEVEL=INFO
LOG_FILE=/home/terneiraspro/logs/django.log

# Email (opcional - para alertas)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

```bash
# Aplicar configurações
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1

# Criar diretório de logs
mkdir -p /home/terneiraspro/logs

# Testar aplicação
python manage.py runserver 0.0.0.0:8000
# Testar acesso: http://IP_DO_PI:8000
# CTRL+C para parar
```

---

### **ETAPA 7: Configurar Gunicorn**

```bash
# Como usuário terneiraspro
cd /home/terneiraspro/TERNEIRASPRO

# Criar configuração do Gunicorn
nano gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 2  # CPU cores do Pi
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
user = "terneiraspro"
group = "terneiraspro"
tmp_upload_dir = None
pythonpath = "/home/terneiraspro/TERNEIRASPRO"
```

```bash
# Testar Gunicorn
source venv/bin/activate
gunicorn --config gunicorn.conf.py gestao_terneiras.wsgi:application
# Testar acesso: http://IP_DO_PI:8000
# CTRL+C para parar
```

---

### **ETAPA 8: Configurar Supervisor**

```bash
# Voltar para usuário pi
exit

# Criar configuração do Supervisor
sudo nano /etc/supervisor/conf.d/terneiraspro.conf
```

```ini
[program:terneiraspro]
command=/home/terneiraspro/TERNEIRASPRO/venv/bin/gunicorn --config /home/terneiraspro/TERNEIRASPRO/gunicorn.conf.py gestao_terneiras.wsgi:application
directory=/home/terneiraspro/TERNEIRASPRO
user=terneiraspro
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/terneiraspro/logs/gunicorn.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="/home/terneiraspro/TERNEIRASPRO/venv/bin",DJANGO_SETTINGS_MODULE="gestao_terneiras.settings"
```

```bash
# Atualizar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start terneiraspro

# Verificar status
sudo supervisorctl status terneiraspro
```

---

### **ETAPA 9: Configurar Nginx**

```bash
# Remover configuração padrão
sudo rm /etc/nginx/sites-enabled/default

# Criar configuração do TerneirasPro
sudo nano /etc/nginx/sites-available/terneiraspro
```

```nginx
server {
    listen 80;
    server_name IP_DO_RASPBERRY localhost fazenda.local;
    
    # Tamanho máximo de upload
    client_max_body_size 50M;
    
    # Logs
    access_log /var/log/nginx/terneiraspro_access.log;
    error_log /var/log/nginx/terneiraspro_error.log;
    
    # Arquivos estáticos
    location /static/ {
        alias /home/terneiraspro/TERNEIRASPRO/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        gzip_static on;
    }
    
    # Arquivos de mídia
    location /media/ {
        alias /home/terneiraspro/TERNEIRASPRO/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Aplicação Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
    }
    
    # Favicon
    location /favicon.ico {
        alias /home/terneiraspro/TERNEIRASPRO/staticfiles/img/favicon.ico;
        expires 1y;
    }
    
    # Robots.txt
    location /robots.txt {
        alias /home/terneiraspro/TERNEIRASPRO/staticfiles/robots.txt;
        expires 1y;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/terneiraspro /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### **ETAPA 10: Configurar Inicialização Automática**

```bash
# Habilitar serviços no boot
sudo systemctl enable postgresql
sudo systemctl enable nginx
sudo systemctl enable supervisor

# Criar script de monitoramento
sudo nano /home/terneiraspro/monitor_system.sh
```

```bash
#!/bin/bash
# Monitor do sistema TerneirasPro

LOG_FILE="/home/terneiraspro/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Verificando serviços..." >> $LOG_FILE

# Verificar PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo "[$DATE] PostgreSQL parou! Reiniciando..." >> $LOG_FILE
    sudo systemctl restart postgresql
fi

# Verificar Nginx
if ! systemctl is-active --quiet nginx; then
    echo "[$DATE] Nginx parou! Reiniciando..." >> $LOG_FILE
    sudo systemctl restart nginx
fi

# Verificar Supervisor
if ! systemctl is-active --quiet supervisor; then
    echo "[$DATE] Supervisor parou! Reiniciando..." >> $LOG_FILE
    sudo systemctl restart supervisor
fi

# Verificar aplicação
if ! sudo supervisorctl status terneiraspro | grep -q RUNNING; then
    echo "[$DATE] TerneirasPro parou! Reiniciando..." >> $LOG_FILE
    sudo supervisorctl restart terneiraspro
fi

# Verificar espaço em disco
DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "[$DATE] ALERTA: Disco com $DISK_USAGE% de uso!" >> $LOG_FILE
fi
```

```bash
sudo chmod +x /home/terneiraspro/monitor_system.sh

# Configurar cron para monitoramento a cada 5 minutos
sudo crontab -e
# Adicionar linha:
# */5 * * * * /home/terneiraspro/monitor_system.sh
```

---

### **ETAPA 11: Script de Atualização**

```bash
# Criar script de atualização
sudo nano /home/terneiraspro/update_terneiraspro.sh
```

```bash
#!/bin/bash
# Script de atualização do TerneirasPro

set -e

LOG_FILE="/home/terneiraspro/logs/update.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Iniciando atualização..." | tee -a $LOG_FILE

# Mudar para usuário terneiraspro
cd /home/terneiraspro/TERNEIRASPRO

# Backup do banco
echo "[$DATE] Fazendo backup do banco..." | tee -a $LOG_FILE
sudo -u postgres pg_dump terneiraspro > /home/terneiraspro/backups/db_$(date +%Y%m%d_%H%M%S).sql

# Parar aplicação
echo "[$DATE] Parando aplicação..." | tee -a $LOG_FILE
sudo supervisorctl stop terneiraspro

# Baixar atualizações
echo "[$DATE] Baixando código atualizado..." | tee -a $LOG_FILE
sudo -u terneiraspro git pull origin main

# Ativar ambiente virtual
echo "[$DATE] Ativando ambiente virtual..." | tee -a $LOG_FILE
sudo -u terneiraspro bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Aplicar migrações
echo "[$DATE] Aplicando migrações..." | tee -a $LOG_FILE
sudo -u terneiraspro bash -c "source venv/bin/activate && python manage.py migrate"

# Coletar estáticos
echo "[$DATE] Coletando arquivos estáticos..." | tee -a $LOG_FILE
sudo -u terneiraspro bash -c "source venv/bin/activate && python manage.py collectstatic --noinput"

# Reiniciar aplicação
echo "[$DATE] Reiniciando aplicação..." | tee -a $LOG_FILE
sudo supervisorctl start terneiraspro

# Verificar se subiu
sleep 5
if sudo supervisorctl status terneiraspro | grep -q RUNNING; then
    echo "[$DATE] Atualização concluída com sucesso!" | tee -a $LOG_FILE
else
    echo "[$DATE] ERRO: Aplicação não subiu após atualização!" | tee -a $LOG_FILE
    exit 1
fi
```

```bash
sudo chmod +x /home/terneiraspro/update_terneiraspro.sh

# Criar diretório de backups
sudo -u terneiraspro mkdir -p /home/terneiraspro/backups
```

---

### **ETAPA 12: Configurar Acesso via Nome**

```bash
# Configurar hostname local
sudo nano /etc/hosts
# Adicionar linha:
# IP_DO_PI    fazenda.local terneiraspro.local

# No roteador (se possível), adicionar entrada DNS:
# fazenda.local -> IP_DO_PI
```

Nos computadores da fazenda, adicionar ao arquivo hosts:
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **Linux/Mac**: `/etc/hosts`

Linha a adicionar:
```
IP_DO_RASPBERRY    fazenda.local
```

---

## 🔧 **TESTE FINAL E ACESSO**

```bash
# Verificar todos os serviços
sudo systemctl status postgresql nginx supervisor
sudo supervisorctl status terneiraspro

# Testar acesso
curl -I http://localhost/
curl -I http://IP_DO_PI/
```

### **URLs de acesso:**
- **Local no Pi**: http://localhost
- **Rede local**: http://IP_DO_PI  
- **Nome amigável**: http://fazenda.local
- **Admin Django**: http://fazenda.local/admin

### **Credenciais:**
- **Login**: superusuário criado
- **SSH**: `pi@IP_DO_PI`
- **PostgreSQL**: `terneiraspro` / sua_senha

---

## 📊 **MONITORAMENTO E MANUTENÇÃO**

### **Comandos úteis:**
```bash
# Status geral
sudo systemctl status postgresql nginx supervisor
sudo supervisorctl status terneiraspro

# Logs da aplicação
sudo tail -f /home/terneiraspro/logs/gunicorn.log
sudo tail -f /var/log/nginx/terneiraspro_error.log

# Uso de recursos
htop
df -h
free -h

# Backup manual
sudo -u postgres pg_dump terneiraspro > backup_$(date +%Y%m%d).sql

# Reiniciar aplicação
sudo supervisorctl restart terneiraspro

# Atualizar sistema
sudo /home/terneiraspro/update_terneiraspro.sh
```

### **Backup automático diário:**
```bash
sudo crontab -e
# Adicionar:
# 0 3 * * * sudo -u postgres pg_dump terneiraspro > /home/terneiraspro/backups/daily_$(date +\%Y\%m\%d).sql
# 0 4 * * * find /home/terneiraspro/backups -name "daily_*.sql" -mtime +7 -delete
```

---

## 🚨 **TROUBLESHOOTING**

### **Aplicação não responde:**
```bash
sudo supervisorctl restart terneiraspro
sudo systemctl reload nginx
```

### **Erro 502 Bad Gateway:**
- Verificar se Gunicorn está rodando: `sudo supervisorctl status`
- Verificar logs: `sudo tail -f /home/terneiraspro/logs/gunicorn.log`

### **Sem acesso externo:**
- Verificar IP: `hostname -I`
- Testar ping: `ping IP_DO_PI`
- Verificar firewall: `sudo ufw status`

### **Banco de dados:**
- Testar conexão: `sudo -u terneiraspro psql -h localhost -U terneiraspro terneiraspro`
- Verificar logs: `sudo journalctl -u postgresql`

### **Performance:**
- Monitor recursos: `htop`, `iotop`
- Otimizar PostgreSQL se necessário
- Considerar SSD se usando SD card lento

---

## 💰 **CUSTOS ESTIMADOS**

| Item | Custo (R$) |
|---|---:|
| Raspberry Pi 4 (4GB) | R$ 450 |
| SD Card 64GB Classe 10 | R$ 80 |
| Fonte oficial | R$ 70 |
| Case com ventilação | R$ 50 |
| Cabo de rede | R$ 20 |
| **TOTAL** | **R$ 670** |

**+ Custo de energia**: ~R$ 5/mês (consumo muito baixo)

---

## ✅ **CHECKLIST FINAL**

- [ ] Raspberry Pi 4 configurado com OS atualizado
- [ ] PostgreSQL instalado e banco criado
- [ ] Projeto clonado e ambiente virtual configurado
- [ ] Dependências instaladas
- [ ] .env configurado para produção
- [ ] Migrations aplicadas e dados iniciais carregados
- [ ] Gunicorn configurado e testado
- [ ] Supervisor configurado e aplicação rodando
- [ ] Nginx configurado e proxy funcionando
- [ ] Serviços habilitados para auto-start
- [ ] Scripts de monitoramento e atualização criados
- [ ] Backup automático configurado
- [ ] Acesso via nome (fazenda.local) funcionando
- [ ] Teste completo de funcionamento

**Seu servidor local está pronto!** 🎉

---

## 📱 **VANTAGENS DO RASPBERRY PI**

✅ **Independência total** - funciona sem internet  
✅ **Dados na fazenda** - controle total  
✅ **Acesso rápido** - rede local  
✅ **Baixo custo** - investimento único  
✅ **Baixo consumo** - economia de energia  
✅ **Portabilidade** - pode mover entre locais  
✅ **Backup local** - dados seguros  
✅ **Customização total** - adaptado para a fazenda  

**Perfeito para fazendas que querem autonomia e controle total dos dados!** 🍓🚜

---

**Desenvolvedor:** Victor Rodrigues - Passo Fundo/RS  
**Suporte:** Consulte MANUAL_DO_USUARIO.md para operação do sistema