# 📋 LEIA PRIMEIRO — Documentação TerneirasPro

Bem-vindo ao projeto **TerneirasPro**! Este arquivo te orienta por toda a documentação.

---

## 🎯 Você é um Desenvolvedor?

Se você vai implementar melhorias ou corrigir bugs, siga esta ordem:

1. **Comece aqui:** [`GUIA_IMPLEMENTACAO_PARA_EQUIPE.md`](./GUIA_IMPLEMENTACAO_PARA_EQUIPE.md)
   - Setup local (venv, dependências, banco)
   - 5 bugs prioritários com código
   - Testes
   - Deploy

2. **Documentação técnica:** [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md)
   - Arquitetura do sistema
   - Modelos de dados
   - Todas as 47 funcionalidades
   - Stack tecnológico
   - Decisões de design
   - Estado atual e pendências

3. **Checklist pré-deploy:** [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md)
   - Segurança (SECRET_KEY, headers, SSL)
   - Banco de dados (PostgreSQL setup)
   - Static files
   - Dependências
   - Deploy no Render.com

4. **Referência técnica completa:** [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md)
   - Estado atual do desenvolvimento
   - Funcionalidades implementadas vs. pendentes
   - 10 decisões pendentes
   - Problemas conhecidos

---

## 📱 Você é um Usuário Final?

Se você vai **usar** o sistema:

1. Comece com: [`MANUAL_DO_USUARIO.md`](./MANUAL_DO_USUARIO.md)
   - Como fazer login
   - Fluxo operacional (registrar terneira, parto, eventos)
   - Dashboard e alertas
   - Conformidades

---

## 🏗️ Você é um Arquiteto / Product Owner?

Se você vai tomar decisões sobre o projeto:

1. **Visão geral:** [`README.md`](./README.md)
   - Objetivo do projeto
   - Quick start
   - Stack

2. **Estado atual:** [`AUDITORIA_PRODUCAO.md`](./AUDITORIA_PRODUCAO.md)
   - 75% pronto para produção
   - 5 bloqueadores críticos
   - Timeline estimada

3. **Decisões pendentes:** [`DOCUMENTACAO_AGENTE.md`](./DOCUMENTACAO_AGENTE.md) — Seção 19
   - Sistema de papéis (não implementado)
   - Recálculo após edição (não definido)
   - Funcionalidades parciais

4. **Changelog:** [`CHANGELOG.md`](./CHANGELOG.md)
   - Histórico de alterações
   - Versões

---

## 📚 Estrutura de Documentação

```
LEIA_PRIMEIRO.md                          ← Você está aqui
│
├── Para Desenvolvedores:
│   ├── GUIA_IMPLEMENTACAO_PARA_EQUIPE.md  (START HERE)
│   ├── DOCUMENTACAO_AGENTE.md             (REFERÊNCIA TÉCNICA COMPLETA)
│   ├── AUDITORIA_PRODUCAO.md              (CHECKLIST PRÉ-DEPLOY)
│   └── TROUBLESHOOTING.md                 (SOLUÇÕES)
│
├── Para Usuários:
│   └── MANUAL_DO_USUARIO.md               (COMO USAR)
│
├── Para Arquitetos:
│   ├── README.md                          (VISÃO GERAL)
│   ├── AUDITORIA_PRODUCAO.md              (ESTADO ATUAL)
│   ├── DOCUMENTACAO_AGENTE.md             (DECISÕES PENDENTES)
│   └── CHANGELOG.md                       (HISTÓRICO)
│
├── Design:
│   ├── IMPLEMENTACAO_LOGIN.md             (TELA DE LOGIN)
│   ├── TELA_LOGIN_LAYOUT.md               (CSS DA LOGIN)
│   └── SIMPLIFICACAO_DADOS.md             (FORMULÁRIOS)
│
├── Deploy (Histórico — redundante, descontinuado):
│   └── DEPLOY_TROUBLESHOOTING.md         (Problemas deployment legado)
│
└── Código:
    ├── gestao_terneiras/                  (Settings, URLs, WSGI)
    ├── core/                              (Propriedade, Admin, Dashboard)
    ├── accounts/                          (Usuários, Login)
    ├── animais/                           (Animais, Ciclos)
    ├── eventos/                           (Parto, Pesagem, etc)
    ├── programas/                         (Programa, Checkpoint)
    ├── config_tecnica/                    (Protocolos, Metas, Critérios)
    ├── indicadores/                       (Conformidade, Cálculos)
    ├── templates/                         (HTML + Bootstrap 5)
    ├── static/                            (CSS, JS, Imagens)
    └── requirements.txt                   (Dependências)
```

---

## ⚡ Começo Rápido (Todos)

```bash
# 1. Clone
git clone git@github.com:sammsuu274-art/TERNEIRASPRO.git
cd TERNEIRASPRO

# 2. Setup
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Banco
cp .env.production.template .env
python manage.py migrate
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
python manage.py createsuperuser

# 4. Rodar
python manage.py runserver
# Acesso: http://127.0.0.1:8000
# Login: admin / admin123
```

