# TROUBLESHOOTING — TerneirasPro

**Soluções para problemas comuns durante setup, desenvolvimento e produção.**

---

## SETUP LOCAL

### Problema: "command not found: python3.12"

**Causa:** Python 3.12 não está instalado ou não está no PATH

**Solução:**
```bash
# Verificar versão disponível
python3 --version
# ou
python --version

# Se tiver 3.10+, usar:
python3 -m venv venv
# ou simplesmente
python -m venv venv
```

**Alternativa:** Instalar Python 3.12
- Linux: `sudo apt install python3.12` (Ubuntu/Debian)
- macOS: `brew install python@3.12`
- Windows: Baixar de python.org

---

### Problema: "No module named 'django'"

**Causa:** Virtual environment não ativado ou dependências não instaladas

**Solução:**
```bash
# 1. Ativar venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Verificar
python -c "import django; print(django.VERSION)"
# Deve exibir: (4, 2, 16, 'final', 0)
```

---

### Problema: "OperationalError: no such table: core_propriedade"

**Causa:** Migrações não foram aplicadas

**Solução:**
```bash
# Aplicar migrações
python manage.py migrate

# Verificar status
python manage.py showmigrations

# Se ainda não funcionar, resetar:
rm db.sqlite3
python manage.py migrate
```

---

### Problema: "Cannot connect to database at /path/to/db.sqlite3"

**Causa:** Permissões insuficientes ou arquivo corrompido

**Solução:**
```bash
# 1. Verificar permissões
ls -la db.sqlite3
# Deve ser: -rw-r--r-- (leitura/escrita para proprietário)

# 2. Resetar banco (perder dados de teste)
rm db.sqlite3
python manage.py migrate

# 3. Se ainda não funcionar, verificar diretório
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
ls -la
# Diretório deve ter permissão de escrita
```

---

### Problema: "ModuleNotFoundError: No module named 'decouple'"

**Causa:** requirements.txt não foi instalado

**Solução:**
```bash
pip install -r requirements.txt
# ou instalar manualmente:
pip install python-decouple==3.8 Django==4.2.16 Pillow==10.4.0 whitenoise==6.7.0 psycopg2-binary==2.9.9
```

---

## DESENVOLVIMENTO

### Problema: "SyntaxError" em um arquivo .py

**Causa:** Erro de sintaxe Python

**Solução:**
```bash
# 1. Verificar arquivo
python -m py_compile seu_arquivo.py

# 2. Achar linha exata do erro
python seu_arquivo.py

# 3. Usar linter (se instalado)
flake8 seu_arquivo.py
```

---

### Problema: Página em branco ao acessar http://127.0.0.1:8000

**Causa:** Erro não exibido (DEBUG=False em desenvolvimento ou erro silencioso)

**Solução:**
```bash
# 1. Verificar DEBUG no .env
cat .env | grep DEBUG
# Deve ser: DEBUG=True

# 2. Se estiver False, mudar para True
echo "DEBUG=True" >> .env

# 3. Reiniciar servidor
python manage.py runserver

# 4. Verificar console para erro
# Terminal mostrará traceback completo
```

---

### Problema: 404 em /admin ou outras URLs

**Causa:** URL não mapeada ou app não instalado

**Solução:**
```bash
# 1. Verificar INSTALLED_APPS em settings.py
grep -A 10 "INSTALLED_APPS" gestao_terneiras/settings.py

# 2. Se app ausente, adicionar:
# gestao_terneiras/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'core',  # Verificar se está
    'accounts',
    'animais',
    # ...
]

# 3. Reiniciar servidor
python manage.py runserver
```

---

### Problema: "csrf_token missing" — formulário não funciona

**Causa:** Token CSRF não inserido no template

**Solução:**
```html
<!-- Adicionar no topo do formulário: -->
<form method="post">
    {% csrf_token %}  <!-- NECESSÁRIO -->
    <!-- resto do formulário -->
</form>
```

---

### Problema: Gráfico não renderiza (Chart.js branco)

**Causa:** JavaScript error ou dados inválidos

