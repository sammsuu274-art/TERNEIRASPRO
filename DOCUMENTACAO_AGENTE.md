# Documentação do Projeto — TerneirasPro
> **Para agentes de IA:** leia este arquivo antes de qualquer ação no projeto.  
> Última atualização: Agosto 2026

---

## 1. IDENTIDADE DO PROJETO

**Nome:** TerneirasPro  
**Finalidade:** Sistema web de gestão técnica da cria e recria de fêmeas bovinas leiteiras.  
**Não é:** sistema financeiro, ERP, produção de leite, reprodução de vacas adultas.  
**Foco:** Acompanhar a fêmea do pré-parto da mãe até a primeira inseminação, com checkpoint aos 6 meses.

**Diretório raiz:**
```
/home/victor/Documentos/victor/Documentos/TERNEIRAS/
```

---

## 2. STACK TÉCNICA

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django 4.2.16 |
| Banco (dev) | SQLite (`db.sqlite3` na raiz) |
| Banco (prod) | PostgreSQL — Neon ou Supabase (gratuito) |
| Frontend | Bootstrap 5.3 + Alpine.js 3 + HTMX 1.9 + Chart.js 4 |
| Estáticos | Whitenoise |
| Virtualenv | `venv/` na raiz |
| Config | `python-decouple` lendo `.env` |

**Rodar o servidor:**
```bash
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
source venv/bin/activate
python manage.py runserver
```

**Acesso:**
- URL: `http://127.0.0.1:8000`
- Login padrão: `admin` / `admin123`
- Admin Django: `http://127.0.0.1:8000/admin`

**requirements.txt atual:**
```
Django==4.2.16
python-decouple==3.8
Pillow==10.4.0
whitenoise==6.7.0
psycopg2-binary==2.9.9
```

---

## 3. ESTADO ATUAL DO BANCO

```
Propriedades: Fazenda Rodrigues (ID=1, ativa=True)
Usuários: admin (superuser)
Vínculos: admin → Fazenda Rodrigues (papel=admin)
Referenciais: 9 carregados (Embrapa + literatura)
Critérios de conformidade: criados via seed_criterios
```

---

## 4. ESTRUTURA DE APPS

```
gestao_terneiras/   ← settings, urls raiz
core/               ← Propriedade, middleware, dashboard, admin do sistema
accounts/           ← Usuario, UsuarioPerfil, login/logout
animais/            ← Animal, Lote, MovimentacaoLote, CicloReprodutivo
eventos/            ← Parto, Colostragem, CuraUmbigo, Pesagem, OcorrenciaSanitaria,
                       Vacinacao, ProtocoloAlimentar, RegistroAlimentacaoDiario,
                       Desaleitamento, BancoColostro
programas/          ← ProgramaAcompanhamento, CheckpointSesMeses,
                       ProjecaoReprodutiva, CoberturaIA
config_tecnica/     ← Protocolo, MetaDesenvolvimento, PontoMetaDesenvolvimento,
                       MetaReprodutiva, ReferencialTecnico, CriterioConformidade
indicadores/        ← ResultadoConformidade + services.py + avaliadores.py
```

**Regra crítica:** `indicadores/` tem modelos (`ResultadoConformidade`) MAS NÃO tem views nem URLs. É consumido pelas outras apps.

---

## 5. MULTI-TENANCY

O sistema suporta múltiplas fazendas por instalação.

**Como funciona:**
1. `core.middleware.PropriedadeMiddleware` injeta `request.propriedade_ativa` em cada requisição.
2. Propriedade ativa fica em `request.session['propriedade_ativa_id']`.
3. **Superusuário** acessa qualquer propriedade ativa — se não houver nenhuma na sessão, pega a primeira existente.
4. **Usuário comum** precisa de `UsuarioPerfil` vinculando-o a uma propriedade.
5. `request.is_master = True` para superusuários (injetado pelo middleware).
6. `core.context_processors.propriedade_ativa` disponibiliza `propriedade_ativa` e `propriedades_usuario` em todos os templates.

**Papéis disponíveis:** `admin`, `tecnico`, `produtor`, `auxiliar`

**IMPORTANTE:** Papéis existem no modelo mas NÃO são verificados funcionalmente. Todas as views usam apenas `@login_required`. Qualquer usuário autenticado tem acesso total a todas as funcionalidades da propriedade.

---

## 6. PRIMEIRO ACESSO E ADMINISTRAÇÃO DO SISTEMA

### Fluxo de primeiro acesso (banco vazio)
1. Login com superusuário → sem propriedade ativa → redireciona para `/primeiro-acesso/`
2. Formulário cria a fazenda com `ativa=True` garantido no código (não depende do form)
3. Superusuário é vinculado automaticamente como admin
4. Redireciona para o dashboard

### Painel de administração (`/admin-sistema/`)
Visível apenas para superusuários. Acessível pela sidebar (seção "Administração" em vermelho).

| URL | Função |
|---|---|
| `/admin-sistema/` | Painel geral + troca rápida de propriedade ativa |
| `/admin-sistema/propriedades/` | Lista de todas as propriedades |
| `/admin-sistema/propriedades/nova/` | Criar nova fazenda |
| `/admin-sistema/propriedades/<pk>/editar/` | Editar fazenda (inclui campo `ativa`) |
| `/admin-sistema/propriedades/<pk>/selecionar/` | POST — troca propriedade ativa |
| `/admin-sistema/usuarios/` | Lista de usuários |
| `/admin-sistema/usuarios/novo/` | Criar novo usuário (login + senha) |
| `/admin-sistema/usuarios/<pk>/editar/` | Editar usuário (inclui reset de senha) |
| `/admin-sistema/vinculos/` | Lista de vínculos usuário ↔ propriedade |
| `/admin-sistema/vinculos/novo/` | Criar vínculo |
| `/admin-sistema/vinculos/<pk>/remover/` | POST — remover vínculo |

### Arquivos do admin do sistema
```
core/views_admin.py     ← todas as views do painel admin
core/forms.py           ← PropriedadeForm, PropriedadeEditForm, NovoUsuarioForm,
                           EditarUsuarioForm, VinculoForm
templates/admin_sistema/
  primeiro_acesso.html
  painel_admin.html
  lista_propriedades.html / form_propriedade.html
  lista_usuarios.html / form_usuario.html
  lista_vinculos.html / form_vinculo.html
```

**IMPORTANTE:** `PropriedadeForm` NÃO tem campo `ativa` (para criação). `PropriedadeEditForm` TEM o campo `ativa` (para edição). Isso evita o bug de criar fazenda inativa.

---

## 7. MODELO DE DADOS — ENTIDADES PRINCIPAIS

```
Propriedade
  ├── Animal (vaca, terneira, novilha, bezerro)
  │     ├── CicloReprodutivo → Parto (OneToOne)
  │     ├── Pesagem (N)
  │     ├── OcorrenciaSanitaria (N)
  │     ├── Vacinacao (N)
  │     ├── Colostragem (N — apenas terneiras)
  │     ├── CuraUmbigo (N)
  │     ├── ProtocoloAlimentar (N)
  │     ├── RegistroAlimentacaoDiario (N, opcional)
  │     └── Desaleitamento (OneToOne)
  ├── BancoColostro
  ├── Lote (via MovimentacaoLote — nunca campo direto no Animal)
  ├── Protocolo (versionado)
  ├── MetaDesenvolvimento + PontoMetaDesenvolvimento
  ├── MetaReprodutiva
  ├── ReferencialTecnico
  └── CriterioConformidade

Terneira
  └── ProgramaAcompanhamento (criado automaticamente no parto)
        └── CheckpointSesMeses
              └── ProjecaoReprodutiva (recalculada a cada pesagem)

ResultadoConformidade (imutável — gerado pelos avaliadores)
  ├── animal
  ├── criterio (FK → CriterioConformidade) ou meta_desenvolvimento
  ├── evento_tipo + evento_id
  ├── valor_observado, valor_referencia, desvio
  └── resultado: conforme / nao_conforme / dado_ausente / nao_aplicavel
```

### Comportamentos automáticos

| Evento | Efeito automático | Quando dispara |
|---|---|---|
| Registrar Parto | Cria Animal (terneira/bezerro) | Sempre ao salvar parto |
| Registrar Parto (fêmea) | Cria ProgramaAcompanhamento | Apenas se sexo='F' |
| Registrar Parto | Atualiza `ciclo.situacao='encerrado_parto'` | Sempre ao salvar parto |
| Registrar Parto | Avalia C5 (dias secos) e C6 (dias pré-parto) | Após salvar, via `avaliar_evento_parto()` |
| Registrar Colostragem | Avalia C1, C2, C3 | Após salvar, via `avaliar_evento_colostragem()` |
| Registrar CuraUmbigo | Avalia C4 (tempo) | Após salvar, via `avaliar_evento_cura_umbigo()` |
| Registrar Pesagem | Avalia C7 (peso/idade) | Após salvar, via `avaliar_evento_pesagem()` |
| Registrar Desaleitamento | `animal.categoria` → `novilha` | Sempre ao salvar desaleitamento |
| Registrar CoberturaIA | `animal.categoria` → `vaca` | Sempre ao salvar IA |
| Realizar Checkpoint | `programa.status` → `encerrado` | Sempre ao salvar checkpoint |
| Cadastrar terneira manual | Cria ProgramaAcompanhamento | Apenas se `data_nascimento` existe |

### Regras de dados

- **Dado ausente ≠ zero.** `null=True` significa "não informado". Nunca trate `None` como `0` em cálculos.
- **Lote atual** = derivado da última `MovimentacaoLote` (ordenada por `-data`). Não existe campo direto `animal.lote_id`.
- **Protocolos são versionados.** Alterar protocolo = criar nova versão com `versao+1`. Nunca editar versão existente.
- **`ResultadoConformidade` é imutável.** Após criação, não pode ser editado (bloqueado no admin). Recalcular = criar novo registro.
- **Eventos são imutáveis.** Parto, Colostragem, CuraUmbigo, Pesagem, Vacinacao, Desaleitamento não têm edição via UI. Correção requer Django Admin.
- **Mudança de categoria é irreversível.** Desaleitamento (`terneira→novilha`) e IA (`novilha→vaca`) não podem ser desfeitos via UI.

---

## 8. CAMADA DE CONFORMIDADE

