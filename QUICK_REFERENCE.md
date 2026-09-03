# QUICK REFERENCE — TerneirasPro

**Cheat sheet para operações comuns.**

---

## SETUP

```bash
# Clone
git clone git@github.com:sammsuu274-art/TERNEIRASPRO.git

# Venv
python3.12 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# Config
cp .env.production.template .env

# Banco
python manage.py migrate
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1

# Admin
python manage.py createsuperuser

# Rodar
python manage.py runserver
# http://127.0.0.1:8000
```

---

## DJANGO COMMANDS

```bash
# Servidor
python manage.py runserver
python manage.py runserver 0.0.0.0:8001  # Porta diferente

# Migrações
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Shell
python manage.py shell
>>> from animais.models import Animal
>>> Animal.objects.count()

# Admin
python manage.py createsuperuser
python manage.py changepassword username

# Verificação
python manage.py check
python manage.py test indicadores

# Limpeza
python manage.py limpar_dados_teste
python manage.py flush --noinput  # Zera tudo

# Seeds
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
python manage.py seed_dados_teste
```

---

## URLs PRINCIPAIS

```
/                          Dashboard
/accounts/login/           Login
/accounts/logout/          Logout
/accounts/perfil/          Perfil do usuário

/admin/                    Django Admin
/admin-sistema/            Admin do sistema (superuser)

/animais/                  Lista terneiras
/animais/nova/             Nova terneira
/animais/<pk>/             Ficha da terneira
/animais/vacas/            Lista vacas
/animais/lotes/            Lotes

/eventos/parto/novo/<ciclo_pk>/        Registrar parto
/eventos/colostragem/<terneira_pk>/    Registrar colostragem
/eventos/umbigo/<terneira_pk>/         Registrar cura umbigo
/eventos/pesagem/<animal_pk>/          Registrar pesagem
/eventos/sanitario/<animal_pk>/        Registrar ocorrência sanitária
/eventos/vacinacao/<animal_pk>/        Registrar vacinação
/eventos/desaleitamento/<terneira_pk>/ Registrar desaleitamento

/programas/                            Lista programas
/programas/<pk>/                       Detalhe programa
/programas/<pk>/checkpoint/            Realizar checkpoint
/programas/aptas/                      Novilhas aptas

/config/protocolos/                    Protocolos
/config/metas/                         Metas de desenvolvimento
/config/criterios/                     Critérios de conformidade
/config/meta-reprodutiva/              Metas reprodutivas
```

---

## ESTRUTURA DE ARQUIVOS

```
TERNEIRAS/
├── gestao_terneiras/              # Projeto Django
│   ├── settings.py                # Configurações
│   ├── urls.py                    # URLs raiz
│   ├── wsgi.py                    # WSGI application
│   └── asgi.py                    # ASGI (async)
│
├── core/                          # App central
│   ├── models.py                  # Propriedade, Usuário
│   ├── views_admin.py             # Admin system
│   ├── views_dashboard.py         # Dashboard
│   ├── middleware.py              # Propriedade injection
│   └── urls.py, forms.py, etc.
│
├── accounts/                      # Autenticação
│   ├── models.py                  # Usuario, UsuarioPerfil
│   ├── views.py                   # Login, logout
│   └── urls.py, forms.py, etc.
│
├── animais/                       # Animais
│   ├── models.py                  # Animal, CicloReprodutivo
│   ├── views.py                   # CRUD animais
│   └── urls.py, forms.py, etc.
│
├── eventos/                       # Eventos
│   ├── models.py                  # Parto, Colostragem, etc.
│   ├── views.py                   # Registrar eventos
│   └── urls.py, forms.py, etc.
│
├── programas/                     # Programa + Checkpoint
│   ├── models.py                  # ProgramaAcompanhamento
│   ├── views.py                   # Programa + Checkpoint
│   └── urls.py, forms.py, etc.
│
├── config_tecnica/                # Configurações
│   ├── models.py                  # Protocolo, Meta, Criterio
│   ├── views.py                   # CRUD config
│   └── management/commands/       # Seeds
│
├── indicadores/                   # Conformidade
│   ├── models.py                  # ResultadoConformidade
│   ├── services.py                # Cálculos zootécnicos
│   ├── avaliadores.py             # C1-C7 evaluation
│   └── urls.py
│
├── templates/                     # HTML
│   ├── base.html                  # Layout principal
│   ├── dashboard.html
│   ├── accounts/login.html
│   └── ... (mais)
│
├── static/                        # CSS, JS, imagens
│   ├── css/
│   ├── js/
│   └── img/
│
├── .env                           # Variáveis (NÃO versionado)
├── .env.production.template       # Template seguro
├── .gitignore
├── requirements.txt               # Dependências
├── manage.py                      # CLI
├── db.sqlite3                     # Banco SQLite
├── README.md
├── DOCUMENTACAO_AGENTE.md
├── LEIA_PRIMEIRO.md
└── ... (mais docs)
```

---

## MODELOS PRINCIPAIS