**Solução:**
```bash
# 1. Abrir console do navegador (F12)
# Procurar por erros JavaScript

# 2. Verificar se Chart.js está carregando
# Deve haver <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/...">

# 3. Verificar dados do gráfico
# No console: console.log(chartData)
# Deve exibir array de objetos com labels e data

# 4. Se dados vazios, verificar view
# core/views_dashboard.py → _buscar_dados_graficos()
```

---

### Problema: "IntegrityError: UNIQUE constraint failed"

**Causa:** Tentativa de criar registro com identificador duplicado

**Solução:**
```bash
# 1. Verificar dados existentes
python manage.py shell
>>> from animais.models import Animal
>>> Animal.objects.filter(propriedade_id=1, identificacao='DUPLICADO').count()

# 2. Se encontrou duplicata, deletar uma
>>> Animal.objects.filter(identificacao='DUPLICADO').delete()

# 3. Ou usar identificador diferente
```

---

## BANCO DE DADOS

### Problema: "ProgrammingError: column ... does not exist"

**Causa:** Modelo foi alterado mas migration não foi criada

**Solução:**
```bash
# 1. Criar migration
python manage.py makemigrations

# 2. Aplicar
python manage.py migrate

# 3. Se erro persistir, resetar:
python manage.py migrate animais zero  # Remove todas as migrations dessa app
python manage.py makemigrations animais
python manage.py migrate animais
```

---

### Problema: Banco sqlite3 crescendo muito de tamanho

**Causa:** Dados acumulados, WAL files

**Solução:**
```bash
# 1. Limpar dados de teste
python manage.py limpar_dados_teste

# 2. Ou resetar banco completo
rm db.sqlite3
python manage.py migrate

# 3. Verificar tamanho
du -sh db.sqlite3

# 4. Se WAL files crescerem:
# (Linux) rm db.sqlite3-wal db.sqlite3-shm
```

---

## SEGURANÇA

### Problema: "SECRET_KEY inseguro" em produção

**Causa:** Usando valor padrão `django-insecure-...`

**Solução:**
```bash
# 1. Gerar chave nova
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Copiar output (ex: z6#_7$@!vx9wnk2m4...)

# 3. Adicionar a .env.production:
echo "SECRET_KEY=z6#_7$@!vx9wnk2m4..." >> .env.production

# 4. Verificar
cat .env.production | grep SECRET_KEY
```

---

### Problema: "403 Forbidden — CSRF token missing or incorrect"

**Causa:** Token CSRF inválido ou domínio não confiável

**Solução:**
```python
# gestao_terneiras/settings.py — produção
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

# .env.production
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
```

---

### Problema: "Permission denied" — acesso negado a app

**Causa:** Usuário não tem vínculo com propriedade ativa

**Solução:**
```bash
# 1. Via Django shell
python manage.py shell
>>> from accounts.models import Usuario, UsuarioPerfil
>>> from core.models import Propriedade
>>> usuario = Usuario.objects.get(username='seu_usuario')
>>> propriedade = Propriedade.objects.get(pk=1)
>>> UsuarioPerfil.objects.create(
...     usuario=usuario,
...     propriedade=propriedade,
...     papel='tecnico',
...     ativo=True
... )

# 2. Ou via admin: /admin-sistema/vinculos/novo/
```

---

## PRODUÇÃO (RENDER.COM)

### Problema: 500 Error — "Internal Server Error"

**Causa:** Muitas possibilidades (log detalhará)

**Solução:**
```bash
# 1. Verificar logs no Render dashboard
# https://dashboard.render.com → Logs

# 2. Comum: falta de variável de ambiente
# Render Settings → Environment Variables
# Verificar: SECRET_KEY, DEBUG, DATABASE_URL, ALLOWED_HOSTS

# 3. Database não conecta
# Verificar: DATABASE_URL está correto
psql "postgresql://user:pass@host/db" -c "SELECT 1"

# 4. Static files não carregam
# Render → Build command
# Verificar se inclui: python manage.py collectstatic --noinput
```

---

### Problema: 404 em static files (CSS, JS, imagens)

**Causa:** collectstatic não executado ou WhiteNoise não configurado