### CriterioConformidade (em config_tecnica/models.py)
Regra mensurável com vigência por propriedade. Diferente de `Protocolo` (documento).

**Códigos disponíveis:**
- `colostragem_tempo` — horas até 1ª colostragem
- `colostragem_volume_relativo` — % do peso vivo na 1ª colostragem
- `colostragem_brix` — Brix mínimo do colostro
- `umbigo_tempo` — horas até 1ª cura de umbigo
- `dias_secos_minimo` / `dias_secos_maximo`
- `dias_pre_parto_minimo`
- `peso_por_idade` — delega para MetaDesenvolvimento
- `desaleitamento_idade_minima` / `desaleitamento_idade_maxima`
- `desaleitamento_peso_minimo`
- `ia_peso_minimo`

### Avaliadores (indicadores/avaliadores.py)

```python
avaliar_evento_parto(parto)         # C5=dias_secos + C6=dias_pre_parto
avaliar_evento_colostragem(col)     # C1=tempo + C2=volume + C3=brix
avaliar_evento_cura_umbigo(cura)    # C4=tempo_umbigo
avaliar_evento_pesagem(pesagem)     # C7=peso_por_idade
```

Comportamentos:
- Dado ausente → `resultado='dado_ausente'` com `motivo_ausencia` explicativo
- Nunca lança exceção (loga silenciosamente)
- Idempotente (não recria se já existe para `animal+criterio+evento_tipo+evento_id`)
- `Q` importado no topo do módulo (`from django.db.models import Q`)

### Seed de critérios padrão

```bash
python manage.py seed_criterios --propriedade 1
python manage.py seed_criterios --propriedade 1 --substituir
```

---

## 9. DASHBOARD (3 zonas) + GRÁFICOS INTERATIVOS

**views:** `core/views_dashboard.py`  
**template:** `templates/dashboard.html`  
**partial:** `templates/partials/kpi_conformidade.html`

### Zona 1 — Alertas
- **Críticos** (vermelho): colostragem pendente, ocorrência aberta >7d, peso crítico <90%, mortes recentes
- **Operacionais** (amarelo): checkpoints pendentes, sem pesagem >30d, parto previsto sem pré-parto, umbigo pendente
- Se nenhum alerta → banner verde "Tudo em dia"

### Zona 2 — Status (período: 30d/90d/180d)
- Desempenho: terneiras ativas, novilhas, nascimentos F/M, GMD médio
- Conformidade: 6 KPIs com verde/amarelo/vermelho
- Sanitário: diarreia, pneumonia, onfalite
- Reprodutivo: novilhas, trajetórias, checkpoints

### Zona 3 — Tendência (6 meses) — 4 Gráficos Chart.js

1. Taxa de colostragem ≤ 2h (%) + meta 90%
2. GMD médio no aleitamento (kg/dia) + meta 0.75 kg/dia
3. Incidência sanitária (%) — diarreia/pneumonia + metas
4. % terneiras dentro da curva de peso + meta 80%

**Dependências Chart.js:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
```

---

## 10. TELA DE LOGIN — ESTADO ATUAL

> **Atenção:** A tela de login passou por extenso redesign. Leia `IMPLEMENTACAO_LOGIN.md` e `TELA_LOGIN_LAYOUT.md` para detalhes completos.

### Arquitetura atual
- **Arquivo:** `templates/accounts/login.html`
- **Standalone:** não herda `base.html`
- **CSS:** embutido na tag `<style>` — sem arquivo `.css` separado
- **Fontes:** Google Fonts Inter (400/500/600/700) + Bootstrap Icons 1.11.3
- **Sem Bootstrap CSS** — todo CSS é customizado

### Estrutura HTML
```html
.login-container          ← fundo escuro #0d1f17, 100vw × 100vh, flex center
  └── .login-right        ← container da imagem (aspect-ratio: 1448/1086, max-height: 94vh)
        ├── <img>         ← Background.png (object-fit: contain, border-radius: 14px)
        └── .login-left   ← posição absoluta, representa a área verde (width: 46.6%)
              └── .login-card   ← card branco, width: min(320px, 100%)
```

### Imagem de fundo
- **Arquivo:** `static/img/Background.png`
- **Dimensões:** 1448 × 1086 px (ratio 4:3)
- **Conteúdo:** arte completa com área verde escura (esquerda) + fotografia de terneiras (direita)
- A área verde ocupa 46.6% da largura (0–675px de 1448px)
- O texto "Tecnologia e cuidado..." e os ícones de benefícios estão **embutidos na imagem** — não recriar em HTML

### Logo
- **Arquivo:** `static/img/logo-terneiraspro.png`
- **Tamanho no card:** `max-width: 200px` — tamanho aprovado, não alterar

### Views de autenticação (`accounts/views.py`)
- `login_view` — integrada ao Django Auth, suporta `?next=`, `remember_me`
- `logout_view` — requer `@login_required`
- `dashboard_view` — requer `@login_required`
- `perfil_view` — requer `@login_required`
- `check_user_status` — endpoint JSON para validação AJAX

### URLs (`accounts/urls.py`, namespace `accounts`)
```
/accounts/login/       → accounts:login
/accounts/logout/      → accounts:logout
/accounts/dashboard/   → accounts:dashboard
/accounts/perfil/      → accounts:perfil
/accounts/api/check-user/ → accounts:check_user
```

---

## 11. URLs COMPLETAS DO SISTEMA

```
/                             → Dashboard
/accounts/login/              → Login
/accounts/logout/             → Logout
/accounts/perfil/             → Perfil do usuário
/selecionar/<pk>/             → Trocar propriedade ativa (GET)

/admin-sistema/               → Painel admin (só superusuário)
/admin-sistema/propriedades/  → Gestão de propriedades
/admin-sistema/usuarios/      → Gestão de usuários
/admin-sistema/vinculos/      → Gestão de vínculos

/animais/                     → Lista terneiras
/animais/nova/                → Nova terneira
/animais/<pk>/                → Ficha da terneira
/animais/<pk>/editar/         → Editar terneira
/animais/vacas/               → Lista vacas
/animais/vacas/nova/          → Nova vaca
/animais/vacas/<pk>/          → Ficha da vaca
/animais/lotes/               → Lista lotes
/animais/lotes/novo/          → Novo lote
/animais/lotes/<pk>/          → Detalhe lote
/animais/vacas/<pk>/ciclo/novo/ → Novo ciclo reprodutivo

/eventos/parto/novo/<ciclo_pk>/         → Registrar parto
/eventos/colostragem/<terneira_pk>/     → Registrar colostragem
/eventos/umbigo/<terneira_pk>/          → Cura de umbigo
/eventos/pesagem/<animal_pk>/           → Pesagem
/eventos/pesagem/<animal_pk>/historico/ → Histórico pesagens
/eventos/sanitario/<animal_pk>/         → Ocorrência sanitária
/eventos/sanitario/<pk>/encerrar/       → Encerrar ocorrência
/eventos/vacinacao/<animal_pk>/         → Vacinação
/eventos/desaleitamento/<terneira_pk>/  → Desaleitamento
/eventos/banco-colostro/                → Banco de colostro
/eventos/banco-colostro/novo/           → Novo registro banco

/programas/                         → Lista de programas
/programas/<pk>/                    → Detalhe programa
/programas/<pk>/checkpoint/         → Realizar checkpoint
/programas/checkpoint/<pk>/         → Detalhe checkpoint
/programas/projecao/<terneira_pk>/  → Projeção reprodutiva
/programas/aptas/                   → Novilhas aptas à reprodução
/programas/ia/<terneira_pk>/        → Registrar cobertura/IA

/config/                            → Painel de config técnica
/config/protocolos/                 → Protocolos
/config/metas/                      → Metas de desenvolvimento
/config/metas/<pk>/                 → Detalhe meta (pontos da curva)
/config/meta-reprodutiva/           → Metas reprodutivas
/config/referenciais/               → Referenciais técnicos
/config/criterios/                  → Critérios de conformidade
/config/criterios/novo/             → Novo critério
/config/criterios/<pk>/editar/      → Editar critério
```

---

## 12. TEMPLATES

```
templates/
  base.html                          ← Layout principal (sidebar, navbar, Alpine, HTMX, Bootstrap, Chart.js)
  dashboard.html                     ← Dashboard 3 zonas + 4 gráficos Chart.js
  selecionar_propriedade.html        ← Seleção de propriedade (usuário com várias fazendas)
  sem_propriedade.html               ← Usuário sem vínculo
  partials/
    kpi_conformidade.html
  accounts/
    login.html                       ← STANDALONE. Design com Background.png + card sobreposto.
                                       Ver TELA_LOGIN_LAYOUT.md para arquitetura CSS completa.
    perfil.html
  admin_sistema/
    primeiro_acesso.html             ← Standalone (não herda base.html)
    painel_admin.html
    lista_propriedades.html / form_propriedade.html
    lista_usuarios.html / form_usuario.html
    lista_vinculos.html / form_vinculo.html
  animais/ eventos/ programas/ config_tecnica/
    (ver seção 11 para mapeamento URL → template)
```

**Convenções de templates:**
- Todos herdam `base.html` exceto `login.html` e `primeiro_acesso.html`
- Sidebar: `{% block nav_terneiras %}active{% endblock %}` para marcar item ativo
- Tabs Alpine.js: `x-data="{tab:'crescimento'}"` + `x-show="tab=='crescimento'"` + `x-cloak`
- `[x-cloak]` definido no CSS: `[x-cloak] { display: none !important; }`
- Sidebar tem seção "Administração" visível apenas para `request.user.is_superuser`

---

## 13. SERVIÇOS DE CÁLCULO (indicadores/services.py)

Funções puras — sem estado, sem efeitos colaterais.

```python
calcular_gmd(peso_inicial, peso_final, data_inicial, data_final)
calcular_gmd_periodo(pesagens, dias_janela=30)
classificar_peso_vs_meta(peso_atual, peso_meta)
interpolar_peso_na_idade(pesagens, idade_alvo_dias)
calcular_taxa_colostragem_2h(terneiras_com_dados)
calcular_incidencia(total_animais, animais_afetados)
calcular_mortalidade(nascidos, mortes)
projetar_data_reprodutiva(data_referencia, peso_atual, peso_alvo, gmd_projetado)
classificar_trajetoria(peso_atual, peso_alvo, gmd_recente, gmd_minimo_necessario,
                       data_referencia, data_alvo)
