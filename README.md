# TerneirasPro — Sistema de Gestão Técnica da Cria e Recria

**Rastreie o desenvolvimento de terneiras (fêmeas bovinas jovens) com conformidade técnica automática.**

[![Status](https://img.shields.io/badge/status-75%25%20pronto-yellow)](./AUDITORIA_PRODUCAO.md)
[![Django](https://img.shields.io/badge/Django-4.2.16-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-gray)](#licença)

---

## 📋 O que é TerneirasPro?

**TerneirasPro** é um sistema web que rastreia o desenvolvimento de terneiras desde o pré-parto da mãe até a primeira inseminação (IA) da novilha, com **conformidade técnica automática** contra 7 critérios baseados em literatura zootécnica (Embrapa).

### Recursos Principais

✅ **Multi-tenant** — Múltiplas propriedades em uma instalação  
✅ **Eventos zootécnicos** — Parto, colostragem, pesagem, vacinação, desaleitamento  
✅ **Conformidade automática** — 7 critérios técnicos (C1–C7) avaliados em tempo real  
✅ **Dashboard inteligente** — 3 zonas (alertas, status, tendência) + 4 gráficos Chart.js  
✅ **Cálculos zootécnicos** — GMD, interpolação de curvas, projeções reprodutivas  
✅ **Histórico imutável** — Rastreabilidade completa de todos os eventos  

### O que NÃO é

❌ Sistema financeiro  
❌ Produção de leite (CCS individual)  
❌ Reprodução de vacas adultas  
❌ ERP ou estoque  

---

## 🚀 Quick Start

### 1. Clone o Repositório

```bash
git clone git@github.com:sammsuu274-art/TERNEIRASPRO.git
cd TERNEIRASPRO
```

### 2. Setup Local

```bash
# Criar virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar configuração
cp .env.production.template .env

# Aplicar migrações
python manage.py migrate

# Carregar dados de referência
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1

# Criar usuário admin
python manage.py createsuperuser
# Use: admin / admin123

# Iniciar servidor
python manage.py runserver
```

### 3. Acesso

- **URL:** http://127.0.0.1:8000
- **Login:** admin / admin123
- **Admin Django:** http://127.0.0.1:8000/admin

---

## 📚 Documentação

**👉 Comece por:** [`LEIA_PRIMEIRO.md`](./LEIA_PRIMEIRO.md) — Seu guia de navegação

### Para Desenvolvedores
- [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md) — Setup, bugs prioritários, testes, deploy
- [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) — Arquitetura, modelos, funcionalidades (FONTE OFICIAL)
- [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md) — Checklist pré-deploy, segurança

### Referência Técnica
- [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) — Especificação completa, decisões pendentes
- [`IMPLEMENTACAO_LOGIN.md`](./IMPLEMENTACAO_LOGIN.md) — Design da tela de login
- [`TELA_LOGIN_LAYOUT.md`](./TELA_LOGIN_LAYOUT.md) — CSS e medidas aprovadas

### Para Usuários
- [`MANUAL_DO_USUARIO.md`](./MANUAL_DO_USUARIO.md) — Como usar o sistema
- [`CHANGELOG.md`](./CHANGELOG.md) — Histórico de alterações

---

## 🛠️ Stack Tecnológico

```
Backend:     Python 3.12 + Django 4.2.16
Frontend:    Bootstrap 5.3 + Alpine.js 3 + HTMX 1.9 + Chart.js 4
Banco:       SQLite (dev) | PostgreSQL (prod)
Deploy:      Render.com
Versionamento: GitHub (git@github.com:sammsuu274-art/TERNEIRASPRO.git)
```

### Dependências Principais

```
Django==4.2.16          # Framework web
python-decouple==3.8    # Variáveis de ambiente
Pillow==10.4.0          # Processamento de imagens
whitenoise==6.7.0       # Servir static files
psycopg2-binary==2.9.9  # Driver PostgreSQL
```

---

## 📊 Status do Projeto

| Aspecto | Status | Detalhes |
|---|---|---|
| **Código** | ✅ 100% | 179 arquivos, funcionando |
| **GitHub** | ✅ 100% | Repositório privado pronto |
| **Funcionalidades** | ✅ 75% | 35/47 totalmente implementadas |
| **Segurança** | ⚠️ 60% | Bugs críticos documentados |
| **Produção** | ⚠️ 30% | Ready with corrections |

**Bugs Críticos:** 2 (SECRET_KEY insegura, papéis não verificados)  
**Bugs Altos:** 4 (meta_volume, C8-C10, movimentação lotes, recálculo)  
**Tempo até Produção:** 2-3 semanas  

Veja [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md) para detalhes.

---

## 🚀 Deploy

### Desenvolvimento Local

```bash
python manage.py runserver
# http://127.0.0.1:8000
```

### Produção no Render.com

1. Conectar GitHub ao Render
2. Criar Web Service (build + start commands)
3. Criar PostgreSQL Database
4. Configurar environment variables
5. Deploy automático em cada push a `main`

Veja [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md) — Seção 5 para passos detalhados.

---

## 🔧 Comandos Django Úteis

```bash
# Migrações
python manage.py migrate
python manage.py makemigrations

# Seeds de dados
python manage.py seed_referenciais           # 9 referenciais técnicos
python manage.py seed_criterios --propriedade 1  # Critérios C1-C7

# Usuários
python manage.py createsuperuser

# Verificação
python manage.py check
python manage.py showmigrations

# Limpeza
python manage.py limpar_dados_teste

# Tests (quando implementados)
python manage.py test indicadores --verbosity=2
```

---

## 📁 Estrutura do Projeto

```
TERNEIRAS/
├── gestao_terneiras/      # Projeto Django (settings, urls, wsgi)
├── core/                  # Propriedade, Admin, Dashboard
├── accounts/              # Usuários, Autenticação
├── animais/               # Animais, Ciclos reprodutivos
├── eventos/               # Parto, Colostragem, Pesagem, etc
├── programas/             # Programa, Checkpoint, Projeção
├── config_tecnica/        # Protocolos, Metas, Critérios
├── indicadores/           # Conformidade, Cálculos zootécnicos
├── templates/             # HTML (Bootstrap 5)
├── static/                # CSS, JS, Imagens
├── requirements.txt       # Dependências Python
├── manage.py              # CLI Django
├── README.md              # Este arquivo
├── LEIA_PRIMEIRO.md       # Guia de navegação
├── DOCUMENTACAO_AGENTE.md # Especificação técnica completa
└── ... (mais documentação)
```

---

## 🐛 Problemas Conhecidos

### 🔴 Críticos
1. **SECRET_KEY insegura** — Usar padrão `django-insecure-...`
2. **Sistema de papéis não funcional** — Views não verificam papel

### 🟠 Altos
3. **Template form_colostragem** — Variável `meta_volume` não passada
4. **Critérios C8-C10** — Desaleitamento sem avaliadores
5. **MovimentacaoLote** — Modelo pronto, sem UI

### 🟡 Médios
6. Metas dos gráficos hardcoded
7. ProtocoloAlimentar sem interface

Veja [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md) para detalhes e soluções.

---

## ✅ Funcionalidades Implementadas

- ✅ Gestão de propriedades (multi-tenant)
- ✅ Autenticação e usuários
- ✅ CRUD de animais (vacas, terneiras, bezerros)
- ✅ Ciclo reprodutivo
- ✅ Registro de eventos (parto, colostragem, pesagem, etc)
- ✅ Conformidade automática (C1–C7)
- ✅ Dashboard com alertas e gráficos
- ✅ Programa de acompanhamento (6 meses)
- ✅ Checkpoint com projeção
- ✅ Primeiro acesso automático
- ✅ Admin do sistema

Veja [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) para lista completa.

---

## 📞 Suporte

### Dúvidas Técnicas?
- Documentação: [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md)
- Regras: [`.kiro/steering/projeto.md`](./.kiro/steering/projeto.md)
- Issues: GitHub issues do repositório

### Precisa Implementar?
- Guia: [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md)
- Bugs prioritários com código pronto

### Vai fazer Deploy?
- Checklist: [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md)
- Render.com: Veja seção Deploy acima

---

## 📄 Licença

MIT — Use, modifique e distribua livremente.

---

## 👥 Autores

Desenvolvido por equipe de Desenvolvimento — TerneirasPro Team

---

## 🙏 Agradecimentos

- Embrapa — Referenciais técnicos
- Django — Framework excelente
- Bootstrap — UI components
- Comunidade open source

---

**Última atualização:** Agosto 2026  
**Versão:** 1.0  
**Status:** Pronto para Implementação

👉 **Comece por:** [`LEIA_PRIMEIRO.md`](./LEIA_PRIMEIRO.md)