**Solução:**
```bash
# 1. Verificar build command no Render:
# pip install -r requirements.txt && python manage.py collectstatic --noinput

# 2. Verificar settings.py
grep -A 5 "STATIC_URL" gestao_terneiras/settings.py

# 3. Executar localmente para testar
python manage.py collectstatic --clear --noinput

# 4. Fazer novo deploy (Render)
git push origin main  # Trigger automático no Render
```

---

### Problema: Database connection timeout

**Causa:** PostgreSQL não está acessível

**Solução:**
```bash
# 1. Verificar DATABASE_URL no Render
# Render Dashboard → Environment

# 2. Testar conexão
psql "postgresql://user:pass@host/dbname" -c "SELECT 1"

# 3. Se falhar, verificar:
# - Firewall (Render libera automaticamente)
# - Database em "sleeping" state (upgrade plan)
# - Password com caracteres especiais (URL encode)

# 4. Fazer novo migration
python manage.py migrate --noinput
```

---

### Problema: Render app dorme e demora para acordar

**Causa:** Plano gratuito Render (Spin Down em 15min sem atividade)

**Solução:**
```bash
# 1. Upgrade para Starter Plan (pago)
# ou

# 2. Usar PagerDuty/Uptime Robot
# Ping app a cada 5 minutos para manter acordado

# 3. Configurar cron job (se houver suporte)
# Render nativo não tem cron, usar:
# - EasyCron.com
# - Cloudflare Workers
```

---

## CLOUDFLARE TUNNEL (Futuro)

### Problema: Tunnel offline

**Causa:** Cloudflared não rodando ou credenciais inválidas

**Solução:**
```bash
# 1. Verificar status
cloudflared tunnel list

# 2. Se offline, reconectar
cloudflared tunnel login
cloudflared tunnel create terneiras
cloudflared tunnel route dns terneiras seu-dominio.com

# 3. Iniciar tunnel
cloudflared tunnel run terneiras

# 4. Setup systemd (permanente)
# Ver: GUIA_IMPLEMENTACAO_PARA_EQUIPE.md
```

---

## PERFORMANCE

### Problema: Dashboard carrega lentamente (>5s)

**Causa:** N+1 queries, muitos animais, gráficos pesados

**Solução:**
```python
# core/views_dashboard.py — otimizar queries
# Adicionar select_related() e prefetch_related()

from django.db.models import Prefetch

animais = Animal.objects.filter(
    propriedade=propriedade,
    situacao='ativa'
).select_related(
    'mae'  # ForeignKey
).prefetch_related(
    'pesagem_set',  # Reverse FK
)
```

---

### Problema: Database lento (queries demoram)

**Causa:** Falta de índices, queries não otimizadas

**Solução:**
```python
# Adicionar índices em models
class Animal(models.Model):
    propriedade = ForeignKey(...)
    identificacao = CharField()
    categoria = CharField()
    
    class Meta:
        indexes = [
            models.Index(fields=['propriedade', 'categoria']),
            models.Index(fields=['identificacao']),
        ]
```

---

## DEBUG

### Problema: Não consigo listar queries executadas

**Causa:** django-debug-toolbar não instalado (opcional)

**Solução:**
```bash
# 1. Instalar debug toolbar
pip install django-debug-toolbar

# 2. Adicionar a settings.py (dev apenas)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# 3. Adicionar a urls.py
if DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# 4. Recarregar — aparecerá barra lateral no navegador
```

---

### Problema: Quero logar em arquivo

**Causa:** Logs não configurados

**Solução:**
```python
# gestao_terneiras/settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Criar diretório
mkdir -p logs
```

---

## SUPORTE

Se nenhuma solução acima funcionar:

1. **Verificar documentação:**
   - [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md)
   - [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md)

2. **Verificar GitHub Issues:**
   - https://github.com/sammsuu274-art/TERNEIRASPRO/issues

3. **Django Official Docs:**
   - https://docs.djangoproject.com/en/4.2/

4. **Stack Overflow:**
   - Tag: `django` `python` `postgres`

---

**Última atualização:** Agosto 2026  
**Versão:** 1.0