consolidar_dashboard(propriedade_id, periodo_dias=90)
```

**Regra universal:** `None` nunca é tratado como `0`. Sempre verificar `if valor is not None`.

---

## 14. ARQUIVOS IMPORTANTES

| Arquivo | Função |
|---|---|
| `gestao_terneiras/settings.py` | Configurações do Django |
| `gestao_terneiras/urls.py` | URLs raiz |
| `core/middleware.py` | Injeta `request.propriedade_ativa` e `request.is_master` |
| `core/context_processors.py` | Injeta `propriedade_ativa` e `propriedades_usuario` nos templates |
| `core/views_admin.py` | Painel admin, primeiro acesso, CRUD |
| `core/forms.py` | Formulários do admin |
| `core/views_dashboard.py` | Dashboard com 3 zonas |
| `indicadores/services.py` | Funções de cálculo zootécnico |
| `indicadores/avaliadores.py` | Avaliadores de conformidade C1–C7 |
| `indicadores/models.py` | ResultadoConformidade |
| `templates/base.html` | Layout principal |
| `templates/dashboard.html` | Dashboard + gráficos Chart.js |
| `templates/accounts/login.html` | **Tela de login** — ver TELA_LOGIN_LAYOUT.md |
| `static/img/Background.png` | Arte da tela de login (1448×1086px) — não alterar |
| `static/img/logo-terneiraspro.png` | Logo do sistema |
| `.env` | SECRET_KEY, DEBUG, ALLOWED_HOSTS |

### Dependências Frontend (CDN — definidas em base.html)
```html
<!-- Bootstrap 5.3.3 + Icons -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
<!-- JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<!-- Chart.js (somente no dashboard) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
```

> **Atenção:** `login.html` NÃO usa Bootstrap CSS. Usa apenas Bootstrap Icons e Google Fonts Inter.

---

## 15. FLUXO OPERACIONAL COMPLETO

### Setup de nova propriedade
```
1. Login como admin → /primeiro-acesso/ → criar fazenda
2. python manage.py seed_referenciais
3. python manage.py seed_criterios --propriedade 1
4. /config/metas/nova/ → criar MetaDesenvolvimento + pontos da curva
5. /config/meta-reprodutiva/nova/ → criar MetaReprodutiva
```

### Registrar uma terneira (fluxo completo)
```
1. /animais/vacas/nova/               → cadastrar vaca mãe
2. /animais/vacas/<pk>/ciclo/novo/    → ciclo reprodutivo
3. /eventos/parto/novo/<ciclo_pk>/    → parto → cria terneira + programa
4. /eventos/colostragem/<pk>/         → colostragem → avaliadores C1+C2+C3
5. /eventos/umbigo/<pk>/              → cura umbigo → avaliador C4
6. /eventos/pesagem/<pk>/             → pesagens → avaliador C7
7. /eventos/sanitario/<pk>/           → ocorrências sanitárias
8. /eventos/desaleitamento/<pk>/      → desaleitar → categoria vira novilha
9. /programas/<pk>/checkpoint/        → checkpoint aos 6 meses
10. /programas/projecao/<pk>/         → projeção reprodutiva
11. /programas/ia/<pk>/               → IA → categoria vira vaca
```

---

## 16. DADOS PRÉ-CARREGADOS

9 referenciais técnicos (Embrapa + literatura):

| Indicador | Valor |
|---|---|
| Tempo até colostragem | ≤ 2h (crítico ≥ 6h) |
| Volume de colostro | 10% do peso vivo |
| Brix do colostro | ≥ 22% |
| Dias secos | 45–75 dias (ideal 60) |
| Dias no pré-parto | mínimo 21 dias |
| GMD aleitamento (Holandês) | ideal 0,8 kg/dia |
| Mortalidade até 60 dias | ideal ≤ 2%, limite 5% |
| Incidência de diarreia | ideal ≤ 15%, limite 25% |
| Incidência de pneumonia | ideal ≤ 10%, limite 15% |

---

## 17. CONVENÇÕES DE CÓDIGO

- Views sempre verificam `request.propriedade_ativa` antes de qualquer query
- Superusuário verificado via `request.is_master` ou `request.user.is_superuser`
- Formulários de animais recebem `propriedade=prop` no `__init__`
- Avaliadores sempre importam `Q` no topo: `from django.db.models import Q`
- `None` nunca é tratado como `0`
- Scripts de diagnóstico: criar como arquivos `.py` separados (shell do Django não aceita múltiplas linhas via `-c`)

---

## 18. O QUE NÃO EXISTE (não implementar)

- Gestão financeira (custo, rentabilidade, margem)
- Produção de leite de vacas adultas
- CCS individual
- Integração com sensores/equipamentos
- Estoque de insumos com valoração
- Reprodução completa de vacas adultas (só 1ª IA da novilha está no escopo)

---

## 19. PROBLEMAS CONHECIDOS / DECISÕES PENDENTES

### Bugs conhecidos (correção necessária)

1. **`form_colostragem.html` usa `{{ meta_volume }}`** mas view não passa a variável. Template exibe campo vazio onde deveria mostrar "Volume recomendado: X ml (10% do peso vivo)".

2. **Metas dos gráficos são hardcoded** em `_buscar_metas_graficos()` (meta_colostro_tempo=90%, meta_gmd=0.75, meta_diarreia=15%, etc). Deveriam vir de CriterioConformidade ou serem configuráveis.

3. **SECRET_KEY no `.env`** é insegura (`django-insecure-...`). Gerar nova chave forte para produção.

### Funcionalidades parcialmente implementadas

4. **`ProtocoloAlimentar` e `RegistroAlimentacaoDiario`** — modelos completos, mas sem views/templates/URLs. Funcionalidade planejada não acessível.

5. **`MovimentacaoLote`** — modelo existe, lote atual é calculado, mas não há formulário UI para registrar movimentações. Só via Django Admin.

6. **Critérios C8, C9, C10 (desaleitamento)** — códigos existem em CriterioConformidade mas avaliadores não implementados. Desaleitamento não gera ResultadoConformidade.

7. **Sistema de permissões por papel** — papéis (`admin`, `tecnico`, `produtor`, `auxiliar`) existem em UsuarioPerfil mas NENHUMA view verifica papel. Todos os usuários autenticados têm acesso total.

### Comportamentos indefinidos (decisão necessária)

8. **Editar data de nascimento** — não recalcula conformidades, projeções ou programas automaticamente. Pode gerar inconsistências. NÃO DEFINIDO se deve recalcular ou bloquear edição.

9. **Vaca com múltiplos ciclos simultâneos em `gestando`** — sistema permite mas comportamento não está definido. Uma vaca pode ter 2+ ciclos abertos?

10. **Checkpoint fora da janela 165-195 dias** — sistema bloqueia criação mas não documenta o que acontece se janela expirar sem registro.

11. **`Colostragem.tempo_apos_nascimento_horas`** — retorna `None` se `hora_parto` não foi registrado. Conformidade C1 gera `dado_ausente` mas usuário não é alertado na tela de parto sobre a importância de registrar hora.

### Limitações técnicas conhecidas

12. **ProjecaoReprodutiva não recalcula automaticamente** ao registrar nova pesagem. Cálculo é manual via `/programas/projecao/<pk>/`.

13. **Validações ausentes:** sistema aceita peso absurdo (5000kg), idade incompatível, desaleitamento antes de idade mínima, etc.

14. **URLs de seleção de propriedade** — prefixo mudou para `/selecionar/<pk>/`. Links hardcoded antigos podem gerar 404.

---

## 20. MIGRATIONS

**Estado atual:** todas aplicadas.

```
core         → 0001
accounts     → 0001
animais      → 0001
config_tecnica → 0001, 0002
eventos      → 0001
programas    → 0001
indicadores  → 0001
```

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py check   # deve retornar "no issues"
```

---

## 21. RAÇAS DISPONÍVEIS

```python
('holandes', 'Holandês'), ('jersey', 'Jersey'), ('girolando', 'Girolando'),
('gir_leiteiro', 'Gir Leiteiro'), ('guzera', 'Guzerá'),
('pardo_suico', 'Pardo Suíço'), ('mestaca', 'Mestiça'), ('outra', 'Outra')
# Em CriterioConformidade e MetaDesenvolvimento:
('todas', 'Todas as raças')
```

---

## 22. DOCUMENTAÇÃO COMPLEMENTAR

| Arquivo | Conteúdo |
|---|---|
| `DOCUMENTACAO_AGENTE.md` | Este arquivo — visão geral do projeto |
| `IMPLEMENTACAO_LOGIN.md` | Estado atual da tela de login, autenticação e decisões de design |
| `TELA_LOGIN_LAYOUT.md` | Arquitetura CSS detalhada, medições da Background.png, valores aprovados |
| `.kiro/steering/projeto.md` | Regras permanentes para agentes de IA |

---

## 23. LOGO NA NAVBAR (base.html) — ESTADO E PENDÊNCIAS

### Estado atual (Agosto 2026)

O `base.html` foi alterado durante a sessão de desenvolvimento para incluir o logo real na navbar:

**Antes:**
```html
<a class="navbar-brand ...">
  <i class="bi bi-activity fs-4"></i>
  <span class="d-none d-sm-inline">TerneirasPro</span>
</a>
```

**Atual:**
```html
<nav ... style="z-index:1050; height: 56px;">
  <div class="container-fluid px-3">
    <a class="navbar-brand ... me-2" href="/">
      <img src="/static/img/logobranco.png?v=9" alt="TerneirasPro"
           style="height: 44px !important; width: auto !important; max-height: none !important;">
    </a>
```

Arquivo de logo: `static/img/logobranco.png` — existe, 463 KB, criado em 15/08/2026.

### O que funciona

- Logo exibido na navbar com `height: 44px`
- Navbar com altura fixa `56px`
- `padding-top: 56px` no conteúdo compensa corretamente
- Arquivo `logobranco.png` está presente

### Pendência conhecida

A sessão que fez essas alterações terminou com status `failed` durante ajustes de tamanho do logo e posicionamento do botão de toggle da sidebar. O histórico indica que em alguma iteração o logo ficou grande demais e cobriu parte da navbar. O estado atual (`height: 44px`) parece razoável mas **não foi validado visualmente pelo usuário** — a última mensagem antes da falha era sobre a "setinha da barra de rolagem superior" cortando.

