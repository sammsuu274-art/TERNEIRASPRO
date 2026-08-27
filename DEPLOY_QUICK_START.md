# 🚀 QUICK START — Deployment TerneirasPro no PythonAnywhere

> **Para quem tem pressa:** Resumo executivo do manual completo em 5 minutos.

---

## 📋 PRÉ-REQUISITOS

- [ ] Conta PythonAnywhere criada (free ou paga)
- [ ] Projeto TerneirasPro disponível
- [ ] Conhecimento básico de terminal
- [ ] Arquivo `requirements.txt` atualizado

---

## 🎯 5 PASSOS PRINCIPAIS

### PASSO 1: Enviar projeto (5 min)

**No PythonAnywhere → Bash Console:**

```bash
# Opção A: Via Git
cd ~
git clone <url-do-repo> TerneirasPro

# Opção B: Via upload manual
# 1. Web Files → Upload ZIP do projeto
# 2. Descompactar na pasta ~/TerneirasPro
```

### PASSO 2: Criar ambiente virtual (3 min)

```bash
python3.12 -m venv ~/venv
source ~/venv/bin/activate
```

### PASSO 3: Instalar dependências (2 min)

```bash
cd ~/TerneirasPro
pip install -r requirements.txt
pip check  # Deve retornar "No broken requirements found"
```

### PASSO 4: Preparar Django (5 min)

```bash
# Criar .env com valores corretos (ver abaixo)
cat > .env << 'EOF'
SECRET_KEY=cole-aqui-chave-gerada
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost
EOF

# Migrations
python manage.py migrate

# Estáticos
python manage.py collectstatic --noinput

# Superusuário (se banco novo)
python manage.py createsuperuser
```

### PASSO 5: Configurar no painel (5 min)

**PythonAnywhere → Web:**

1. **Virtualenv:** `/home/seu_username/venv`
2. **WSGI:** Editar `/var/www/seu_username_pythonanywhere_com_wsgi.py`
3. **Static files:** `/static/` → `/home/seu_username/TerneirasPro/staticfiles/`
4. **Reload:** Clicar em "Reload"

---

## 🔑 GERAR SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar a saída e colocar no `.env`.

---

## 📄 ARQUIVO WSGI (PythonAnywhere)

Editar: `/var/www/seu_username_pythonanywhere_com_wsgi.py`

```python
import sys
import os

project_home = '/home/seu_username/TerneirasPro'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

venv_home = '/home/seu_username/venv'
if venv_home not in sys.path:
    sys.path.insert(0, venv_home + '/lib/python3.12/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_terneiras.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Importante:** Substituir `seu_username` em 3 lugares

---

## ✅ TESTES RÁPIDOS

```bash
# Tudo OK?
python manage.py check --deploy

# Dependências OK?
pip check

# Banco OK?
python manage.py showmigrations

# Estáticos OK?
ls -la staticfiles/ | wc -l  # Deve ter muitos arquivos
```

---

## 🌐 ACESSAR O SISTEMA

- **URL:** `https://seu-username.pythonanywhere.com`
- **Admin:** `https://seu-username.pythonanywhere.com/admin`
- **Login padrão:** `admin` / `admin123` (se criado)

---

## ⚠️ ERROS COMUNS

| Erro | Causa | Solução |
|---|---|---|
| 502 Bad Gateway | WSGI incorreto | Conferir arquivo WSGI e caminhos |
| 500 Error | Arquivo .env faltando | Criar `.env` com SECRET_KEY |
| CSS não carrega | Estáticos não coletados | Rodar `collectstatic` novamente |
| Login não funciona | Banco vazio | Rodar `migrate` + `createsuperuser` |

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ativar venv
source ~/venv/bin/activate

# Ver erros
tail -50 /var/log/seu_username.pythonanywhere.com.error.log

# Recarregar app
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

# Backup banco
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup

# Novo superusuário
cd ~/TerneirasPro && python manage.py createsuperuser
```

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para detalhes: **DEPLOYMENT_PYTHONANYWHERE.md**

---

**Sucesso! 🎉**