```python
# Propriedade
from core.models import Propriedade
prop = Propriedade.objects.get(pk=1)
prop.nome, prop.ativa

# Animal
from animais.models import Animal
animal = Animal.objects.get(identificacao='TER001', propriedade=prop)
animal.categoria, animal.raca, animal.data_nascimento, animal.situacao

# Ciclo
from animais.models import CicloReprodutivo
ciclo = CicloReprodutivo.objects.get(vaca=animal)
ciclo.numero_lactacao, ciclo.data_secagem, ciclo.data_entrada_pre_parto

# Parto
from eventos.models import Parto
parto = Parto.objects.get(ciclo=ciclo)
parto.terneira, parto.peso_nascimento, parto.vitalidade, parto.data_parto

# Colostragem
from eventos.models import Colostragem
col = Colostragem.objects.get(terneira=parto.terneira)
col.volume_ml, col.brix_percentual, col.data_hora

# Pesagem
from eventos.models import Pesagem
pesagem = Pesagem.objects.get(animal=animal)
pesagem.peso_kg, pesagem.data

# Programa
from programas.models import ProgramaAcompanhamento
prog = ProgramaAcompanhamento.objects.get(terneira=parto.terneira)
prog.status, prog.data_inicio, prog.duracao_dias

# Conformidade
from indicadores.models import ResultadoConformidade
conf = ResultadoConformidade.objects.filter(animal=animal)
conf.resultado  # conforme, nao_conforme, dado_ausente, nao_aplicavel
```

---

## QUERIES COMUNS

```python
# Shell: python manage.py shell

# Terneiras ativas
from animais.models import Animal
terneiras = Animal.objects.filter(
    propriedade_id=1,
    categoria='terneira',
    situacao='ativa'
)

# Vacas
vacas = Animal.objects.filter(propriedade_id=1, categoria='vaca')

# Animais da propriedade
from core.models import Propriedade
prop = Propriedade.objects.get(pk=1)
prop.animal_set.all()

# Partos este mês
from eventos.models import Parto
from datetime import datetime, timedelta
this_month = Parto.objects.filter(
    propriedade_id=1,
    data_parto__gte=datetime.now().replace(day=1)
)

# Conformidades não-conformes
from indicadores.models import ResultadoConformidade
nao_conforme = ResultadoConformidade.objects.filter(
    propriedade_id=1,
    resultado='nao_conforme'
)

# Pesagens de uma terneira
animal = Animal.objects.get(identificacao='TER001', propriedade_id=1)
pesagens = animal.pesagem_set.all().order_by('data')

# Lote atual do animal
from animais.models import MovimentacaoLote
lote_atual = MovimentacaoLote.objects.filter(
    animal=animal
).order_by('-data').first()
```

---

## GIT WORKFLOW

```bash
# Status
git status

# Add + commit
git add arquivo.py
git commit -m "Descrição do commit"

# Push
git push origin main

# Pull
git pull origin main

# Branch novo
git checkout -b feature/minha-feature
git push -u origin feature/minha-feature

# Merge
git checkout main
git merge feature/minha-feature
git push origin main

# Log
git log --oneline -5
```

---

## TESTES

```bash
# Rodar todos os testes
python manage.py test

# Apenas uma app
python manage.py test indicadores

# Uma classe de teste
python manage.py test indicadores.tests.AvaliadoresTestCase

# Um teste específico
python manage.py test indicadores.tests.AvaliadoresTestCase.test_conformidade_parto

# Com verbosidade
python manage.py test indicadores --verbosity=2

# Sem migrations (mais rápido)
python manage.py test indicadores --nomigrations

# Coverage (se instalado: pip install coverage)
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera report HTML
```

---

## ADMIN DO SISTEMA

```
/admin-sistema/                    Painel admin
/admin-sistema/propriedades/       Lista propriedades
/admin-sistema/propriedades/nova/  Criar propriedade
/admin-sistema/usuarios/           Lista usuários
/admin-sistema/usuarios/novo/      Criar usuário
/admin-sistema/vinculos/           Lista vínculos
/admin-sistema/vinculos/novo/      Criar vínculo
```

**Apenas superusuários acessam.**

---

## ENVIRONMENT VARIABLES

```
# .env (desenvolvimento)
DEBUG=True
SECRET_KEY=django-insecure-dev-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# .env.production (produção)
DEBUG=False
SECRET_KEY=[GERAR_NOVA]
ALLOWED_HOSTS=terneiraspro.onrender.com
DATABASE_URL=postgresql://user:pass@host/dbname
CSRF_TRUSTED_ORIGINS=https://terneiraspro.onrender.com
```

---

## DEPLOY CHECKLIST

```
☐ Gerar nova SECRET_KEY
☐ DEBUG=False
☐ ALLOWED_HOSTS correto
☐ CSRF_TRUSTED_ORIGINS configurado
☐ DATABASE_URL PostgreSQL
☐ Migrações aplicadas
☐ Static files coletados
☐ Requirements.txt atualizado
☐ Procfile criado
☐ GitHub branch main limpo
☐ Deploy em Render ou Heroku
☐ Testar login em produção
☐ Criar animal de teste
☐ Verificar dashboard
☐ Ativar backups automáticos
```

---

## CONTATO RÁPIDO

| Aspecto | Arquivo |
|---|---|
| Começar | [`LEIA_PRIMEIRO.md`](./LEIA_PRIMEIRO.md) |
| Implementação | [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md) |
| Arquitetura | [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) |
| Deploy | [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md) |
| Bugs | [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md#14-problemas-conhecidos-e-pendências) |
| Problemas | [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) |
| Técnica | [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) |
| Usuário | [`MANUAL_DO_USUARIO.md`](./MANUAL_DO_USUARIO.md) |

---

**Última atualização:** Agosto 2026