**Antes de alterar o logo ou a navbar novamente:** verificar o comportamento visual atual no navegador. O estado pode estar correto ou precisar de um ajuste fino de 2–3px.

### Arquivos relacionados

- `templates/base.html` — logo e navbar
- `static/img/logobranco.png` — logo branco para fundo verde
- `static/img/logo-terneiraspro.png` — logo original (cor, para tela de login)
- `static/img/logo_sem_fundo.png` — variante sem fundo (criada em 15/08/2026)
- `static/css/main.css` — contém posicionamento da sidebar (verifica `top: 56px`)

---

## 24. DECISÕES DE SIMPLIFICAÇÃO DE FORMULÁRIOS

> Registradas em Agosto 2026. Fonte original: `SIMPLIFICACAO_DADOS.md` (documento histórico, não atualizar).

### Critério aplicado

Cada campo de formulário foi avaliado em três categorias:
- **Essencial:** necessário para cálculos, conformidades ou decisões de manejo
- **Útil/Opcional:** informação interessante mas não deve poluir a tela principal
- **Redundante:** não utilizado em nenhum cálculo, indicador ou decisão — removido

### Formulário de Parto (`PartoForm`)

**Campo removido:**
- `tempo_levantar_min` — não participa de nenhum cálculo ou conformidade

**Campo mantido como obrigatório:**
- `peso_nascimento` — **ESSENCIAL**: base do cálculo do volume de colostro (peso_kg × 100 = ml recomendados)
- `hora_parto` — **ESSENCIAL**: necessário para calcular tempo até colostragem (conformidade C1)

### Formulário de Pesagem (`PesagemForm`)

**Campos removidos da interface principal:**
- `altura_garupa_cm` — não participa de cálculos ou conformidades
- `perimetro_toracico_cm` — não participa de cálculos ou conformidades
- `ecc` (Escore de Condição Corporal) — sem utilização prática implementada

**Solução adotada:** formulário alternativo `PesagemComplementarForm` criado para quando medições extras são necessárias, acessível via `/pesagem/<id>/complementar/`.

### Regra permanente

**Não re-adicionar campos removidos sem justificativa técnica concreta** (que cálculo ou conformidade o campo alimenta?). A simplificação foi uma decisão deliberada de produto para reduzir carga operacional.

---

## 1. GESTÃO DE PROPRIEDADES E MULTI-TENANCY

### 1.1. Criar primeira propriedade (primeiro acesso)

**Objetivo:** Permitir que um administrador do sistema configure a primeira fazenda na instalação.

**Quem pode executar:** Apenas superusuário (is_superuser=True)

**Pré-condições:** 
- Usuário autenticado como superusuário
- Nenhuma propriedade existe no banco de dados

**Entrada:**
- Nome da propriedade (obrigatório)
- CNPJ/CPF (opcional)
- Endereço completo (opcional)
- Telefone de contato (opcional)
- E-mail (opcional)
- Responsável técnico (opcional)

**Processo:**
1. Sistema detecta ausência de propriedades e redireciona para `/primeiro-acesso/`
2. Usuário preenche formulário standalone (não herda base.html)
3. Sistema cria propriedade com `ativa=True` (forçado no código, não depende do formulário)
4. Sistema cria vínculo `UsuarioPerfil` automaticamente: superusuário → propriedade → papel=admin
5. Sistema define `propriedade_ativa_id` na sessão
6. Redireciona para dashboard

**Resultado:**
- Propriedade criada e ativa
- Superusuário vinculado como admin
- Sessão configurada com propriedade ativa

**Automações:**
- Criação automática de vínculo admin
- Ativação automática da propriedade
- Configuração da sessão

**Restrições:**
- Apenas superusuários podem acessar
- Formulário não permite criar propriedade inativa (campo `ativa` não está no PropriedadeForm)

**Histórico:**
- Registro de criação preservado no campo `criado_em`

**Regras de negócio:**
- REGRA CONFIRMADA: Primeira propriedade sempre é criada como `ativa=True`
- REGRA CONFIRMADA: Campo `ativa` só está disponível na edição (PropriedadeEditForm), não na criação

**Estado resultante:**
- Propriedade: `ativa=True`, vinculada ao superusuário

---

### 1.2. Gerenciar múltiplas propriedades

**Objetivo:** Permitir que o sistema atenda múltiplas fazendas em uma única instalação (SaaS multi-tenant).

**Quem pode executar:** Apenas superusuários

**Funcionalidades disponíveis:**
- Criar novas propriedades (`/admin-sistema/propriedades/nova/`)
- Editar propriedades existentes incluindo campo `ativa` (`/admin-sistema/propriedades/<pk>/editar/`)
- Listar todas as propriedades (`/admin-sistema/propriedades/`)
- Trocar propriedade ativa rapidamente (`/admin-sistema/propriedades/<pk>/selecionar/`)

**Processo de isolamento:**
1. Middleware `PropriedadeMiddleware` injeta `request.propriedade_ativa` em cada requisição
2. Propriedade ativa vem de `request.session['propriedade_ativa_id']`
3. Todas as queries filtram por `propriedade=request.propriedade_ativa`
4. Superusuários podem ver qualquer propriedade ativa; se não houver propriedade na sessão, sistema pega a primeira

**Regras de negócio:**
- REGRA CONFIRMADA: Cada propriedade é completamente isolada (dados, animais, eventos, configurações)
- REGRA CONFIRMADA: Superusuário pode acessar qualquer propriedade; usuário comum só acessa propriedades vinculadas via UsuarioPerfil
- REGRA CONFIRMADA: Middleware sempre garante `request.propriedade_ativa` ou redireciona
- IMPLEMENTAÇÃO ATUAL: Não existe limite de propriedades por instalação

**Estado resultante:**
- Sistema operando em modo multi-tenant com isolamento completo

**DIVERGÊNCIA DOCUMENTAÇÃO × IMPLEMENTAÇÃO:**
- URLs antigas de seleção de propriedade mudaram de prefixo
- Documentação menciona links hardcoded que podem gerar 404

---

### 1.3. Troca de propriedade ativa

**Objetivo:** Permitir que usuários com acesso a múltiplas fazendas alternem entre elas.

**Quem pode executar:**
- Superusuários: podem alternar para qualquer propriedade `ativa=True`
- Usuários comuns: podem alternar apenas entre propriedades vinculadas via `UsuarioPerfil` com `ativo=True`

**Entrada:**
- ID da propriedade de destino

**Processo:**
1. Sistema valida que usuário tem acesso à propriedade solicitada
2. Atualiza `request.session['propriedade_ativa_id']`
3. Redireciona para URL solicitada ou dashboard

**Resultado:**
- Sessão atualizada
- Todas as views subsequentes operam no contexto da nova propriedade

**Restrições:**
- Usuário comum não pode selecionar propriedade para a qual não tem vínculo ativo
- Propriedade deve estar `ativa=True`

**Regras de negócio:**
- REGRA CONFIRMADA: Troca de propriedade não afeta outros usuários (sessão individual)
- REGRA CONFIRMADA: Animais, eventos e configurações mudam completamente ao trocar de propriedade

---

## 2. GESTÃO DE USUÁRIOS E PERMISSÕES

### 2.1. Criar usuário do sistema

**Objetivo:** Cadastrar novos usuários que poderão acessar o sistema.

**Quem pode executar:** Apenas superusuários via `/admin-sistema/usuarios/novo/`

**Pré-condições:**
- Usuário autenticado como superusuário

**Entrada:**
- Username (obrigatório, único)
- Senha (obrigatório)
- Nome completo (opcional)
- E-mail (opcional)
- Telefone (opcional)
- Status ativo (boolean)

**Processo:**
1. Sistema valida unicidade do username
2. Cria usuário com senha criptografada (Django Auth)
3. NÃO cria vínculo automaticamente com nenhuma propriedade

**Resultado:**
- Usuário criado mas SEM acesso a nenhuma propriedade

**Automações:**
- Senha automaticamente hasheada via Django Auth

**Restrições:**
- Username deve ser único no sistema
- Criar usuário NÃO é suficiente para dar acesso — precisa criar vínculo separadamente

**Regras de negócio:**
- REGRA CONFIRMADA: Usuário sem vínculo `UsuarioPerfil` ativo vê tela "sem_propriedade.html" após login
- IMPLEMENTAÇÃO ATUAL: Não há validação de força de senha
- IMPLEMENTAÇÃO ATUAL: Não há recuperação de senha por e-mail

**Estado resultante:**
- Usuário: `is_active=True`, sem vínculos

---

### 2.2. Vincular usuário a propriedade

**Objetivo:** Dar acesso a um usuário para operar em uma fazenda específica com um papel definido.

**Quem pode executar:** Apenas superusuários via `/admin-sistema/vinculos/novo/`

**Entrada:**
- Usuário (FK)
- Propriedade (FK)
- Papel: `admin` | `tecnico` | `produtor` | `auxiliar`
- Ativo (boolean)

**Processo:**
1. Sistema cria registro `UsuarioPerfil`
2. Vínculo pode ser ativado/desativado sem exclusão

**Resultado:**
- Usuário ganha acesso à propriedade com o papel especificado

**Restrições:**
- Um usuário pode ter múltiplos vínculos (múltiplas propriedades)
- Um usuário pode ter múltiplos papéis em propriedades diferentes
- NÃO DEFINIDO: Se um usuário pode ter múltiplos papéis na MESMA propriedade

**Regras de negócio:**
- REGRA CONFIRMADA: Vínculo inativo (`ativo=False`) impede acesso mesmo que exista
- IMPLEMENTAÇÃO ATUAL: Papéis existem no banco mas NÃO são verificados em views (ver seção 2.4)
- NÃO DEFINIDO: Hierarquia entre papéis (admin > tecnico > produtor > auxiliar?)

**Estado resultante:**
- UsuarioPerfil criado com papel definido

**LACUNA CRÍTICA:**
- Sistema de papéis existe no modelo mas não é utilizado nas views

---

### 2.3. Editar e desativar usuários

**Objetivo:** Atualizar dados de usuários ou remover acesso sem excluir histórico.

**Quem pode executar:** Apenas superusuários

**Funcionalidades:**
- Editar dados do usuário (`/admin-sistema/usuarios/<pk>/editar/`)
- Resetar senha
- Ativar/desativar usuário (`is_active`)
- Remover vínculos (`/admin-sistema/vinculos/<pk>/remover/` — exclusão física)

