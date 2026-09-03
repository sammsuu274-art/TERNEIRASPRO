# Deploy TerneirasPro no PythonAnywhere

## 📋 GUIA COMPLETO USANDO SCRIPT AUTOMÁTICO

### Pré-requisitos
- **Conta no PythonAnywhere** (gratuita ou paga)
- **Projeto TerneirasPro** completo
- **Script automático** `deploy_pythonanywhere.sh` (já incluído no projeto)

---

## 🚀 **PASSO A PASSO DETALHADO**

### **ETAPA 1: Preparar Conta PythonAnywhere**

1. **Criar conta:**
   - Acesse: https://www.pythonanywhere.com
   - Criar conta gratuita ou paga
   - Confirmar email

2. **Escolher plano:**
   - **Gratuita**: Limite de CPU, sem HTTPS customizado
   - **Hacker ($5/mês)**: Sem limites, HTTPS, domínio próprio
   - **Web Developer ($12/mês)**: Mais recursos, MySQL

---

### **ETAPA 2: Enviar Projeto para PythonAnywhere**

#### **Opção A: Via Git (RECOMENDADO)**
```bash
# No PythonAnywhere Bash console:
cd ~
git clone https://github.com/SEU_USUARIO/TERNEIRASPRO.git TerneirasPro
```

#### **Opção B: Via Upload de Arquivo**
1. Compactar projeto: `tar -czf terneiraspro.tar.gz TERNEIRAS/`
2. Upload via Files → Upload a file
3. Extrair: `tar -xzf terneiraspro.tar.gz`
4. Renomear: `mv TERNEIRAS TerneirasPro`

---

### **ETAPA 3: Configurar Ambiente**

1. **Abrir Bash Console** no PythonAnywhere

2. **Dar permissão ao script:**
```bash
cd ~/TerneirasPro
chmod +x deploy_pythonanywhere.sh
```

3. **Criar arquivo .env:**
```bash
nano .env
```

Conteúdo do `.env`:
```env
# Configurações de Produção PythonAnywhere
SECRET_KEY=SUA_CHAVE_SUPER_SECRETA_E_LONGA_AQUI_MINIMO_50_CHARS
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,127.0.0.1,localhost

# Banco de dados (SQLite para conta gratuita)
DATABASE_URL=sqlite:///home/seu-username/TerneirasPro/db.sqlite3

# Configurações regionais
USE_TZ=True
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# Arquivos estáticos
STATIC_ROOT=/home/seu-username/TerneirasPro/staticfiles
MEDIA_ROOT=/home/seu-username/TerneirasPro/media

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**⚠️ IMPORTANTE:**
- Substitua `seu-username` pelo seu username do PythonAnywhere
- Gere SECRET_KEY segura: https://djecrety.ir/
- Para contas pagas, pode usar PostgreSQL/MySQL

---

### **ETAPA 4: Executar Deploy Automático**

```bash
./deploy_pythonanywhere.sh
```

O script vai:
- ✅ Verificar ambiente
- ✅ Criar ambiente virtual Python 3.12
- ✅ Instalar dependências
- ✅ Aplicar migrations
- ✅ Coletar arquivos estáticos
- ✅ Verificar configurações

---

### **ETAPA 5: Configurar Web App**

1. **Ir para Web → Web app → Create a web app**

2. **Configurar Python:**
   - Framework: Django
   - Python version: 3.12
   - Django version: Skip (já instalado)

3. **Configurar Virtualenv:**
   ```
   /home/seu-username/venv
   ```

4. **Configurar Source code:**
   ```
   /home/seu-username/TerneirasPro
   ```

5. **Configurar WSGI file:**
   - Editar: `/var/www/seu_username_pythonanywhere_com_wsgi.py`
   
   Conteúdo:
   ```python
   import os
   import sys
   
   # Adicionar projeto ao path
   path = '/home/seu-username/TerneirasPro'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   # Configurar Django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

6. **Configurar Static Files:**
   - URL: `/static/`
   - Directory: `/home/seu-username/TerneirasPro/staticfiles/`

7. **Configurar Media Files (opcional):**
   - URL: `/media/`
   - Directory: `/home/seu-username/TerneirasPro/media/`

---

### **ETAPA 6: Configurar Banco de Dados**

#### **Para conta GRATUITA (SQLite):**
```bash
cd ~/TerneirasPro
source ../venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

#### **Para conta PAGA (MySQL):**
1. Criar banco no painel Databases
2. Atualizar .env:
```env
DATABASE_URL=mysql://usuario:senha@seu-username.mysql.pythonanywhere-services.com/banco$default
```
3. Executar migrations como acima

---

### **ETAPA 7: Reload e Teste**

1. **Recarregar aplicação:**
   - Web → Web app → Reload
   - Ou: `touch /var/www/seu_username_pythonanywhere_com_wsgi.py`

2. **Testar acesso:**
   - Abrir: `https://seu-username.pythonanywhere.com`
   - Fazer login com superusuário criado
   - Verificar se dashboard carrega

