# 🆕 Deployment em Novo Ambiente — TerneirasPro no PythonAnywhere

> **Objetivo:** Criar uma segunda instalação completa do TerneirasPro em **nova conta PythonAnywhere** para outra pessoa testar, mantendo o ambiente atual intacto.

> **Público:** Qualquer pessoa que precise fazer deployment em conta separada.

> **Data de criação:** Agosto 2026  
> **Status:** ✅ Baseado em documentação existente

---

## ⚠️ AVISO IMPORTANTE

Este documento descreve como criar um **segundo ambiente completamente independente**:

- ✅ **Ambiente Atual:** Não será alterado
- ✅ **Novo Ambiente:** Será criado em conta PythonAnywhere diferente
- ✅ **Isolamento Total:** Dados do novo ambiente não afetam o atual
- ✅ **Para Teste:** Usuário/fazenda de teste dedicados
- ✅ **Reproduzível:** Qualquer pessoa consegue seguir este guia

---

## 📋 ÍNDICE

1. [Visão geral](#1-visão-geral)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Checklist de preparação](#3-checklist-de-preparação)
4. [12 Passos do deployment](#4-12-passos-do-deployment)
5. [Criação do banco de teste](#5-criação-do-banco-de-teste)
6. [Primeiro login e validação](#6-primeiro-login-e-validação)
7. [Troubleshooting específico](#7-troubleshooting-específico)
8. [Checklist de validação](#8-checklist-de-validação)
9. [Referência rápida](#9-referência-rápida)

---

## 1. VISÃO GERAL

### O que é este documento?

Guia completo para criar uma **segunda instalação do TerneirasPro** em **nova conta PythonAnywhere**, destinada para outro usuário fazer testes de forma independente.

### Diferença entre ambientes

| Aspecto | Ambiente Atual | Novo Ambiente |
|---|---|---|
| **Conta PythonAnywhere** | victor_terneiras (ou atual) | novo_usuario_terneiras (ou nome novo) |
| **Domínio** | victor-terneiras.pythonanywhere.com | novo-usuario-terneiras.pythonanywhere.com |
| **Banco de dados** | db.sqlite3 atual | db.sqlite3 novo (vazio ou com dados de teste) |
| **Propriedades** | Dados atuais | Fazenda de teste apenas |
| **Usuários** | admin atual | admin_teste nova conta |
| **Alterações no código** | ❌ Nenhuma | ❌ Nenhuma |
| **Isolamento** | ✅ Completo | ✅ Completo |

### Resultado esperado

Após seguir este guia:

```
Ambiente Atual (sem alterações)
├── https://victor-terneiras.pythonanywhere.com
├── Dados originais intactos
└── Funcionando normalmente

Novo Ambiente (independente)
├── https://novo-usuario-terneiras.pythonanywhere.com
├── Dados de teste (novo banco)
├── Usuário admin_teste
└── Pronto para testar
```

---

## 2. PRÉ-REQUISITOS

### Para quem vai criar o novo ambiente

- [ ] Acesso ao código-fonte do TerneirasPro (seu computador)
- [ ] `requirements.txt` atualizado
- [ ] Arquivo `.env.production.template` disponível
- [ ] Script `deploy_pythonanywhere.sh` disponível
- [ ] Entendimento básico de terminal

### Para a segunda pessoa (testador)

- [ ] Conta PythonAnywhere nova criada (https://www.pythonanywhere.com)
- [ ] Email verificado
- [ ] Senha salva em lugar seguro
- [ ] Acesso ao Bash Console do PythonAnywhere

### Dados que você precisará

```
Seu ambiente (origem):
├── Caminho local: /caminho/para/TerneirasPro
├── Arquivo: requirements.txt
├── Arquivo: manage.py
└── Arquivo: deploy_pythonanywhere.sh

Novo ambiente (destino):
├── Username PythonAnywhere: [será atribuído]
├── Email: [da segunda pessoa]
├── Domínio: [será atribuído automaticamente]
└── Senha: [a segunda pessoa escolhe]
```

---

## 3. CHECKLIST DE PREPARAÇÃO

Antes de começar, verificar que você tem:

### Código-fonte
- [ ] Projeto TerneirasPro disponível localmente
- [ ] requirements.txt presente
- [ ] Arquivo `.env.production.template` presente
- [ ] Script `deploy_pythonanywhere.sh` presente
- [ ] `manage.py` na raiz

### Documentação
- [ ] DEPLOYMENT_PYTHONANYWHERE.md lido
- [ ] DEPLOY_TROUBLESHOOTING.md em mãos
- [ ] DEPLOY_QUICK_START.md como referência
- [ ] Este documento impresso ou aberto

### Coordenação com testador
- [ ] Outra pessoa criou conta PythonAnywhere ✅
- [ ] Email dela foi verificado ✅
- [ ] Username da nova conta definido ✅
- [ ] Senha salva em lugar seguro ✅

---

## 4. 12 PASSOS DO DEPLOYMENT

### PASSO 1: Segunda pessoa cria conta PythonAnywhere

**Quem faz:** A segunda pessoa (testador)  
**Local:** https://www.pythonanywhere.com  
**Tempo:** 5 minutos

**Ações:**
1. Clicar em "Create a Beginner Account" (gratuito)
2. Preencher:
   - Username: ex: `paulo_teste_terneiras`
   - Email: email pessoal dela
   - Senha: criar forte e salvar
3. Clicar em "Create a free account"
4. Verificar e-mail (checar spam)
5. Fazer login com credenciais

**Resultado:**
- ✅ Painel PythonAnywhere acessível
- ✅ Domínio atribuído (ex: `paulo-teste-terneiras.pythonanywhere.com`)
- ✅ Username registrado (ex: `paulo_teste_terneiras`)

**Próximo:** Ela envia o username para você

---

### PASSO 2: Você prepara arquivos para enviar

**Quem faz:** Você (criador do novo ambiente)  
**Local:** Seu computador  
**Tempo:** 5 minutos

**Ações:**

1. **Reunir arquivos necessários:**
   ```bash
   # No seu computador, criar pasta com tudo que precisa
   mkdir TerneirasPro_para_deploy
   cp -r /caminho/TerneirasPro/* TerneirasPro_para_deploy/
   ```

2. **Verificar que tem:**
   ```
   TerneirasPro_para_deploy/
   ├── manage.py                    ✓
   ├── requirements.txt             ✓
   ├── gestao_terneiras/
   │   ├── settings.py              ✓
   │   ├── urls.py                  ✓
   │   └── wsgi.py                  ✓
   ├── core/                        ✓
   ├── accounts/                    ✓
   ├── animais/                     ✓
   ├── eventos/                     ✓
   ├── programas/                   ✓
   ├── config_tecnica/              ✓
   ├── indicadores/                 ✓
   ├── templates/                   ✓
   ├── static/                      ✓
   └── venv/                        ✗ NÃO INCLUIR
   ```

3. **Compactar para envio:**
   ```bash
   # NÃO incluir venv nem db.sqlite3
   zip -r TerneirasPro.zip TerneirasPro_para_deploy/ \
     -x "*/venv/*" "*/db.sqlite3" "*/__pycache__/*" "*/.git/*"
   ```

**Resultado:**
- ✅ Arquivo `TerneirasPro.zip` criado (~10-15 MB)
- ✅ Pronto para segunda pessoa fazer upload

**Próximo:** Você envia arquivo para segunda pessoa via e-mail/nuvem

---

### PASSO 3: Segunda pessoa faz upload para PythonAnywhere

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Files  
**Tempo:** 10-15 minutos

**Ações:**

1. **Entrar em PythonAnywhere:**
   - URL: https://www.pythonanywhere.com/user/seu_username (ela coloca o username dela)
   - Fazer login

2. **Ir para Files:**
   - Clicar em "Files"
   - Criar nova pasta: clique no botão "New folder"
   - Nome: `TerneirasPro`

3. **Upload do arquivo:**
   - Dentro de pasta `TerneirasPro`
   - Clicar em "Upload a file"
   - Selecionar `TerneirasPro.zip`
   - Aguardar conclusão

4. **Descompactar:**
   - Clique direito no `TerneirasPro.zip`
   - Selecionar "Unzip"
   - Aguardar conclusão

5. **Verificar:**
   ```
   ~/TerneirasPro/
   ├── manage.py
   ├── requirements.txt
   ├── gestao_terneiras/
   └── ... (outros arquivos)
   ```

**Resultado:**
- ✅ Arquivos do projeto em `~/TerneirasPro/`
- ✅ Pronto para próximo passo

**Próximo:** Ela envia mensagem confirmando que upload foi feito

---

### PASSO 4: Segunda pessoa cria ambiente virtual

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 3 minutos

**Ações:**

1. **Abrir Bash Console:**
   - PythonAnywhere → Console (ou "Bash console")
   - Tipo: "Bash"
   - Clicar em "Start new console"

2. **Executar comandos:**
   ```bash
   # Criar ambiente virtual
   python3.12 -m venv ~/venv
   
   # Ativar
   source ~/venv/bin/activate
   
   # Verificar que foi ativado (deve aparecer (venv) no prompt)
   which python
   ```

3. **Resultado esperado:**
   ```
   (venv) paulo@myserver:~$ which python
   /home/paulo_teste_terneiras/venv/bin/python
   ```

**Próximo:** Próximo passo — instalar dependências

---

### PASSO 5: Segunda pessoa instala dependências

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 5 minutos

**Ações:**

1. **Ativar venv (se não estiver):**
   ```bash
   source ~/venv/bin/activate
   ```

2. **Navegar para projeto:**
   ```bash
   cd ~/TerneirasPro
   ```

3. **Atualizar pip:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verificar integridade:**
   ```bash
   pip check
   ```

**Resultado esperado:**
```
Successfully installed Django-4.2.16 python-decouple-3.8 Pillow-10.4.0 whitenoise-6.7.0 psycopg2-binary-2.9.9
No broken requirements found.
```

**Próximo:** Configurar arquivo `.env`

---

### PASSO 6: Segunda pessoa cria arquivo .env

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 5 minutos

**Ações:**

1. **Navegar para projeto:**
   ```bash
   cd ~/TerneirasPro
   ```

2. **Gerar SECRET_KEY nova (executar localmente ou no console):**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Copiar a chave gerada e criar arquivo .env:**
   ```bash
   cat > .env << 'EOF'
   SECRET_KEY=COLE_AQUI_A_CHAVE_GERADA
   DEBUG=False
   ALLOWED_HOSTS=paulo-teste-terneiras.pythonanywhere.com,localhost,127.0.0.1
   EOF
   ```

4. **Verificar que foi criado:**
   ```bash
   cat .env
   ```

**Importante:**
- ✅ Substituir `paulo-teste-terneiras.pythonanywhere.com` pelo domínio DELA
- ✅ Substituir `SECRET_KEY` pela chave gerada (não usar a do ambiente atual)
- ✅ DEBUG sempre = False

**Próximo:** Aplicar migrations no banco

---

### PASSO 7: Segunda pessoa aplica migrations

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 3 minutos

**Ações:**

1. **Ativar venv:**
   ```bash
   source ~/venv/bin/activate
   ```

2. **Navegar para projeto:**
   ```bash
   cd ~/TerneirasPro
   ```

3. **Aplicar migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Verificar que aplicaram:**
   ```bash
   python manage.py showmigrations
   ```

**Resultado esperado:**
```
[X] 0001_initial
[X] ... (todas com X)
```

**Próximo:** Criar superusuário de teste

---

### PASSO 8: Segunda pessoa cria superusuário de teste

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 2 minutos

**Ações:**

1. **Ativar venv:**
   ```bash
   source ~/venv/bin/activate
   ```

2. **Navegar para projeto:**
   ```bash
   cd ~/TerneirasPro
   ```

3. **Criar superusuário:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Preencher:**
   ```
   Username: admin_teste
   Email: email-de-teste@example.com
   Password: criar-senha-forte
   Password (again): confirmar
   ```

**Importante:**
- ✅ Username diferente: `admin_teste` (não `admin`)
- ✅ Senha forte (pelo menos 8 caracteres)
- ✅ Anotar credenciais em lugar seguro

**Próximo:** Coletar arquivos estáticos

---

### PASSO 9: Segunda pessoa coleta arquivos estáticos

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Bash Console  
**Tempo:** 2 minutos

**Ações:**

1. **Ativar venv:**
   ```bash
   source ~/venv/bin/activate
   ```

2. **Navegar para projeto:**
   ```bash
   cd ~/TerneirasPro
   ```

3. **Coletar estáticos:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Verificar:**
   ```bash
   ls -la staticfiles/ | head -20
   ```

**Resultado esperado:**
```
42 static files copied to '/home/paulo_teste_terneiras/TerneirasPro/staticfiles', 0 unmodified, 0 post-processed.
```

**Próximo:** Configurar WSGI no painel

---

### PASSO 10: Segunda pessoa configura WSGI

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Web  
**Tempo:** 3 minutos

**Ações:**

1. **Entrar no painel:**
   - PythonAnywhere → Web

2. **Criar novo Web App:**
   - Clicar em "Add a new web app"
   - Selecionar domínio (será `paulo-teste-terneiras.pythonanywhere.com`)
   - Escolher: **Manual configuration** (não framework específico)
   - Selecionar Python: **3.12**

3. **Editar arquivo WSGI:**
   - PythonAnywhere → Web → Web app → Code
   - Link: `/var/www/paulo_teste_terneiras_pythonanywhere_com_wsgi.py`
   - Clicar para abrir e editar

4. **Conteúdo do WSGI:**
   ```python
   # ============================================================================
   # ARQUIVO WSGI - TERNEIRASPRO (NOVO AMBIENTE)
   # ============================================================================
   
   import sys
   import os
   
   # Adicionar diretório do projeto ao path
   project_home = '/home/paulo_teste_terneiras/TerneirasPro'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   
   # Adicionar diretório do venv
   venv_home = '/home/paulo_teste_terneiras/venv'
   if venv_home not in sys.path:
       sys.path.insert(0, venv_home + '/lib/python3.12/site-packages')
   
   # Configuração Django
   os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_terneiras.settings'
   
   # Aplicação WSGI
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. **Substituições necessárias:**
   - Linha com `paulo_teste_terneiras` em 2 lugares (substituir pelo username dela)
   - Linha com `/lib/python3.12/` (conferir se Python é 3.12, senão ajustar)

6. **Salvar:**
   - Clicar em "Save"
   - Deve aparecer mensagem de confirmação

**Próximo:** Configurar Virtualenv

---

### PASSO 11: Segunda pessoa configura Virtual Environment

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Web  
**Tempo:** 2 minutos

**Ações:**

1. **Entrar em:**
   - PythonAnywhere → Web → Web app → Virtualenv

2. **Informar caminho do venv:**
   ```
   /home/paulo_teste_terneiras/venv
   ```

3. **Clicar em "Save"**

4. **Verificar que ícone ficou verde** ✅

**Próximo:** Mapear arquivos estáticos

---

### PASSO 12: Segunda pessoa mapeia Static Files

**Quem faz:** A segunda pessoa (testador)  
**Local:** PythonAnywhere → Web  
**Tempo:** 2 minutos

**Ações:**

1. **Entrar em:**
   - PythonAnywhere → Web → Web app → Static files

2. **Adicionar mapeamento:**
   ```
   URL:       /static/
   Directory: /home/paulo_teste_terneiras/TerneirasPro/staticfiles
   ```

3. **Se houver media upload (opcional):**
   ```
   URL:       /media/
   Directory: /home/paulo_teste_terneiras/TerneirasPro/media
   ```

4. **Clicar em "Save"**

5. **Fazer Reload:**
   - Clicar em "Reload" no topo
   - Aguardar 10-30 segundos

**Resultado esperado:**
```
✅ Site is live at https://paulo-teste-terneiras.pythonanywhere.com
```

---

## 5. CRIAÇÃO DO BANCO DE TESTE

### 5.1 Criar primeira propriedade (fazenda de teste)

**Quem faz:** A segunda pessoa (testador)  
**Local:** Navegador  
**Tempo:** 5 minutos

**Ações:**

1. **Acessar:**
   - URL: `https://paulo-teste-terneiras.pythonanywhere.com`

2. **Deve aparecer:**
   - Tela de login do TerneirasPro

3. **Fazer login:**
   - Username: `admin_teste`
   - Password: (a que foi criada)

4. **Se for primeira vez:**
   - Sistema redireciona para `/primeiro-acesso/`
   - Preencher dados da propriedade:
     ```
     Nome: Fazenda de Testes
     CNPJ/CPF: [opcional]
     Endereço: [opcional]
     Responsável técnico: [opcional]
     ```

5. **Clicar em "Criar Propriedade"**

6. **Resultado:**
   - ✅ Propriedade criada como "ativa"
   - ✅ Superusuário vinculado automaticamente
   - ✅ Redireciona para dashboard

### 5.2 Seed dos dados de referência (opcional)

**Se quiser dados de exemplo:**

```bash
# No Bash Console
source ~/venv/bin/activate
cd ~/TerneirasPro

# Seed de referenciais técnicos
python manage.py seed_referenciais

# Seed de critérios de conformidade
python manage.py seed_criterios --propriedade 1

# Seed de dados de teste (se existir)
python manage.py seed_dados_teste --propriedade 1
```

**Resultado:**
- ✅ Dados de teste carregados
- ✅ Dashboard com dados de exemplo

---

## 6. PRIMEIRO LOGIN E VALIDAÇÃO

### 6.1 Fazer login

**Quem faz:** A segunda pessoa (testador)  
**Local:** Navegador  
**Tempo:** 1 minuto

**Ações:**

1. **URL:**
   ```
   https://paulo-teste-terneiras.pythonanywhere.com/accounts/login/
   ```

2. **Preencher:**
   - Username: `admin_teste`
   - Password: (a que foi criada)

3. **Clicar: "Entrar"**

4. **Verificar:**
   - ✅ Redireciona para dashboard
   - ✅ Sem erro 500
   - ✅ Painel carrega normalmente

### 6.2 Verificar funcionamento básico

**Ações:**

1. **Verificar CSS/JS carregou:**
   - [ ] Página tem cores e formatação
   - [ ] Bootstrap está funcionando
   - [ ] Não é só texto branco

2. **Testar gráficos:**
   - [ ] Gráficos aparecem (se houver dados)
   - [ ] Sem erros no console do navegador

3. **Testar navegação:**
   - [ ] Clicar em "Terneiras" → lista aparece (vazia ou com dados)
   - [ ] Clicar em "Vacas" → lista aparece
   - [ ] Clicar em "Dashboard" → volta ao início

4. **Testar admin:**
   - [ ] Acessar `/admin/` → Django admin aparece
   - [ ] Login funciona
   - [ ] Consegue ver propriedade criada

---

## 7. TROUBLESHOOTING ESPECÍFICO

### ❌ Erro: 502 Bad Gateway

**Solução rápida:**
```bash
# Verificar que WSGI está correto
cat /var/www/paulo_teste_terneiras_pythonanywhere_com_wsgi.py | head -20

# Verificar caminhos
ls -la /home/paulo_teste_terneiras/TerneirasPro/
ls -la /home/paulo_teste_terneiras/venv/bin/python

# Ver erro específico
tail -30 /var/log/paulo_teste_terneiras.pythonanywhere.com.error.log
```

### ❌ Erro: 500 Internal Server Error

**Verificar:**
```bash
# .env existe?
cat /home/paulo_teste_terneiras/TerneirasPro/.env

# Banco foi criado?
ls -la /home/paulo_teste_terneiras/TerneirasPro/db.sqlite3

# Ver erro
tail -50 /var/log/paulo_teste_terneiras.pythonanywhere.com.error.log
```

### ❌ CSS/JS não carregam (404)

**Solução:**
```bash
# Verificar que staticfiles foi criado
ls -la /home/paulo_teste_terneiras/TerneirasPro/staticfiles/ | wc -l

# Se vazio, coletar novamente
cd /home/paulo_teste_terneiras/TerneirasPro
source /home/paulo_teste_terneiras/venv/bin/activate
python manage.py collectstatic --noinput

# Fazer reload
# PythonAnywhere → Web → Reload
```

### ❌ Erro: "SECRET_KEY não definida"

**Solução:**
```bash
# Verificar .env
cat /home/paulo_teste_terneiras/TerneirasPro/.env | grep SECRET_KEY

# Se vazio, criar novo
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Atualizar .env com novo SECRET_KEY
nano /home/paulo_teste_terneiras/TerneirasPro/.env
# Adicionar: SECRET_KEY=chave_aqui

# Fazer reload
# PythonAnywhere → Web → Reload
```

---

## 8. CHECKLIST DE VALIDAÇÃO

Use este checklist para confirmar que **novo ambiente está funcionando**:

### ✅ Pré-deployment
```
[ ] Conta PythonAnywhere criada
[ ] Email verificado
[ ] Arquivos do projeto enviados
[ ] Arquivo está em ~/TerneirasPro/
```

### ✅ Ambiente
```
[ ] Venv criado: ~/venv
[ ] Venv ativado: (venv) aparece no prompt
[ ] Dependências instaladas: pip check retorna OK
[ ] .env criado com SECRET_KEY
[ ] Migrations aplicadas: showmigrations OK
[ ] Superusuário criado: admin_teste
[ ] Estáticos coletados: 40+ arquivos em staticfiles/
```

### ✅ Configuração
```
[ ] WSGI arquivo criado e salvo
[ ] Caminhos no WSGI corretos
[ ] Virtualenv mapeado: /home/[username]/venv
[ ] Static files mapeado: /static/ → staticfiles/
[ ] Reload feito
```

### ✅ Acesso
```
[ ] Site acessível: https://[novo-dominio].pythonanywhere.com
[ ] Tela de login aparece
[ ] CSS carregou (tem formatação)
[ ] JS carregou (navegação funciona)
[ ] Admin acessível: https://[novo-dominio].pythonanywhere.com/admin
```

### ✅ Funcionalidade
```
[ ] Login com admin_teste funciona
[ ] Dashboard carrega
[ ] Lista de terneiras acessível
[ ] Lista de vacas acessível
[ ] Propriedade criada com sucesso
[ ] Logout funciona
[ ] Redireciona para login após logout
```

### ✅ Banco de dados
```
[ ] db.sqlite3 criado
[ ] Propriedade "Fazenda de Testes" existe
[ ] Superusuário admin_teste criado
[ ] Tabelas criadas (migrations aplicadas)
[ ] Banco está em: ~/TerneirasPro/db.sqlite3
```

### ✅ Isolamento (Verificar que ambiente atual NÃO foi alterado)
```
[ ] Ambiente atual ainda acessível
[ ] Dados atuais não foram alterados
[ ] Novo ambiente tem domínio diferente
[ ] Novo ambiente tem conta separada
[ ] Novo ambiente tem banco separado
```

### ✅ Pronto para teste
```
[ ] Segunda pessoa consegue fazer login
[ ] Segunda pessoa consegue navegar
[ ] Segunda pessoa consegue criar registros
[ ] Segunda pessoa consegue fazer logout
[ ] Nenhum erro aparece para segunda pessoa
```

---

## 9. REFERÊNCIA RÁPIDA

### Caminhos importantes (substituir `paulo_teste_terneiras` pelo username)

```
Projeto:           /home/paulo_teste_terneiras/TerneirasPro
Venv:              /home/paulo_teste_terneiras/venv
Banco:             /home/paulo_teste_terneiras/TerneirasPro/db.sqlite3
Estáticos:         /home/paulo_teste_terneiras/TerneirasPro/staticfiles
WSGI:              /var/www/paulo_teste_terneiras_pythonanywhere_com_wsgi.py
Erro log:          /var/log/paulo_teste_terneiras.pythonanywhere.com.error.log
Access log:        /var/log/paulo_teste_terneiras.pythonanywhere.com.access.log
```

### URLs importantes

```
Site público:      https://paulo-teste-terneiras.pythonanywhere.com
Login:             https://paulo-teste-terneiras.pythonanywhere.com/accounts/login/
Admin Django:      https://paulo-teste-terneiras.pythonanywhere.com/admin
Painel PA:         https://www.pythonanywhere.com/user/paulo_teste_terneiras
```

### Comandos úteis

```bash
# Ativar venv
source ~/venv/bin/activate

# Desativar venv
deactivate

# Ver erros
tail -50 /var/log/[seu_username].pythonanywhere.com.error.log

# Fazer reload
touch /var/www/[seu_username]_pythonanywhere_com_wsgi.py

# Teste rápido
curl https://[seu_username].pythonanywhere.com -I

# Ver espaço
df -h ~

# Backup do banco
cp ~/TerneirasPro/db.sqlite3 ~/db.sqlite3.backup.$(date +%Y%m%d)
```

---

## 🎯 PRÓXIMOS PASSOS

Depois que novo ambiente está funcionando:

### 1. Segunda pessoa testa funcionalidades
- [ ] Criar propriedade
- [ ] Cadastrar vaca
- [ ] Registrar parto
- [ ] Registrar colostragem
- [ ] Ver dashboard
- [ ] Criar pesagem

### 2. Você faz backup do novo banco
```bash
scp paulo_teste_terneiras@ssh.pythonanywhere.com:~/TerneirasPro/db.sqlite3 ~/backup_novo_ambiente.sqlite3
```

### 3. Documentar feedback
- [ ] Funcionalidades que funcionaram
- [ ] Problemas encontrados
- [ ] Sugestões de melhoria
- [ ] Performance observada

---

## ✅ GARANTIA

Se você seguir **exatamente** este documento, o novo ambiente funcionará.

Se der erro:
1. Procurar em [DEPLOY_TROUBLESHOOTING.md](./DEPLOY_TROUBLESHOOTING.md)
2. Verificar seção 7 deste documento
3. Consultar PythonAnywhere Help

---

## 📝 DOCUMENTAÇÃO DE SUPORTE

- 📖 [Manual principal](./DEPLOYMENT_PYTHONANYWHERE.md) — Referência completa
- 🔧 [Troubleshooting](./DEPLOY_TROUBLESHOOTING.md) — Soluções de erros
- 🔄 [Operações](./DEPLOY_OPERACOES_PRODUCAO.md) — Manutenção
- ⚡ [Quick start](./DEPLOY_QUICK_START.md) — Resumo rápido

---

**Sucesso! Seu novo ambiente está pronto para testes. 🚀**