**Processo:**
- Desativar usuário (`is_active=False`) impede login
- Desativar vínculo (`ativo=False`) impede acesso à propriedade mas mantém histórico

**Regras de negócio:**
- REGRA CONFIRMADA: Desativar usuário não remove eventos registrados por ele (FK com SET_NULL)
- REGRA CONFIRMADA: Remover vínculo é exclusão física, não soft delete
- IMPLEMENTAÇÃO ATUAL: Não há confirmação ao remover vínculo

---

### 2.4. Controle de acesso por papel (SISTEMA DE PERMISSÕES)

**Objetivo:** Restringir funcionalidades baseado no papel do usuário na propriedade.

**Papéis documentados:**
- `admin` — administrador da fazenda
- `tecnico` — técnico/veterinário  
- `produtor` — proprietário/gestor
- `auxiliar` — operador de campo

**IMPLEMENTAÇÃO ATUAL:**
- ✅ Modelo `UsuarioPerfil` tem campo `papel` com 4 opções
- ✅ Middleware injeta `request.propriedade_ativa`
- ❌ NENHUMA view verifica papel além de `@login_required`
- ❌ Não existem decorators `@permission_required` ou `@user_passes_test`
- ❌ Não existem mixins de permissão em views
- ❌ Templates não verificam papel para ocultar/exibir funcionalidades

**LACUNA CRÍTICA:**
```
NÃO DEFINIDO — Sistema de papéis não está implementado funcionalmente.

Qualquer usuário autenticado e vinculado pode:
- Criar/editar/excluir animais
- Registrar todos os eventos
- Alterar configurações técnicas
- Ver dashboard completo
- Acessar todas as URLs da propriedade

Não há distinção de permissões entre admin, tecnico, produtor e auxiliar.
```

**Decisões pendentes:**
1. Quais funcionalidades cada papel pode executar?
2. Admin pode editar configurações mas auxiliar não?
3. Técnico aprova desaleitamento ou qualquer um pode registrar?
4. Produtor pode excluir animais?
5. Auxiliar pode ver indicadores financeiros (se implementados no futuro)?

**Impacto:**
- Segurança: Qualquer usuário pode fazer operações críticas
- Auditoria: Não há separação de responsabilidades
- Conformidade: Pode violar requisitos de controle de acesso

---

## 3. GESTÃO DO REBANHO

### 3.1. Cadastrar vacas (matrizes)

**Objetivo:** Registrar fêmeas adultas que gerarão terneiras.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade (sistema de permissões por papel NÃO está implementado)

**Pré-condições:**
- Propriedade ativa configurada

**Entrada:**
- Identificação (brinco/chip/nome) — obrigatório, único por propriedade
- Nome (opcional)
- Sexo: fixo `F`
- Raça: Holandês | Jersey | Girolando | Gir Leiteiro | Guzerá | Pardo Suíço | Mestiça | Outra
- Descrição da raça (se Mestiça ou Outra)
- Data de nascimento (opcional)
- Mãe (FK para outro Animal, opcional)
- Pai/Sêmen (texto livre, opcional)
- Situação: ativa (padrão) | morta | vendida | descartada | transferida
- Data de saída (se situação != ativa)
- Motivo da saída
- Observações

**Processo:**
1. Sistema valida unicidade de identificação dentro da propriedade
2. Cria Animal com `categoria='vaca'` e `sexo='F'`
3. Redireciona para ficha da vaca

**Resultado:**
- Vaca cadastrada no sistema
- Disponível para criar ciclos reprodutivos

**Automações:**
- Nenhuma automação no cadastro de vaca

**Restrições:**
- Identificação deve ser única por propriedade (unique_together)
- Categoria não pode ser alterada manualmente após criação (mudanças automáticas via eventos)

**Regras de negócio:**
- REGRA CONFIRMADA: Vaca pode ser mãe de múltiplos animais (relação one-to-many via campo `mae`)
- IMPLEMENTAÇÃO ATUAL: Não valida idade mínima/máxima para ser considerada vaca
- NÃO DEFINIDO: Vaca pode ter histórico de produção de leite? (fora do escopo do sistema)

**Estado resultante:**
- Animal: `categoria='vaca'`, `sexo='F'`, `situacao='ativa'`

---

### 3.2. Gerenciar lotes de manejo

**Objetivo:** Organizar animais em grupos para facilitar manejo e aplicação de protocolos.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Tipos de lote disponíveis:**
- Pré-parto
- Maternidade
- Aleitamento
- Pós-desaleitamento
- Recria
- Vacas em lactação
- Vacas secas
- Geral

**Funcionalidades:**
- Criar lote (`/animais/lotes/novo/`)
- Listar lotes (`/animais/lotes/`)
- Ver animais de um lote (`/animais/lotes/<pk>/`)

**Processo de movimentação:**
- IMPLEMENTAÇÃO ATUAL: Modelo `MovimentacaoLote` existe
- ❌ NÃO há formulário de movimentação pela UI
- REGRA CONFIRMADA: Lote atual do animal = última movimentação registrada
- REGRA CONFIRMADA: Não existe campo direto `animal.lote` — sempre derivado de `MovimentacaoLote`

**Histórico:**
- Todas as movimentações são preservadas (histórico completo)
- `movimentacoes.order_by('-data')` para obter lote atual

**Regras de negócio:**
- REGRA CONFIRMADA: Animal pode estar sem lote (nenhuma movimentação registrada)
- REGRA CONFIRMADA: Lote tem `ativo` (soft delete) mas movimentações são permanentes
- IMPLEMENTAÇÃO ATUAL: Não há validação de lote apropriado para categoria (terneira no lote de vacas secas é permitido)

**LACUNA CRÍTICA:**
```
FUNCIONALIDADE INCOMPLETA — Sistema não verifica permissões por papel.

MovimentacaoLote existe no modelo mas não há interface UI para registrar movimentações.
Usuário vê "lote atual" na ficha mas não consegue mover animais entre lotes.
Única forma é via Django Admin ou shell.
```

**Decisões pendentes:**
1. Movimentação deve ser manual ou automática baseada em eventos?
2. Desaleitamento move automaticamente para lote "Pós-desaleitamento"?
3. Múltiplos animais podem ser movidos em lote (operação em massa)?

---

### 3.3. Registrar ciclo reprodutivo da vaca

**Objetivo:** Documentar uma gestação específica vinculando a vaca mãe ao nascimento da terneira.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Pré-condições:**
- Vaca cadastrada no sistema

**Entrada:**
- Vaca (FK obrigatório)
- Número da lactação (1 = primeira cria, 2 = segunda, etc.)
- Data da cobertura/IA (opcional)
- Touro/sêmen utilizado (opcional)
- Data de previsão do parto (opcional)
- Data da secagem (opcional)
- Tratamento de secagem (texto livre)
- Data de entrada no pré-parto (opcional)
- Lote pré-parto (FK opcional)
- ECC na entrada do pré-parto (1.0 a 5.0, opcional)
- Situação: gestando (padrão) | encerrado_parto | encerrado_aborto | encerrado_outro

**Processo:**
1. Usuário acessa ficha da vaca e clica "Novo ciclo reprodutivo"
2. Preenche formulário
3. Sistema cria CicloReprodutivo vinculado à vaca

**Resultado:**
- Ciclo criado com `situacao='gestando'`
- Disponível para registrar parto futuro

**Automações:**
- Nenhuma ao criar ciclo
- Situação muda automaticamente para `encerrado_parto` ao registrar Parto

**Restrições:**
- Um ciclo reprodutivo pode ter apenas UM parto (OneToOne)
- NÃO DEFINIDO: Vaca pode ter múltiplos ciclos em `situacao='gestando'` simultaneamente?

**Regras de negócio:**
- REGRA CONFIRMADA: Campos `data_secagem` e `data_entrada_pre_parto` são usados para calcular conformidade (C5 e C6)
- REGRA CONFIRMADA: `dias_secos` e `dias_pre_parto` são properties calculadas APÓS o parto ser registrado
- IMPLEMENTAÇÃO ATUAL: Não valida se previsão de parto é compatível com data de cobertura (280 dias de gestação)

**Estado resultante:**
- CicloReprodutivo: `situacao='gestando'`, sem parto vinculado

---

## 4. GESTÃO DAS TERNEIRAS

### 4.1. Cadastrar terneira manualmente

**Objetivo:** Registrar fêmeas jovens que não nasceram de partos rastreados no sistema.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Pré-condições:**
- Propriedade ativa

**Entrada:**
- Mesmos campos de Animal (identificação, nome, sexo='F', raça, data_nascimento, etc.)
- Categoria: fixo `terneira`

**Processo:**
1. Sistema cria Animal com `categoria='terneira'`, `sexo='F'`
2. Se `data_nascimento` informada, cria `ProgramaAcompanhamento` automaticamente

**Resultado:**
- Terneira cadastrada
- Programa de acompanhamento criado

**Automações:**
- Criação automática de `ProgramaAcompanhamento` se data de nascimento existe

**Restrições:**
- Terneiras cadastradas manualmente NÃO têm `parto_origem` (campo fica null)

**Regras de negócio:**
- REGRA CONFIRMADA: Terneira sem data de nascimento não gera programa de acompanhamento
- IMPLEMENTAÇÃO ATUAL: Não valida idade máxima para ser considerada terneira (pode cadastrar animal de 2 anos como terneira)

**Estado resultante:**
- Animal: `categoria='terneira'`, `sexo='F'`, `situacao='ativa'`
- ProgramaAcompanhamento: `status='em_andamento'` (se data_nascimento existe)

---

### 4.2. Visualizar ficha completa da terneira

**Objetivo:** Acesso consolidado a todos os dados, eventos e indicadores de uma terneira específica.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Informações exibidas:**

**Dados cadastrais:**
- Identificação, nome, raça, data de nascimento, idade (dias e meses)
- Mãe, pai/sêmen
- Categoria atual, situação

**Origem:**
- Parto de origem (se nascida de parto rastreado)
- Facilidade do parto, vitalidade, peso ao nascer

**Crescimento:**
- Lista de pesagens (data, peso, idade na pesagem)
- GMD total (primeira a última pesagem)
- GMD recente (últimos 30 dias)
- Gráfico: peso real × peso meta da raça (Chart.js)
- Classificação: dentro da curva | atenção | crítico