3. **Primeiro acesso:**
   - Sistema vai para configuração de propriedade
   - Criar primeira fazenda
   - Pronto para usar!

---

### **ETAPA 8: Configurações Finais**

#### **HTTPS e Domínio Personalizado (contas pagas):**
1. Web → Web app → Security
2. Enable HTTPS
3. Configure custom domain se tiver

#### **Backup Automático:**
```bash
# Criar script de backup
nano ~/backup_terneiraspro.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cd ~/TerneirasPro
cp db.sqlite3 ~/backups/db_$DATE.sqlite3
tar -czf ~/backups/media_$DATE.tar.gz media/
```

```bash
chmod +x ~/backup_terneiraspro.sh
# Executar manualmente ou configurar cron (contas pagas)
```

---

## 🔧 **ATUALIZAÇÕES FUTURAS**

### Script de Atualização:
```bash
nano ~/update_terneiraspro.sh
```

```bash
#!/bin/bash
cd ~/TerneirasPro

echo "Fazendo backup..."
cp db.sqlite3 ~/db_backup_$(date +%Y%m%d).sqlite3

echo "Baixando atualizações..."
git pull origin main

echo "Ativando venv..."
source ../venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Aplicando migrations..."
python manage.py migrate

echo "Coletando estáticos..."
python manage.py collectstatic --noinput

echo "Recarregando app..."
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

echo "Atualização concluída!"
```

```bash
chmod +x ~/update_terneiraspro.sh
```

---

## 📊 **MONITORAMENTO**

### **Logs importantes:**
```bash
# Error logs
less /var/log/seu-username.pythonanywhere.com.error.log

# Server logs  
less /var/log/seu-username.pythonanywhere.com.server.log

# Django logs (se configurado)
tail -f ~/TerneirasPro/logs/django.log
```

### **Comandos úteis:**
```bash
# Status do ambiente
source ~/venv/bin/activate
cd ~/TerneirasPro
python manage.py check

# Ver usuários
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all())"

# Limpar sessões antigas
python manage.py clearsessions
```

---

## 🚨 **TROUBLESHOOTING**

### **Problemas comuns:**

#### **Erro 502 - Bad Gateway:**
- Verificar WSGI file
- Verificar permissions
- Verificar .env

#### **Estáticos não carregam:**
- Verificar STATIC_ROOT no .env
- Executar collectstatic
- Verificar configuração no painel Web

#### **Banco de dados:**
- Verificar permissions do db.sqlite3
- Executar migrations
- Verificar .env

#### **Import errors:**
- Verificar se venv está correto no painel Web
- Verificar requirements.txt
- Verificar PYTHONPATH no WSGI

### **Comandos de diagnóstico:**
```bash
# Testar WSGI
cd ~/TerneirasPro
python manage.py shell -c "from django.core.wsgi import get_wsgi_application; app = get_wsgi_application(); print('WSGI OK')"

# Testar banco
python manage.py migrate --check

# Testar estáticos
python manage.py findstatic admin/css/base.css
```

---

## ✅ **CHECKLIST FINAL**

- [ ] Conta PythonAnywhere criada
- [ ] Projeto enviado para ~/TerneirasPro  
- [ ] Arquivo .env configurado corretamente
- [ ] Script deploy_pythonanywhere.sh executado
- [ ] Web app configurado no painel
- [ ] WSGI file editado
- [ ] Static files configurados
- [ ] Banco migrado e superusuário criado
- [ ] Dados iniciais carregados (seed_referenciais, seed_criterios)
- [ ] Aplicação recarregada
- [ ] Teste de acesso funcionando
- [ ] Backup configurado

**Sua instalação está completa!** 🎉

---

## 💰 **CUSTOS ESTIMADOS**

| Plano | Custo/mês | Recursos |
|---|---:|---|
| **Beginner (Gratuito)** | $0 | CPU limitada, HTTP apenas |
| **Hacker** | $5 | HTTPS, sem limite CPU |  
| **Web Developer** | $12 | MySQL, mais recursos |

**Recomendação:** Iniciar com gratuito para testes, depois Hacker ($5) para produção.

---

**Desenvolvedor:** Victor Rodrigues - Passo Fundo/RS  
**Suporte:** Consulte MANUAL_DO_USUARIO.md para operação do sistema