---

## 🔴 Status Atual (Agosto 2026)

| Aspecto | Status | Notas |
|---|---|---|
| **Código** | ✅ 100% | 179 arquivos, funcionando |
| **GitHub** | ✅ 100% | Repositório privado pronto |
| **Funcionalidades** | ✅ 75% | 35/47 totalmente implementadas |
| **Segurança** | ⚠️ 60% | SECRET_KEY insegura, papéis não verificados |
| **Testes** | ❌ 10% | Testes unitários ausentes |
| **Produção** | ⚠️ 30% | Ready for deployment com correções |

---

## 🚀 Próximos Passos

### Curto Prazo (2-3 horas)
1. ✅ Corrigir `form_colostragem.html` (meta_volume)
2. ✅ Implementar permission_required decorator
3. ✅ Gerar nova SECRET_KEY
4. ✅ Implementar avaliadores C8-C10

### Médio Prazo (1 semana)
5. ✅ Adicionar testes unitários
6. ✅ Remover hardcoded em gráficos
7. ✅ Deploy em Render.com

### Longo Prazo (backlog)
8. Implementar MovimentacaoLote UI
9. Remover ou implementar ProtocoloAlimentar
10. Adicionar validações técnicas

---

## 🔧 Tecnologias

```
Backend:    Python 3.12 + Django 4.2.16
Frontend:   Bootstrap 5.3 + Alpine.js 3 + HTMX 1.9 + Chart.js 4
Banco:      SQLite (dev) | PostgreSQL (prod)
Deploy:     Render.com
Versionamento: GitHub
```

---

## 📖 Documentos Principais

| Arquivo | Público | Tamanho | Tempo de Leitura |
|---|---|---|---|
| DOCUMENTACAO_AGENTE.md | Tech | ~75 KB | 60 min | Fonte oficial — Especificação técnica completa |
| AUDITORIA_PRODUCAO.md | Dev/Ops | ~25 KB | 25 min |
| MANUAL_DO_USUARIO.md | User | ~15 KB | 15 min |

---

## ❓ FAQ

### Qual é o objetivo do sistema?
Rastrear desenvolvimento de terneiras (fêmeas jovens bovinas) do pré-parto até primeira IA, com conformidade técnica automática.

### Quantas funcionalidades estão prontas?
35 de 47 (75%). Veja `DOCUMENTACAO_AGENTE.md` para lista completa.

### Quanto tempo até produção?
2-3 semanas (considerando correções críticas + testes + deploy).

### O sistema roda em qual servidor?
Render.com (recomendado), ou Heroku, PythonAnywhere, AWS, etc.

### E o Cloudflare Tunnel?
Instalado mas não configurado. Será usado depois do Render estar online.

### Posso modificar o design da login?
Veja `TELA_LOGIN_LAYOUT.md` — design foi aprovado, alterações requerem justificativa.

### Onde está o banco de dados em produção?
PostgreSQL em Neon ou Supabase (gratuito), configurável em `.env`.

---

## 📞 Suporte

**Documentação técnica:** `DOCUMENTACAO_AGENTE.md`  
**Regras do projeto:** `.kiro/steering/projeto.md`  
**Issues:** GitHub issues do repositório  
**Emergência:** Consulte `TROUBLESHOOTING.md` (após deployment)

---

## 🎓 Roteiros Recomendados

### Cenário: "Quero correções rápidas"
1. `GUIA_IMPLEMENTACAO_PARA_EQUIPE.md` — seção 2 (bugs)
2. Implementar 5 bugs prioritários (2-3 horas)
3. Commit + push
4. Pronto!

### Cenário: "Quero entender tudo"
1. `DOCUMENTACAO_AGENTE.md` — visão geral
2. `ESPECIFICACAO_TECNICA_COMPLETA.md` — arquitetura
3. `GUIA_IMPLEMENTACAO_PARA_EQUIPE.md` — implementation details
4. Código-fonte (django apps)

### Cenário: "Quero fazer deploy"
1. `AUDITORIA_PRODUCAO.md` — checklist completo
2. `GUIA_IMPLEMENTACAO_PARA_EQUIPE.md` — seção 5 (deployment)
3. Seguir passos de deploy no Render

---

## 📋 Checklist de Onboarding

- [ ] Li `LEIA_PRIMEIRO.md` (você está aqui!)
- [ ] Identifiquei meu papel (dev / user / arquiteto)
- [ ] Li documentação relevante para meu papel
- [ ] Clonei repositório localmente
- [ ] Setup funcionando (venv + manage.py runserver)
- [ ] Consegui fazer login (admin / admin123)
- [ ] Criei primeiro animal de teste
- [ ] Entendi fluxo: animal → parto → programa → checkpoint

---

**Bem-vindo ao TerneirasPro! 🐄**

Qualquer dúvida, comece pela documentação relevante acima.

---

*Última atualização: Agosto 2026*  
*Versão: 1.0*