**Eventos sanitários:**
- Ocorrências abertas e encerradas (tipo, data, tratamento, resultado)
- Vacinações (vacina, data, lote)

**Manejo:**
- Colostragens (data/hora, volume, origem, Brix, método)
- Curas de umbigo (data/hora, produto, avaliação do coto)
- Desaleitamento (data, método, peso, idade)

**Lotes:**
- Lote atual
- Histórico de movimentações

**Programa de acompanhamento:**
- Status: em_andamento | encerrado | cancelado
- Dias decorridos, % concluído
- Checkpoint realizado (se existe)
- Indicador se checkpoint está pendente (165-195 dias)

**Processo:**
1. View carrega animal e todos os relacionamentos via `select_related` e `prefetch_related`
2. Calcula GMD usando `indicadores/services.py`
3. Busca `MetaDesenvolvimento` para a raça e interpola peso meta
4. Classifica peso vs meta
5. Gera dados para gráfico Chart.js

**Regras de negócio:**
- REGRA CONFIRMADA: GMD só é calculado se existem pelo menos 2 pesagens
- REGRA CONFIRMADA: Classificação de peso requer meta ativa para a raça
- REGRA CONFIRMADA: Gráfico só exibe pontos onde há meta interpolada

**DIVERGÊNCIA DOCUMENTAÇÃO × IMPLEMENTAÇÃO:**
```
Template form_colostragem.html usa variável {{ meta_volume }} mas view 
registrar_colostragem() não passa essa variável no contexto.

Resultado: campo exibe vazio onde deveria mostrar volume recomendado (10% do peso vivo).
```

---

### 4.3. Editar dados cadastrais da terneira

**Objetivo:** Corrigir ou atualizar informações do animal.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Campos editáveis:**
- Identificação, nome, raça, raça_descricao
- Data de nascimento
- Mãe, pai_identificação
- Situação (ativa | morta | vendida | descartada | transferida)
- Data de saída, motivo de saída
- Observações

**Campos NÃO editáveis:**
- Propriedade (imutável)
- Categoria (mudada automaticamente via eventos)
- Sexo (imutável)

**Processo:**
- Formulário padrão do Django com instância
- Validação de unicidade de identificação

**Restrições:**
- Alterar data de nascimento NÃO recalcula automações já executadas
- NÃO DEFINIDO: Alterar data de nascimento deve recalcular conformidades e projeções?

**Regras de negócio:**
- IMPLEMENTAÇÃO ATUAL: Não há restrição para mudar situação para "morta" se existem eventos futuros
- NÃO DEFINIDO: Alterar mãe retroativamente afeta conformidades já calculadas?

**LACUNA CRÍTICA:**
```
NÃO DEFINIDO — Comportamento após edição de dados históricos.

Se data de nascimento é alterada:
- Conformidades de colostragem (tempo) devem ser recalculadas?
- Conformidades de peso/idade devem ser recalculadas?
- Projeções reprodutivas devem ser invalidadas?
- Programa de acompanhamento deve recalcular datas?

Sistema não recalcula nada automaticamente após edição.
```

---

## 5. EVENTOS ZOOTÉCNICOS

### 5.1. Registrar parto

**Objetivo:** Criar o animal nascido e vincular ao ciclo reprodutivo da mãe.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Pré-condições:**
- Ciclo reprodutivo da vaca em `situacao='gestando'`
- Ciclo NÃO pode ter parto já registrado (OneToOne)

**Entrada do parto:**
- Data do parto (obrigatório)
- Hora do parto (opcional mas crítico para conformidade de colost

ragem)
- Facilidade: 0=normal | 1=pequena assistência | 2=tração moderada | 3=cesariana
- Houve assistência? (boolean)
- Parto gemelar? (boolean)
- Peso ao nascer (kg, opcional)
- Vitalidade: normal | lento | fraco | natimorto
- Tempo para levantar (minutos, opcional)
- Lesões ou anormalidades (texto livre)

**Entrada do animal nascido:**
- Identificação (obrigatório, único)
- Sexo: F | M
- Raça (padrão = raça da mãe)

**Processo:**
1. Sistema cria Animal:
   - `identificacao` fornecida
   - `sexo` fornecido
   - `raca` = raça da vaca ou selecionado
   - `categoria` = 'terneira' se F, 'bezerro' se M
   - `data_nascimento` = data_parto
   - `mae` = vaca do ciclo
   - `pai_identificacao` = touro_semen do ciclo

2. Sistema cria Parto:
   - `ciclo` = ciclo reprodutivo
   - `terneira` = animal criado
   - Dados do parto preenchidos
   - `registrado_por` = request.user

3. Sistema atualiza ciclo:
   - `situacao` = 'encerrado_parto'

4. Se sexo='F', sistema cria ProgramaAcompanhamento:
   - `terneira` = animal criado
   - `data_inicio` = data_parto
   - `duracao_dias` = 180 (padrão)
   - `status` = 'em_andamento'

5. Sistema dispara avaliador:
   - `avaliar_evento_parto(parto)` → verifica C5 (dias secos) e C6 (dias pré-parto)

**Resultado:**
- Animal nascido cadastrado
- Parto registrado
- Ciclo reprodutivo encerrado
- Programa de acompanhamento iniciado (se fêmea)
- Conformidades C5 e C6 avaliadas e registradas em `ResultadoConformidade`

**Automações:**
- Criação do Animal
- Criação do ProgramaAcompanhamento (fêmeas)
- Atualização de `ciclo.situacao`
- Avaliação de conformidade automática

**Restrições:**
- Um ciclo só pode ter um parto (OneToOne constraint)
- Identificação do nascido deve ser única na propriedade
- Ciclo deve estar em `situacao='gestando'` (verificado na view)

**Regras de negócio:**
- REGRA CONFIRMADA: Machos recebem `categoria='bezerro'` e NÃO geram programa de acompanhamento
- REGRA CONFIRMADA: Dias secos = `data_secagem` até `data_parto` (calculado após parto)
- REGRA CONFIRMADA: Dias pré-parto = `data_entrada_pre_parto` até `data_parto`
- REGRA CONFIRMADA: Se `data_secagem` ou `data_entrada_pre_parto` estiverem ausentes no ciclo, conformidade gera `resultado='dado_ausente'` com motivo

**Histórico:**
- Parto é imutável após criação (não há view de edição)
- Para corrigir erro, usar Django Admin ou registrar nova terneira
- COMPORTAMENTO INDEFINIDO: O que fazer se animal foi registrado com dados incorretos?

**Estado resultante:**
- Animal: `categoria='terneira'` ou `'bezerro'`, `situacao='ativa'`
- Parto: criado com todos os dados
- CicloReprodutivo: `situacao='encerrado_parto'`
- ProgramaAcompanhamento: `status='em_andamento'` (apenas fêmeas)
- ResultadoConformidade: C5 e C6 criados

---

### 5.2. Registrar colostragem

**Objetivo:** Documentar cada fornecimento de colostro à terneira.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Pré-condições:**
- Terneira cadastrada
- Idealmente, parto com `hora_parto` registrada (para calcular tempo)

**Entrada:**
- Terneira (FK)
- Data e hora do fornecimento (obrigatório)
- Volume fornecido (ml, obrigatório)
- Origem: mãe biológica | banco | sucedâneo | outra vaca
- Lote do banco (FK opcional, se origem=banco)
- Método: mamada direta | mamadeira | sonda | balde
- Brix (%, opcional mas crítico para conformidade)
- Temperatura (°C, opcional)
- Ingestão confirmada? (boolean, padrão True)
- Responsável (FK request.user)
- Observações

**Processo:**
1. Sistema valida dados
2. Cria registro Colostragem
3. Sistema dispara avaliador:
   - `avaliar_evento_colostragem(col)` → verifica C1 (tempo), C2 (volume relativo), C3 (Brix)

**Resultado:**
- Colostragem registrada
- Conformidades C1, C2 e C3 avaliadas e registradas em `ResultadoConformidade`

**Automações:**
- Avaliação de conformidade automática
- Cálculo de `tempo_apos_nascimento_horas` (property)

**Restrições:**
- Terneira pode ter múltiplas colostragens (relação one-to-many)
- Primeira colostragem é crítica para conformidade

**Regras de negócio:**
- REGRA CONFIRMADA: Tempo após nascimento só pode ser calculado se `parto_origem.hora_parto` existe
- REGRA CONFIRMADA: C1 (tempo) avalia se primeira colostragem ocorreu ≤ 2h após nascimento
- REGRA CONFIRMADA: C2 (volume relativo) avalia se volume ≥ 10% do peso ao nascer (ou peso da primeira pesagem)
- REGRA CONFIRMADA: C3 (Brix) avalia se Brix ≥ 22%
- REGRA CONFIRMADA: Se dados necessários estiverem ausentes (hora_parto, peso, Brix), conformidade gera `resultado='dado_ausente'` com motivo explicativo

**Histórico:**
- Todas as colostragens são preservadas
- Ordem cronológica via `data_hora`

**Estado resultante:**
- Colostragem: criada
- ResultadoConformidade: C1, C2, C3 criados (ou marcados como dado_ausente)

**DIVERGÊNCIA DOCUMENTAÇÃO × IMPLEMENTAÇÃO:**
```
Template form_colostragem.html espera variável {{ meta_volume }} para exibir 
volume recomendado (10% do peso vivo).

View registrar_colostragem() NÃO passa essa variável no contexto.

Correção necessária: calcular meta_volume = peso_nascimento * 0.10 e passar no contexto.
```

---

### 5.3. Registrar cura de umbigo

**Objetivo:** Documentar aplicação de produto no umbigo e avaliar estado do coto umbilical.

**Quem pode executar:** Qualquer usuário autenticado com vínculo ativo à propriedade

**Entrada:**
- Terneira (FK)
- Data e hora (obrigatório)
- Produto utilizado (texto, obrigatório)
- Concentração (opcional)
- Método de aplicação: imersão | aspersão | pincel
- Avaliação do umbigo:
  - Coto seco? (boolean nullable)
  - Inchaço? (boolean)
  - Secreção? (boolean)
  - Odor? (boolean)
  - Sangramento? (boolean)
  - Dor à palpação? (boolean)
  - Suspeita de onfalite? (boolean)
- Foto (upload opcional)
- Responsável (FK)
- Observações

**Processo:**
1. Sistema cria registro CuraUmbigo
2. Sistema dispara avaliador:
   - `avaliar_evento_cura_umbigo(cura)` → verifica C4 (tempo até primeira cura)

