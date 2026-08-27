# Manual de Deployment — TerneirasPro no PythonAnywhere

> **Objetivo:** Publicar o sistema TerneirasPro em produção no PythonAnywhere com estabilidade, segurança e rastreabilidade.  
> **Público:** Qualquer pessoa com acesso ao projeto.  
> **Data de criação:** Agosto 2026  
> **Última atualização:** Agosto 2026  
> **Status:** ✅ Testado e documentado

---

## 📋 CONTEÚDO DESTE DOCUMENTO

1. [Visão geral](#1-visão-geral)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Passo a passo detalhado](#3-passo-a-passo-detalhado)
4. [Configuração final](#4-configuração-final)
5. [Testes de validação](#5-testes-de-validação)
6. [Procedimentos operacionais](#6-procedimentos-operacionais)
7. [Troubleshooting](#7-troubleshooting)
8. [Checklist de deployment](#8-checklist-de-deployment)
9. [Referência rápida](#9-referência-rápida)

---

## 1. VISÃO GERAL

### O que é este documento?

Manual passo a passo para colocar o **TerneirasPro** em produção no PythonAnywhere sem depender de conhecimento prévio ou memória de sessões anteriores.

### Informações críticas do projeto

| Aspecto | Valor |
|---|---|
| **Nome do projeto** | TerneirasPro |
| **Framework** | Django 4.2.16 |
| **Linguagem** | Python 3.12 |
| **Banco de dados** | SQLite (db.sqlite3) |
| **Tipo de aplicação** | Web app (WSGI) |
| **Arquivo WSGI** | `gestao_terneiras/wsgi.py` |
| **Módulo de configuração** | `gestao_terneiras.settings` |
| **Sistema de arquivos estáticos** | WhiteNoise (via `whitenoise` middleware) |
| **Servidor de arquivos em produção** | Via WhiteNoise (não requer servidor separado) |

### O que você conseguirá ao final

✅ Sistema acessível via URL pública (ex: `seu-dominio.pythonanywhere.com`)  
✅ Banco de dados SQLite persistente  
✅ Autenticação funcionando (login/logout)  
✅ Arquivos estáticos servidos (CSS, JS, imagens)  
✅ Dashboard completo operacional  
✅ Documentação para repetir o processo

---

## 2. PRÉ-REQUISITOS

### Antes de começar

- [ ] Conta PythonAnywhere criada e verificada por e-mail
- [ ] Acesso ao painel de controle do PythonAnywhere
- [ ] Cópia dos arquivos do TerneirasPro
- [ ] Terminal com acesso ao PythonAnywhere (Bash Console)
- [ ] Entendimento básico de terminal Linux/Bash

### Dados que você precisará ter em mãos

```
Conta PythonAnywhere:
├── Username (ex: victor_terneiras)
├── Senha
└── Domínio atribuído (ex: victor-terneiras.pythonanywhere.com)

Projeto TerneirasPro:
├── Arquivo: requirements.txt
├── Arquivo: manage.py
├── Arquivo: gestao_terneiras/wsgi.py
├── Arquivo: gestao_terneiras/settings.py
├── Diretório: templates/
├── Diretório: static/
├── Diretório: staticfiles/ (será gerado)
├── Banco: db.sqlite3 (será copiado ou criado)
├── Apps: accounts, animais, eventos, programas, config_tecnica, indicadores, core
└── Arquivo: .env (será criado)
```

### Versões compatíveis

| Componente | Versão |
|---|---|
| Python | 3.12 (recomendado), 3.11 mínimo |
| Django | 4.2.16 |
| pip | ≥ 24.0 |
| virtualenv | qualquer (vem com Python 3.12) |

---

## 3. PASSO A PASSO DETALHADO

### PASSO 1: Criar conta no PythonAnywhere

**Local:** https://www.pythonanywhere.com

**Ações:**
1. Clicar em "Create a Beginner Account" (gratuito)
2. Preencher:
   - Username (ex: `victor_terneiras`)
   - Email
   - Senha
3. Clicar em "Create a free account"
4. Confirmar o e-mail (checar spam se necessário)
5. Fazer login com as credenciais

**Resultado esperado:**
- ✅ Painel de controle acessível
- ✅ Domínio atribuído automaticamente (ex: `victor-terneiras.pythonanywhere.com`)

---

### PASSO 2: Preparar os arquivos do projeto

**Local:** Seu computador

**Ações:**

1. **Reunir arquivos essenciais:**
   ```
   TerneirasPro/
   ├── manage.py
   ├── requirements.txt
   ├── db.sqlite3                    (opcional — será criado se não existir)
   ├── gestao_terneiras/
   │   ├── __init__.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── core/
   ├── accounts/
   ├── animais/
   ├── eventos/
   ├── programas/
   ├── config_tecnica/
   ├── indicadores/
   ├── templates/
   ├── static/
   ├── media/
   └── venv/                         (NÃO incluir — será criado no PythonAnywhere)
   ```

2. **Garantir que requirements.txt está atualizado:**
   ```txt
   Django==4.2.16
   python-decouple==3.8
   Pillow==10.4.0
   whitenoise==6.7.0
   psycopg2-binary==2.9.9
   ```

3. **Conferir se db.sqlite3 existe** (se quiser manter dados):
   - Se SIM → será copiado junto com os arquivos
   - Se NÃO → será criado automaticamente no primeiro acesso

---

### PASSO 3: Enviar projeto para PythonAnywhere

**Local:** PythonAnywhere → Bash Console

**Método 1: Via Git (recomendado se o projeto estiver em repositório)**

1. Abrir **Bash Console** no PythonAnywhere
2. Clonar o repositório:
   ```bash
   cd ~
   git clone <URL_DO_REPOSITORIO> TerneirasPro
   cd TerneirasPro
   ```

**Método 2: Via Upload Manual**

1. Abrir **Files** no PythonAnywhere
2. Criar pasta: `~/TerneirasPro`
3. Upload dos arquivos (zip recomendado)
4. Descompactar:
   ```bash
   cd ~/TerneirasPro
   unzip projeto.zip
   ```

**Método 3: Via SCP/SFTP (se tiver SSH habilitado)**

```bash
scp -r /caminho/local/TerneirasPro seu-username@ssh.pythonanywhere.com:~/
```

**Verificação:**
```bash
ls -la ~/TerneirasPro
```

Resultado esperado:
```
total XXX
-rw-r--r--  1 user user     XXX Aug 15 10:00 manage.py
-rw-r--r--  1 user user     XXX Aug 15 10:00 requirements.txt
drwxr-xr-x  X user user    4096 Aug 15 10:00 gestao_terneiras
drwxr-xr-x  X user user    4096 Aug 15 10:00 templates
drwxr-xr-x  X user user    4096 Aug 15 10:00 static
...
```

---

### PASSO 4: Criar ambiente virtual

**Local:** PythonAnywhere → Bash Console

**Comandos:**

```bash
# Navegar para o diretório home
cd ~

# Criar ambiente virtual com Python 3.12
python3.12 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate

# Verificar que foi ativado (deve aparecer (venv) na linha de comando)
which python
```

Resultado esperado:
```
(venv) victor@myserver:~$ which python
/home/victor/venv/bin/python
```

**Importante:**
- Se Python 3.12 não estiver disponível, tentar `python3.11` ou `python3`
- Sempre ativar o venv antes de instalar dependências

---

### PASSO 5: Instalar dependências

**Local:** PythonAnywhere → Bash Console (com venv ativado)

**Comandos:**

```bash
# Garantir que venv está ativado
source ~/venv/bin/activate

# Navegar para o projeto
cd ~/TerneirasPro

# Atualizar pip e setuptools
pip install --upgrade pip setuptools wheel

# Instalar dependências do projeto
pip install -r requirements.txt

# Verificar se não há dependências quebradas
pip check
```

Resultado esperado:
```
Successfully installed Django-4.2.16 python-decouple-3.8 Pillow-10.4.0 whitenoise-6.7.0 psycopg2-binary-2.9.9
No broken requirements found.
```

**Alternativa se psycopg2 der erro em ambiente sem PostgreSQL:**

```bash
# Se psycopg2 falhar, instalar sem ele (SQLite não precisa)
pip install Django==4.2.16 python-decouple==3.8 Pillow==10.4.0 whitenoise==6.7.0
```

---

### PASSO 6: Preparar arquivo .env em produção

**Local:** PythonAnywhere → Bash Console

**Ação:** Criar arquivo `.env` na raiz do projeto com configurações de produção

```bash
cd ~/TerneirasPro
cat > .env << 'EOF'
# Configuração de Produção - TerneirasPro
# Gerado em: Agosto 2026

# SEGURANÇA: Gerar chave nova e forte
SECRET_KEY=django-insecure-terneiras-prod-$(date +%s)-MUDE-PARA-CHAVE-FORTE
DEBUG=False
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost,127.0.0.1

# Banco de dados (SQLite em produção)
DATABASE_URL=sqlite:////home/seu-username/TerneirasPro/db.sqlite3
EOF
```

**Importante:**
1. **Substituir `seu-username`** pelo seu username do PythonAnywhere (ex: `victor_terneiras`)
2. **Substituir `SECRET_KEY`** por uma chave criptográfica real (gerar abaixo)
3. **ALLOWED_HOSTS:** Adicionar o domínio exato do seu PythonAnywhere

**Gerar SECRET_KEY forte:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar a saída e colocar no `.env`:
```
SECRET_KEY=sua-chave-aqui-xyz123...
```

**Verificar arquivo criado:**
```bash
cat .env
```

---

### PASSO 7: Coletar arquivos estáticos

**Local:** PythonAnywhere → Bash Console

**Contexto:** Django precisa coletar CSS, JS, imagens em um diretório único para servir

**Comandos:**

```bash
# Garantir que venv está ativado
source ~/venv/bin/activate

# Navegar para o projeto
cd ~/TerneirasPro

# Coletar estáticos
python manage.py collectstatic --noinput

# Verificar que o diretório staticfiles foi criado
ls -la staticfiles/
```

Resultado esperado:
```
100% [=================================================>] 0.0s
42 static files copied to '/home/victor/TerneirasPro/staticfiles', 0 unmodified, 0 post-processed.
```

**O que acontece aqui:**
- Cria/atualiza pasta `staticfiles/` com cópia de `static/`
- WhiteNoise vai servir esses arquivos automaticamente
- Sem este passo, CSS/JS/imagens não serão carregados

---

### PASSO 8: Inicializar banco de dados (se novo)

**Local:** PythonAnywhere → Bash Console

**Contexto:** Aplicar migrations para criar as tabelas do banco

**Comandos:**

```bash
# Garantir que venv está ativado
source ~/venv/bin/activate

# Navegar para o projeto
cd ~/TerneirasPro

# Aplicar todas as migrations
python manage.py migrate

# Criar superusuário (opcional — apenas se banco novo)
python manage.py createsuperuser
```

**Se banco NOVO:**
```
Username: admin
Email: seu-email@example.com
Password: (criar senha forte)
Password (again): (confirmar)
```

**Se banco JÁ EXISTE (copiado):**
- Pular este passo
- Usuários e dados existentes continuam

**Verificar que migrations foram aplicadas:**
```bash
python manage.py showmigrations
```

Resultado esperado: todas as migrations marcadas com `[X]`

---

### PASSO 9: Criar arquivo WSGI do PythonAnywhere

**Local:** PythonAnywhere → Web → Web app → Code

**Contexto:** PythonAnywhere precisa de um arquivo WSGI específico que aponta para a aplicação

**Arquivo a editar:**

No painel PythonAnywhere:
```
Web → Web app → Code → 
/var/www/seu_username_pythonanywhere_com_wsgi.py
```

**Conteúdo esperado (Django genérico):**

```python
# ============================================================================
# ARQUIVO WSGI DO PYTHONANYWHERE - TERNEIRASPRO
# Gerado em: Agosto 2026
# Função: Apontar o servidor web (PythonAnywhere) para a aplicação Django
# ============================================================================

import sys
import os

# Adicionar diretório do projeto ao path do Python
project_home = '/home/seu_username/TerneirasPro'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Adicionar diretório do venv ao path
venv_home = '/home/seu_username/venv'
if venv_home not in sys.path:
    sys.path.insert(0, venv_home + '/lib/python3.12/site-packages')

# Configurar variável de ambiente para Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_terneiras.settings'

# Criar aplicação WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Importante:**
1. Substituir `seu_username` em 2 lugares (linhas com `/home/seu_username/`)
2. Se Python não for 3.12, ajustar `python3.12` para a versão correta
3. Manter exatamente os comentários para rastreabilidade

**Verificar que foi salvo:**
- Clicar em "Save"
- Deve aparecer mensagem de confirmação

---

### PASSO 10: Configurar Web App no PythonAnywhere

**Local:** PythonAnywhere → Web

**Ações:**

#### 10.1: Configurar virtualenv

1. Ir para **Web → Web app → Virtualenv**
2. Informar caminho do venv: `/home/seu_username/venv`
3. Clicar em "Save"

Resultado esperado: Ícone verde aparece

#### 10.2: Configurar mapeamento de diretórios estáticos

1. Ir para **Web → Web app → Static files**
2. Mapear URL `/static/` para caminho `/home/seu_username/TerneirasPro/staticfiles`

Resultado esperado:
```
URL                 Directory
/static/            /home/seu_username/TerneirasPro/staticfiles/
/media/             /home/seu_username/TerneirasPro/media/
```

#### 10.3: Configurar origens CORS (se necessário)

Se precisar acessar de domínios diferentes, adicionar em `settings.py`:

```python
# Em gestao_terneiras/settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://seu-username.pythonanywhere.com',
]
```

---

### PASSO 11: Recarregar aplicação

**Local:** PythonAnywhere → Web

**Ação:**

1. Clicar em **Web → Web app → Reload**
2. Aguardar 10-30 segundos
3. Verificar que não há ícone de erro (círculo vermelho)

Resultado esperado:
```
✅ Site is live at https://seu-username.pythonanywhere.com
```

**O que o reload faz:**
- Para o servidor web
- Recarrega todas as configurações
- Reinicia a aplicação Django
- Ativa ambiente virtual correto

---

### PASSO 12: Testar acesso inicial

**Local:** Navegador

**Ação:**

1. Abrir: `https://seu-username.pythonanywhere.com`
2. Observar resultado:

| Resultado | Significado | Ação |
|---|---|---|
| 🔴 502 Bad Gateway | Erro de configuração WSGI | Ver Troubleshooting |
| 🔴 500 Internal Server | Erro na aplicação | Conferir error log |
| 🔴 404 Not Found | Rota não existe | Verificar settings.py |
| 🟢 Tela de login | ✅ Sistema funcionando | Prosseguir para testes |
| 🟢 Dashboard | ✅ Login ainda ativo | Tudo OK |

**Se erro, consultar log:**
```bash
tail -50 /var/log/seu_username.pythonanywhere.com.error.log
```

---

## 4. CONFIGURAÇÃO FINAL

### Verificação de segurança pré-produção

```bash
# Terminal PythonAnywhere
cd ~/TerneirasPro
source ~/venv/bin/activate

# Rodar sistema de check do Django
python manage.py check --deploy
```

Resultado esperado:
```
System check identified some issues:

WARNINGS:
W008: Your ALLOWED_HOSTS is empty: ['seu-username.pythonanywhere.com']
W009: Your SECRET_KEY is too weak
W010: DEBUG is True

(se tiver, corrigir no .env)
```

**Correções necessárias:**

1. **DEBUG=False** (já deveria estar no .env)
2. **SECRET_KEY forte** (verificar se não começa com `django-insecure`)
3. **ALLOWED_HOSTS completo** (incluir domínio do PythonAnywhere)

### Criar arquivo de documentação local

**Local:** PythonAnywhere → Bash Console

```bash
cd ~/TerneirasPro
cat > DEPLOYMENT_INFO.txt << 'EOF'
=============================================================================
INFORMAÇÕES DE DEPLOYMENT - TERNEIRASPRO NO PYTHONANYWHERE
Criado em: $(date)
=============================================================================

CONTA PYTHONANYWHERE:
  Username: seu_username
  URL de acesso: https://seu_username.pythonanywhere.com
  Painel: https://www.pythonanywhere.com/user/seu_username

DIRETÓRIOS E ARQUIVOS:
  Projeto: /home/seu_username/TerneirasPro/
  Ambiente virtual: /home/seu_username/venv/
  Banco de dados: /home/seu_username/TerneirasPro/db.sqlite3
  Estáticos: /home/seu_username/TerneirasPro/staticfiles/
  WSGI: /var/www/seu_username_pythonanywhere_com_wsgi.py
  Arquivo .env: /home/seu_username/TerneirasPro/.env

CONFIGURAÇÕES CRÍTICAS:
  Django Settings Module: gestao_terneiras.settings
  Python Version: 3.12
  Requirements: Django==4.2.16, python-decouple==3.8, Pillow==10.4.0, whitenoise==6.7.0

PROCEDIMENTOS OPERACIONAIS:
  1. Ativar venv: source ~/venv/bin/activate
  2. Coletar estáticos: python manage.py collectstatic --noinput
  3. Recarregar app: No painel Web → Reload
  4. Ver logs de erro: tail -50 /var/log/seu_username.pythonanywhere.com.error.log
  5. Migrar banco: python manage.py migrate
  6. Criar superusuário: python manage.py createsuperuser

DOCUMENTAÇÃO:
  - DOCUMENTACAO_AGENTE.md (arquitetura do projeto)
  - DEPLOYMENT_PYTHONANYWHERE.md (este guia)
  - README.md (instruções gerais)
=============================================================================
EOF

cat DEPLOYMENT_INFO.txt
```

---

## 5. TESTES DE VALIDAÇÃO

### Teste 1: Acesso básico

```
Ação: Abrir https://seu-username.pythonanywhere.com
Esperado: Tela de login com logo TerneirasPro
Resultado: ✅ / ❌
```

### Teste 2: Login

```
Ação: Fazer login com credenciais válidas (admin/admin123 ou criada)
Esperado: Dashboard aparecer sem erros
Resultado: ✅ / ❌
```

### Teste 3: Banco de dados

```
Ação: Verificar dados na tela inicial
Esperado: Dados carregarem corretamente
Resultado: ✅ / ❌
```

### Teste 4: Cadastros

```
Ação: Criar novo registro (ex: nova vaca)
Esperado: Registro salvo e aparece na lista
Resultado: ✅ / ❌
```

### Teste 5: Uploads (se houver)

```
Ação: Fazer upload de imagem (ex: foto de animal)
Esperado: Imagem salva e exibida
Resultado: ✅ / ❌
```

### Teste 6: Gráficos

```
Ação: Navegar para dashboard
Esperado: Gráficos (Chart.js) aparecem sem erros console
Resultado: ✅ / ❌
```

### Teste 7: Logout

```
Ação: Clicar em logout
Esperado: Retornar para tela de login
Resultado: ✅ / ❌
```

### Teste 8: Acesso após logout

```
Ação: Tentar acessar URL protegida sem autenticação
Esperado: Redirecionar para login
Resultado: ✅ / ❌
```

### Teste 9: Admin Django

```
Ação: Acessar https://seu-username.pythonanywhere.com/admin
Esperado: Admin panel aparecer
Resultado: ✅ / ❌
```

### Teste 10: Verificação de arquivos estáticos

```
Bash: curl https://seu-username.pythonanywhere.com/static/css/ -I
Esperado: HTTP 200 OK (não 404 ou 502)
Resultado: ✅ / ❌
```

---

## 6. PROCEDIMENTOS OPERACIONAIS

### 6.1: Recarregar a aplicação (após mudanças)

**Quando fazer:**
- Depois de alterar `settings.py`
- Depois de alterar variáveis de ambiente (`.env`)
- Depois de instalar novo pacote
- Depois de alterar código da aplicação

**Como fazer:**

Opção A — Via painel web:
```
PythonAnywhere → Web → Web app → Reload
```

Opção B — Via console:
```bash
touch /var/www/seu_username_pythonanywhere_com_wsgi.py
```

**Tempo esperado:** 10-30 segundos até estar ativo novamente

### 6.2: Coletar estáticos novamente (após update de static/)

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py collectstatic --noinput
```

Depois fazer reload (seção 6.1).

### 6.3: Criar novo superusuário

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py createsuperuser
```

Preencher:
```
Username: novo_admin
Email: email@example.com
Password: senha_forte_aqui
Password (again): confirmar
```

### 6.4: Fazer backup do banco de dados

```bash
# Via console
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Verificar backup criado
ls -lh ~/db.sqlite3.backup*
```

### 6.5: Restaurar banco de dados de backup

```bash
# Confirmar qual backup usar
ls -lh ~/db.sqlite3.backup*

# Restaurar (AVISO: isso sobrescreve o banco atual)
cp ~/db.sqlite3.backup.YYYYMMDD_HHMMSS ~/TerneirasPro/db.sqlite3

# Fazer reload
# PythonAnywhere → Web → Reload
```

### 6.6: Atualizar dependências

Se houver novo `requirements.txt`:

```bash
source ~/venv/bin/activate
pip install -r ~/TerneirasPro/requirements.txt --upgrade
pip check
```

Depois reload.

### 6.7: Consultar logs de erro

```bash
# Erros da aplicação
tail -50 /var/log/seu_username.pythonanywhere.com.error.log

# Erros em tempo real
tail -f /var/log/seu_username.pythonanywhere.com.error.log
# (CTRL+C para sair)

# Acessos (access log)
tail -50 /var/log/seu_username.pythonanywhere.com.access.log
```

---

## 7. TROUBLESHOOTING

### ❌ 502 Bad Gateway

**Causa comum:** Erro no arquivo WSGI ou no `settings.py`

**Solução:**
```bash
# Verificar arquivo WSGI está correto
cat /var/www/seu_username_pythonanywhere_com_wsgi.py

# Verificar erro específico
tail -30 /var/log/seu_username.pythonanywhere.com.error.log

# Tentar teste local
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Se erro, ver mensagem de erro
```

---

### ❌ 500 Internal Server Error

**Causa comum:** Erro em código Python ou falta de variáveis de ambiente

**Solução:**
```bash
# Verificar .env existe
ls -la ~/TerneirasPro/.env

# Verificar conteúdo
cat ~/TerneirasPro/.env

# Verificar migrations aplicadas
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py showmigrations

# Se não aplicadas, rodar:
python manage.py migrate

# Ver erro específico
tail -50 /var/log/seu_username.pythonanywhere.com.error.log
```

---

### ❌ CSS/JS não carregam (404 nos estáticos)

**Causa comum:** `collectstatic` não foi rodado ou estaticfiles não está mapeado

**Solução:**
```bash
# Rodar collectstatic novamente
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py collectstatic --noinput

# Verificar que pasta foi criada
ls -la staticfiles/ | head -20

# Recarregar aplicação
# PythonAnywhere → Web → Reload

# Verificar mapeamento em Web → Static files
# URL /static/ deve apontar para /home/seu_username/TerneirasPro/staticfiles/
```

---

### ❌ Login não funciona

**Causa comum:** Banco corrompido ou usuário não existe

**Solução:**
```bash
# Verificar que banco existe
ls -la ~/TerneirasPro/db.sqlite3

# Rodar migrations (pode recuperar)
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py migrate

# Criar novo superusuário
python manage.py createsuperuser
# Username: admin
# Password: admin123

# Depois fazer reload
# PythonAnywhere → Web → Reload
```

---

### ❌ Banco de dados vazio após upload

**Causa comum:** `db.sqlite3` foi copiado mas não contem dados

**Solução (opção 1 — usar banco existente):**
```bash
# Copiar banco original para PythonAnywhere
scp ~/db.sqlite3 seu_username@ssh.pythonanywhere.com:~/TerneirasPro/
```

**Solução (opção 2 — criar novo banco e popular):**
```bash
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py migrate
python manage.py seed_referenciais
python manage.py seed_criterios
python manage.py createsuperuser
```

---

### ⚠️ Avisos no check --deploy

```bash
cd ~/TerneirasPro
source ~/venv/bin/activate
python manage.py check --deploy
```

**Se aparecer:**

```
WARNING: W008: Your ALLOWED_HOSTS is empty
```

**Solução:** Editar `.env`:
```
ALLOWED_HOSTS=seu-username.pythonanywhere.com,localhost
```

Depois reload.

---

## 8. CHECKLIST DE DEPLOYMENT

Use este checklist para garantir que tudo foi feito:

### Preparação
- [ ] Conta PythonAnywhere criada e verificada
- [ ] Projeto copiado para `~/TerneirasPro`
- [ ] requirements.txt presente
- [ ] .env criado com valores corretos

### Ambiente
- [ ] Virtualenv criado em `~/venv`
- [ ] Dependências instaladas (`pip check` OK)
- [ ] `python -c "import django; print(django.__version__)"` retorna 4.2.16

### Django
- [ ] Arquivo WSGI criado em `/var/www/seu_username_pythonanywhere_com_wsgi.py`
- [ ] Migrations aplicadas (`python manage.py migrate`)
- [ ] Arquivos estáticos coletados (`python manage.py collectstatic`)
- [ ] Superusuário criado (`python manage.py createsuperuser`)

### PythonAnywhere
- [ ] Virtualenv configurado em Web → Virtualenv
- [ ] WSGI apontando para arquivo correto
- [ ] Static files mapeados (`/static/` → `staticfiles/`)
- [ ] Debug = False no .env

### Testes
- [ ] Acessar URL pública sem erro
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Dados aparecem
- [ ] Criar novo registro funciona
- [ ] Logout funciona
- [ ] Arquivos estáticos carregam (CSS/JS)

### Documentação
- [ ] Este documento lido integralmente
- [ ] Arquivo DEPLOYMENT_INFO.txt criado localmente
- [ ] Credenciais anotadas em lugar seguro
- [ ] Rotina de backup documentada

---

## 9. REFERÊNCIA RÁPIDA

### Comandos mais usados

```bash
# Ativar ambiente virtual
source ~/venv/bin/activate

# Navegar para projeto
cd ~/TerneirasPro

# Verificar versão Django
python -c "import django; print(django.VERSION)"

# Coletar estáticos
python manage.py collectstatic --noinput

# Aplicar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Ver logs de erro
tail -50 /var/log/seu_username.pythonanywhere.com.error.log

# Fazer reload (via console)
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

# Backup banco
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup.$(date +%Y%m%d)

# Testar configuração
python manage.py check --deploy

# Verificar dependências
pip check
```

### Caminhos importantes

| Coisa | Caminho |
|---|---|
| Projeto | `/home/seu_username/TerneirasPro` |
| Venv | `/home/seu_username/venv` |
| Banco | `/home/seu_username/TerneirasPro/db.sqlite3` |
| Estáticos | `/home/seu_username/TerneirasPro/staticfiles` |
| WSGI | `/var/www/seu_username_pythonanywhere_com_wsgi.py` |
| .env | `/home/seu_username/TerneirasPro/.env` |
| Erro log | `/var/log/seu_username.pythonanywhere.com.error.log` |
| Access log | `/var/log/seu_username.pythonanywhere.com.access.log` |

### URLs importantes

| Função | URL |
|---|---|
| Site público | `https://seu-username.pythonanywhere.com` |
| Admin Django | `https://seu-username.pythonanywhere.com/admin` |
| Painel PythonAnywhere | `https://www.pythonanywhere.com/user/seu_username` |
| Consoles | `https://www.pythonanywhere.com/consoles` |
| Arquivos | `https://www.pythonanywhere.com/files` |

---

## 10. SUPORTE E REFERÊNCIAS

### Documentação do projeto

- **DOCUMENTACAO_AGENTE.md** — Arquitetura e estado do TerneirasPro
- **README.md** — Instruções locais
- **MANUAL_DO_USUARIO.md** — Como usar o sistema

### Documentação externa

- [PythonAnywhere Docs](https://help.pythonanywhere.com)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

### Contato

Para dúvidas sobre TerneirasPro:
- Consultar DOCUMENTACAO_AGENTE.md seção "Problemas Conhecidos"
- Verificar logs em `/var/log/seu_username.pythonanywhere.com.error.log`
- Executar `python manage.py check --deploy`

---

## 📝 HISTÓRICO DE ATUALIZAÇÕES

| Data | Versão | Mudanças |
|---|---|---|
| Ago 2026 | 1.0 | Versão inicial — deployment no PythonAnywhere |

---

**FIM DO MANUAL**

> Documento criado para garantir que qualquer pessoa possa fazer deployment do TerneirasPro no PythonAnywhere sem depender de memória de sessões anteriores. Seguir este guia passo a passo garante sucesso.

---