**Resultado:**
- Cura de umbigo registrada
- Conformidade C4 avaliada

**Automações:**
- Avaliação de conformidade automática (C4)

**Restrições:**
- Terneira pode ter múltiplas curas de umbigo (histórico de aplicações)
- Primeira cura é crítica para conformidade

**Regras de negócio:**
- REGRA CONFIRMADA: C4 avalia se primeira cura ocorreu nas primeiras horas após nascimento
- REGRA CONFIRMADA: Critério de tempo é configurável via `CriterioConformidade` (código='umbigo_tempo')
- IMPLEMENTAÇÃO ATUAL: Foto é armazenada mas não há galeria na ficha da terneira

**Histórico:**
- Todas as curas preservadas
- Histórico permite rastrear evolução do umbigo

**Estado resultante:**
- CuraUmbigo: criada
- ResultadoConformidade: C4 criado

---

Devido ao tamanho, vou continuar criando a especificação funcional em partes. Devo continuar agora com as próximas seções (Pesagem, Ocorrências Sanitárias, etc.)?


---

# RELATÓRIO DE AUDITORIA FUNCIONAL

> **Data da auditoria:** Agosto 2026  
> **Escopo:** Comparação entre especificação funcional documentada e implementação real do TerneirasPro

---

## RESUMO EXECUTIVO

### Funcionalidades mapeadas: 47+

**Por área funcional:**
1. Propriedades e multi-tenancy: 3 funcionalidades
2. Usuários e permissões: 4 funcionalidades
3. Gestão do rebanho: 3 funcionalidades
4. Gestão das terneiras: 3 funcionalidades
5. Eventos zootécnicos: 8 funcionalidades
6. Programas de acompanhamento: 4 funcionalidades
7. Reprodução: 1 funcionalidade
8. Configurações técnicas: 5 funcionalidades
9. Conformidade e indicadores: 2 funcionalidades
10. Dashboard e alertas: 1 funcionalidade (com 13 sub-componentes)
11. Admin do sistema: 8 funcionalidades

### Status de implementação

| Status | Quantidade | % |
|---|---:|---:|
| ✅ Totalmente implementado | 35 | 74% |
| ⚠️ Parcialmente implementado | 10 | 21% |
| ❌ Documentado mas não implementado | 2 | 4% |
| ⚡ Implementado mas não documentado | 0 | 0% |

---

## 1. FUNCIONALIDADES TOTALMENTE IMPLEMENTADAS (35)

### Gestão de propriedades ✅
- Criar primeira propriedade (primeiro acesso)
- Gerenciar múltiplas propriedades (multi-tenant com isolamento completo)
- Trocar propriedade ativa

### Gestão de usuários ✅
- Criar usuário do sistema
- Vincular usuário a propriedade com papel
- Editar e desativar usuários

### Rebanho ✅
- Cadastrar vacas (matrizes)
- Gerenciar lotes de manejo (criar, listar, visualizar)
- Registrar ciclo reprodutivo da vaca

### Terneiras ✅
- Cadastrar terneira manualmente
- Visualizar ficha completa da terneira (com gráficos Chart.js)
- Editar dados cadastrais

### Eventos zootécnicos ✅
- Registrar parto (cria animal + programa automaticamente)
- Registrar colostragem (múltiplas, com avaliação automática C1/C2/C3)
- Registrar cura de umbigo (com avaliação automática C4)
- Registrar pesagem (com avaliação automática C7)
- Registrar ocorrência sanitária (abrir e encerrar)
- Registrar vacinação
- Registrar desaleitamento (muda categoria automaticamente)
- Gerenciar banco de colostro

### Programas ✅
- Programa de acompanhamento automático (criado no nascimento)
- Checkpoint de 6 meses (cálculo automático completo)
- Projeção reprodutiva (classificação de trajetória)
- Lista de novilhas aptas à reprodução

### Reprodução ✅
- Registrar primeira cobertura/IA (encerra escopo)

### Configurações técnicas ✅
- Gerenciar protocolos (versionados)
- Configurar metas de desenvolvimento (curvas de peso)
- Configurar metas reprodutivas
- Configurar critérios de conformidade (C1-C7)
- Consultar referenciais técnicos

### Conformidade ✅
- Avaliação automática de conformidade (C1-C7 implementados)
- Dashboard com KPIs consolidados

### Dashboard ✅
- Dashboard 3 zonas completo (alertas + status + tendência)
- 4 gráficos Chart.js de tendência (6 meses)
- 10 tipos de alertas (críticos + operacionais)

### Admin do sistema ✅
- Painel admin completo para superusuários
- CRUD de propriedades, usuários e vínculos

---

## 2. FUNCIONALIDADES PARCIALMENTE IMPLEMENTADAS (10)

### ⚠️ Sistema de permissões por papel
**Status:** Modelo existe, lógica NÃO implementada  
**Implementado:**
- Modelo `UsuarioPerfil` com campo `papel` (admin/tecnico/produtor/auxiliar)
- Criação e edição de vínculos

**NÃO implementado:**
- Decorators de permissão além de `@login_required`
- Verificação de papel em views
- Restrições por papel em templates
- Matriz de permissões funcional

**Impacto:** Qualquer usuário autenticado pode executar qualquer operação

---

### ⚠️ Movimentação de lotes
**Status:** Modelo existe, UI NÃO implementada  
**Implementado:**
- Modelo `MovimentacaoLote` completo
- Lógica de "lote atual" (última movimentação)
- Exibição de lote atual na ficha

**NÃO implementado:**
- Formulário de movimentação pela UI
- Movimentação em massa
- Histórico visual de movimentações

**Impacto:** Movimentações só podem ser criadas via Django Admin ou shell

---

### ⚠️ Protocolo alimentar e registro diário
**Status:** Modelos existem, views/templates NÃO existem  
**Implementado:**
- Modelos `ProtocoloAlimentar` e `RegistroAlimentacaoDiario` completos

**NÃO implementado:**
- Views para criar/editar protocolos alimentares
- Views para registrar alimentação diária
- Templates correspondentes
- URLs mapeadas

**Impacto:** Funcionalidade planejada mas não acessível pela interface

---

### ⚠️ Consulta detalhada de conformidades
**Status:** Dados existem, interface de consulta NÃO existe  
**Implementado:**
- `ResultadoConformidade` gerado automaticamente
- KPIs agregados no dashboard

**NÃO implementado:**
- Listagem de não-conformidades por animal
- Filtros por período, tipo, resultado
- Relatório exportável
- Aba de conformidade na ficha da terneira

**Impacto:** Usuário só vê conformidade agregada, não consegue detalhar por animal

---

### ⚠️ Critérios de desaleitamento (C8, C9, C10)
**Status:** Códigos existem no modelo, avaliadores NÃO implementados  
**Implementado:**
- Modelo `CriterioConformidade` permite códigos:
  - `desaleitamento_idade_minima`
  - `desaleitamento_idade_maxima`
  - `desaleitamento_peso_minimo`

**NÃO implementado:**
- Função `avaliar_evento_desaleitamento()` não existe
- Desaleitamento não gera `ResultadoConformidade`
- Validações de idade/peso mínimos

**Impacto:** Desaleitamento pode ser registrado fora dos padrões técnicos sem alerta

---

### ⚠️ Recálculo de conformidades após edição
**Status:** Edição permitida, recálculo NÃO automático  
**Implementado:**
- Edição de animais (data nascimento, raça, etc.)
- Conformidades imutáveis (não editáveis)

**NÃO implementado:**
- Recálculo automático de conformidades ao alterar data de nascimento
- Invalidação de projeções ao alterar peso/raça
- Recálculo de programa ao alterar data de nascimento

**Impacto:** Dados históricos podem ficar inconsistentes após edições

---

### ⚠️ Controle de estoque do banco de colostro
**Status:** Registro existe, controle de volume NÃO automático  
**Implementado:**
- Modelo `BancoColostro` completo
- Registro de lotes
- Referência em colostragem

**NÃO implementado:**
- Dedução automática de volume ao usar
- Alertas de estoque baixo
- Relatório de rastreabilidade (lote → terneiras)

**Impacto:** Controle de estoque deve ser manual

---

### ⚠️ Metas configuráveis nos gráficos
**Status:** Gráficos existem, metas são hardcoded  
**Implementado:**
- 4 gráficos Chart.js no dashboard
- Linhas de meta exibidas

**NÃO implementado:**
- Metas vêm de `_buscar_metas_graficos()` com valores fixos
- Não há interface para alterar metas dos gráficos

**Impacto:** Metas não refletem configuração da propriedade

---

### ⚠️ Validações técnicas automáticas
**Status:** Eventos registrados, validações ausentes  
**Exemplos:**
- Peso absurdo em pesagem (5000kg)
- Desaleitamento antes de idade mínima
- Gestação incompatível com data de cobertura (≠280 dias)
- Idade máxima para categoria terneira

**Impacto:** Dados incorretos podem ser registrados

---

### ⚠️ Histórico de alterações
**Status:** Eventos imutáveis, mas dados cadastrais editáveis sem auditoria  
**Implementado:**
- Campos `criado_em`, `atualizado_em`
- `registrado_por`, `responsavel` em eventos

**NÃO implementado:**
- Log de quem alterou dados cadastrais (identificação, data nascimento)
- Histórico de mudanças de categoria
- Auditoria de exclusões

**Impacto:** Alterações maliciosas ou acidentais não são rastreáveis

---

## 3. FUNCIONALIDADES DOCUMENTADAS MAS NÃO IMPLEMENTADAS (2)

### ❌ Edição de eventos após registro
**Status:** NÃO implementado  
**Eventos imutáveis:**
- Parto, Colostragem, CuraUmbigo, Pesagem, Vacinacao, Desaleitamento

**Motivo técnico:** Editar eventos históricos invalidaria conformidades já calculadas

**Decisão pendente:** Implementar edição com recálculo ou manter imutável?

---

### ❌ Exclusão de animais
**Status:** NÃO implementado via UI  
**Implementado:**
- Campo `situacao` permite marcar como morta/vendida/descartada
- Soft delete funcional

**NÃO implementado:**
- Exclusão física (delete) pela UI
- Motivo: preservar histórico e integridade referencial

---

## 4. DIVERGÊNCIAS ENTRE DOCUMENTAÇÃO E IMPLEMENTAÇÃO (10 CRÍTICAS)

### 🔴 DIVERGÊNCIA #1: Template form_colostragem.html
**Documentado:** Template usa `{{ meta_volume }}` para exibir volume recomendado  
**Implementado:** View `registrar_colostragem()` NÃO passa essa variável no contexto  
**Resultado:** Campo exibe vazio  
**Correção:** Calcular `meta_volume = peso_nascimento * 0.10` e passar no contexto

---

### 🔴 DIVERGÊNCIA #2: Sistema de papéis não funcional
**Documentado:** 4 papéis com permissões diferentes (admin, tecnico, produtor, auxiliar)  
**Implementado:** Papéis existem no banco mas não são verificados em nenhuma view  
**Resultado:** Todos os usuários têm acesso total  
**Impacto:** Segurança e auditoria comprometidas

---

### 🔴 DIVERGÊNCIA #3: Metas dos gráficos hardcoded
**Documentado:** Metas devem vir de configuração  
**Implementado:** Valores fixos em `_buscar_metas_graficos()`  
**Resultado:** Metas não customizáveis por propriedade

---

### 🔴 DIVERGÊNCIA #4: Escopo pós-primeira IA
**Documentado:** "Sistema termina na primeira IA"  
**Implementado:** Animal permanece na base, pode continuar recebendo eventos  
**Resultado:** Não há separação clara entre recria e vacas adultas

---

### 🔴 DIVERGÊNCIA #5: URLs de seleção de propriedade
**Documentado:** Links antigos podem estar em templates  
**Implementado:** Prefixo mudou para `/selecionar/<pk>/`  
**Resultado:** Possíveis 404s em links hardcoded

---

### 🔴 DIVERGÊNCIA #6: SECRET_KEY insegura
**Documentado:** Chave de produção deve ser forte  
**Implementado:** `.env` contém `django-insecure-...`  
**Resultado:** Vulnerabilidade em produção

---

### 🔴 DIVERGÊNCIA #7: Critérios C8-C10 não implementados
**Documentado:** Desaleitamento deve ser avaliado  
**Implementado:** Avaliadores não existem  
**Resultado:** Conformidade de desaleitamento não é medida

---

### 🔴 DIVERGÊNCIA #8: MovimentacaoLote sem UI
**Documentado:** Lotes são fundamentais para manejo  
**Implementado:** Funcionalidade parcial (sem formulário)  
**Resultado:** Recurso planejado mas inacessível

---

### 🔴 DIVERGÊNCIA #9: Protocolo alimentar não acessível
**Documentado:** Rastreamento de alimentação  
**Implementado:** Modelos prontos mas sem interface  
**Resultado:** Funcionalidade prevista mas não utilizável

---

### 🔴 DIVERGÊNCIA #10: Conformidade sem detalhamento
**Documentado:** Usuário deve ver detalhes de não-conformidades  
**Implementado:** Apenas KPIs agregados no dashboard  
**Resultado:** Falta visibilidade operacional

---

## 5. REGRAS DE NEGÓCIO CLARAMENTE DEFINIDAS (20+)

### ✅ Confirmadas e implementadas:

1. Multi-tenancy com isolamento completo por propriedade
2. Primeira propriedade sempre criada como `ativa=True`
3. Dado ausente ≠ zero (null explícito em campos opcionais)
4. Lote atual = derivado da última MovimentacaoLote (não há campo direto)
5. Protocolos são versionados (alterar = criar nova versão)
6. ResultadoConformidade é imutável (não editável)
7. Avaliadores são idempotentes (não recriam se já existe)
8. Avaliadores nunca lançam exceções (log silencioso)
9. GMD só calculado com ≥2 pesagens
10. Checkpoint disponível entre 165-195 dias
11. Dias secos = data_secagem até data_parto
12. Dias pré-parto = data_entrada_pre_parto até data_parto
13. Conformidade diferencia: conforme | nao_conforme | dado_ausente | nao_aplicavel
14. Taxa de conformidade = conformes / (conformes + nao_conformes) — dado_ausente não entra
15. Desaleitamento muda categoria: terneira → novilha (automático)
16. IA muda categoria: novilha → vaca (automático)
17. Checkpoint muda status: programa em_andamento → encerrado (automático)
18. Parto encerra ciclo: gestando → encerrado_parto (automático)
19. Machos recebem categoria 'bezerro' e NÃO geram programa
20. Interpolação linear entre pontos da curva de peso

---

## 6. DECISÕES PENDENTES (TOP 10 CRÍTICAS)

### 1️⃣ Sistema de permissões por papel
**Questão:** Quais funcionalidades cada papel pode executar?  
**Contexto:** Modelo existe mas não há lógica de verificação  
**Impacto:** Segurança, auditoria, conformidade regulatória  
**Prioridade:** 🔴 CRÍTICA

### 2️⃣ Recálculo após edição de dados históricos
**Questão:** Alterar data de nascimento deve recalcular conformidades/projeções?  
**Contexto:** Edição permitida mas recálculo não automático  
**Impacto:** Inconsistência de dados, conformidades incorretas  
**Prioridade:** 🔴 CRÍTICA

### 3️⃣ Implementar critérios de desaleitamento (C8-C10)
**Questão:** Validar idade mínima/máxima e peso mínimo?  
**Contexto:** Códigos existem mas avaliadores não implementados  
**Impacto:** Desaleitamento fora de padrões técnicos passa sem alerta  
**Prioridade:** 🟠 ALTA

### 4️⃣ Edição vs. imutabilidade de eventos
**Questão:** Permitir correção de eventos ou manter imutáveis?  
**Contexto:** Erro de digitação requer exclusão no Django Admin  
**Impacto:** Usabilidade, confiança no sistema  
**Prioridade:** 🟠 ALTA

### 5️⃣ Movimentação de lotes pela UI
**Questão:** Implementar formulário de movimentação?  
**Contexto:** Modelo pronto mas sem interface  
**Impacto:** Rastreabilidade de manejo comprometida  
**Prioridade:** 🟠 ALTA

### 6️⃣ Protocolo alimentar e registro diário
**Questão:** Implementar interface ou remover modelos não utilizados?  
**Contexto:** Modelos completos mas sem views/templates  
**Impacto:** Funcionalidade planejada mas inacessível  
**Prioridade:** 🟡 MÉDIA

### 7️⃣ Metas configuráveis nos gráficos
**Questão:** Metas devem vir de CriterioConformidade ou serem configuráveis separadamente?  
**Contexto:** Atualmente hardcoded em view  
**Impacto:** Metas não refletem realidade da propriedade  
**Prioridade:** 🟡 MÉDIA

### 8️⃣ Controle automático de estoque de colostro
**Questão:** Deduzir volume automaticamente ao vincular em colostragem?  
**Contexto:** Registro existe mas controle é manual  
**Impacto:** Risco de usar colostro inexistente  
**Prioridade:** 🟡 MÉDIA

### 9️⃣ Interface de consulta de conformidades
**Questão:** Criar tela de detalhamento de não-conformidades por animal?  
**Contexto:** Dados existem mas interface só mostra KPIs agregados  
**Impacto:** Falta visibilidade operacional para correções  
**Prioridade:** 🟡 MÉDIA

### 🔟 Validações técnicas automáticas
**Questão:** Implementar validações de consistência (peso absurdo, idade incompatível, etc.)?  
**Contexto:** Sistema aceita qualquer valor  
**Impacto:** Qualidade dos dados, confiança nos indicadores  
**Prioridade:** 🟡 MÉDIA

---

## 7. PONTOS FORTES DO SISTEMA

✅ **Arquitetura sólida:** Multi-tenancy bem implementado, isolamento completo  
✅ **Automações robustas:** 10+ ações automáticas funcionando corretamente  
✅ **Avaliadores de conformidade:** C1-C7 implementados com lógica correta  
✅ **Dashboard completo:** 3 zonas + 4 gráficos + 10 tipos de alertas  
✅ **Rastreabilidade:** Histórico completo preservado, campos de auditoria  
✅ **Cálculos zootécnicos:** GMD, interpolação de curvas, projeções implementadas  
✅ **Interface moderna:** Bootstrap 5 + Alpine.js + HTMX + Chart.js  
✅ **Admin do sistema:** Painel completo para gestão de propriedades/usuários  
✅ **Regras de negócio claras:** 20+ regras documentadas e implementadas corretamente  
✅ **Tela de login:** Design profissional, autenticação integrada ao Django Auth

---

## 8. RECOMENDAÇÕES PRIORITÁRIAS

### Curto prazo (1-2 sprints)

1. **Implementar matriz de permissões** — decisão crítica de segurança
2. **Corrigir divergência do meta_volume** — bug visível ao usuário
3. **Implementar critérios C8-C10** — conformidade incompleta
4. **Documentar decisão sobre edição de eventos** — definir imutabilidade

### Médio prazo (3-4 sprints)

5. **Implementar movimentação de lotes** — modelo pronto, falta UI
6. **Interface de conformidade detalhada** — melhorar visibilidade operacional
7. **Metas configuráveis nos gráficos** — remover valores hardcoded
8. **Definir política de recálculo** — comportamento após edições

### Longo prazo (backlog)

9. **Protocolo alimentar** — decidir se implementa ou remove modelos
10. **Validações técnicas** — melhorar qualidade dos dados
11. **Auditoria completa** — log de alterações em dados cadastrais
12. **Controle de estoque** — automação do banco de colostro

---

## 9. CONCLUSÃO

O **TerneirasPro** possui uma base sólida com **74% das funcionalidades totalmente implementadas**. A arquitetura é robusta, o multi-tenancy funciona corretamente e as automações críticas estão operacionais.

**Principais lacunas:**
- Sistema de permissões não funcional (crítico)
- 3 critérios de conformidade não implementados (C8-C10)
- 2 funcionalidades com modelos prontos mas sem UI (movimentação lotes, protocolo alimentar)
- 10 divergências entre documentação e implementação

**Próximos passos:**
1. Definir matriz de permissões (decisão de produto)
2. Corrigir bugs conhecidos (meta_volume, metas hardcoded)
3. Implementar critérios faltantes ou documentar exclusão
4. Decidir sobre funcionalidades parciais (implementar ou remover)

O sistema está **funcional e utilizável** mas requer decisões de produto para fechar lacunas críticas de segurança e conformidade.

---

**Fim da auditoria funcional**

