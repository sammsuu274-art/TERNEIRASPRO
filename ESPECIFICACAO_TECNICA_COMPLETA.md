# ESPECIFICAÇÃO TÉCNICA COMPLETA — TerneirasPro

**Versão:** 1.0  
**Data:** Agosto 2026  
**Status:** Pronto para Implementação  
**Destinatários:** Equipe de Desenvolvimento

---

## ÍNDICE

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Objetivos e Escopo](#2-objetivos-e-escopo)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Arquitetura do Sistema](#4-arquitetura-do-sistema)
5. [Modelos de Dados](#5-modelos-de-dados)
6. [Funcionalidades Implementadas](#6-funcionalidades-implementadas)
7. [Funcionalidades Parciais](#7-funcionalidades-parciais)
8. [Decisões de Design](#8-decisões-de-design)
9. [Integração com Banco de Dados](#9-integração-com-banco-de-dados)
10. [Frontend e Interface](#10-frontend-e-interface)
11. [Segurança e Autenticação](#11-segurança-e-autenticação)
12. [Deployment e Produção](#12-deployment-e-produção)
13. [Checklist de Implementação](#13-checklist-de-implementação)
14. [Problemas Conhecidos e Pendências](#14-problemas-conhecidos-e-pendências)

---

## 1. VISÃO GERAL DO PROJETO

### Nome
**TerneirasPro** — Sistema de Gestão Técnica da Cria e Recria de Fêmeas Bovinas Leiteiras

### Descrição
Sistema web que rastreia o desenvolvimento de terneiras (fêmeas jovens bovinas) desde o pré-parto da mãe até a primeira inseminação (IA) da novilha, com conformidade contra critérios técnicos baseados em literatura zootécnica (Embrapa + padrões internacionais).

### Contexto de Negócio
- **Usuários:** Proprietários de fazendas, técnicos, veterinários, auxiliares
- **Fazendas:** Multi-tenant (múltiplas propriedades em uma instalação)
- **Dados Críticos:** Rastreabilidade completa de eventos zootécnicos
- **Compliance:** Conformidade contra 7 critérios técnicos (C1–C7)

### Diferencial
Não é ERP, não é sistema financeiro, não é produção de leite. Foco exclusivo em indicadores zootécnicos de qualidade.

---

## 2. OBJETIVOS E ESCOPO

### Objetivos Principais
✅ Rastrear desenvolvimento de terneiras com histórico imutável  
✅ Alertar sobre não-conformidades técnicas em tempo real  
✅ Calcular indicadores de desempenho (GMD, peso, projeções)  
✅ Suportar múltiplas fazendas em uma instalação  
✅ Providenciar dashboard com 3 zonas (alertas, status, tendência)  

### O QUE ESTÁ NO ESCOPO
- ✅ Gestão de propriedades (multi-tenant)
- ✅ Autenticação e controle de acesso por usuário/propriedade
- ✅ CRUD de animais (vacas, terneiras, bezerros)
- ✅ Registro de 8+ eventos zootécnicos com histórico
- ✅ Cálculos zootécnicos (GMD, interpolação de curvas, projeções)
- ✅ Conformidade automática (C1–C7)
- ✅ Dashboard com alertas e gráficos Chart.js
- ✅ Admin do sistema para gestão de propriedades/usuários
- ✅ Tela de login profissional

### O QUE NÃO ESTÁ NO ESCOPO
- ❌ Gestão financeira (custos, rentabilidade, margens)
- ❌ Produção de leite (CCS individual, volumes)
- ❌ Reprodução de vacas adultas (além da 1ª IA da novilha)
- ❌ Integração com sensores ou equipamentos
- ❌ Estoque com valoração
- ❌ Vendas/marketing

---

## 3. STACK TECNOLÓGICO

### Backend
```
Python 3.12
Django 4.2.16
Banco de dados: SQLite (dev) | PostgreSQL (prod — Neon/Supabase)
ORM: Django ORM
```

### Frontend
```
HTML5 + Bootstrap 5.3.3
CSS3 (customizado, sem SCSS)
JavaScript: Alpine.js 3 + HTMX 1.9
Gráficos: Chart.js 4
Ícones: Bootstrap Icons 1.11.3
Fontes: Google Fonts Inter
```

### Dependências (requirements.txt)
```
Django==4.2.16
python-decouple==3.8
Pillow==10.4.0
whitenoise==6.7.0
psycopg2-binary==2.9.9
```

### Ferramentas
```
Git (versionamento)
GitHub (repositório)
Render.com ou Heroku (hosting — futuro)
Cloudflare Tunnel (acesso seguro — futuro)
```

### Versões Críticas
- ✅ Django 4.2.16 — LTS, suporte até Abril 2028
- ✅ Python 3.12 — suportado por Django 4.2
- ⚠️ psycopg2-binary 2.9.9 — verificar compatibilidade com PostgreSQL 14+
- ⚠️ whitenoise 6.7.0 — versão instalada é 6.12.0 (verificar se há incompatibilidades)

---

## 4. ARQUITETURA DO SISTEMA

### Estrutura de Pastas
```
TERNEIRAS/
├── gestao_terneiras/           # Projeto Django (settings, urls raiz)
│   ├── settings.py             # Configurações centrais
│   ├── urls.py                 # Mapeamento de URLs raiz
│   ├── wsgi.py                 # Aplicação WSGI
│   └── asgi.py                 # (se usar async)
├── core/                        # App central
│   ├── models.py               # Propriedade, Usuário, UsuarioPerfil
│   ├── views_admin.py          # Painel admin, primeiro acesso
│   ├── views_dashboard.py      # Dashboard 3 zonas
│   ├── urls.py                 # URLs do core
│   ├── middleware.py           # Injeção de propriedade_ativa
│   ├── context_processors.py   # Contexto global em templates
│   └── forms.py                # Formulários de admin e propriedades
├── accounts/                    # Autenticação
│   ├── models.py               # Usuario, UsuarioPerfil
│   ├── views.py                # Login, logout, perfil
│   ├── urls.py                 # URLs de autenticação
│   └── forms.py                # Formulários de login
├── animais/                     # Gestão de animais
│   ├── models.py               # Animal, Lote, MovimentacaoLote, CicloReprodutivo
│   ├── views.py                # CRUD de animais, ciclos
│   ├── urls.py                 # URLs de animais
│   └── forms.py                # Formulários de animais
├── eventos/                     # Eventos zootécnicos
│   ├── models.py               # Parto, Colostragem, Pesagem, Vacinação, etc.
│   ├── views.py                # Views para registrar eventos
│   ├── urls.py                 # URLs de eventos
│   └── forms.py                # Formulários de eventos
├── programas/                   # Programa de acompanhamento
│   ├── models.py               # ProgramaAcompanhamento, Checkpoint, ProjecaoReprodutiva
│   ├── views.py                # Views de programas e checkpoints
│   ├── urls.py                 # URLs de programas
│   └── forms.py                # Formulários de programas
├── config_tecnica/              # Configurações técnicas
│   ├── models.py               # Protocolo, Meta, CriterioConformidade
│   ├── views.py                # Views de configuração
│   ├── urls.py                 # URLs de config
│   ├── forms.py                # Formulários de config
│   └── management/commands/    # Seed de dados (referenciais, critérios)
├── indicadores/                 # Conformidade e cálculos
│   ├── models.py               # ResultadoConformidade
│   ├── services.py             # Funções de cálculo zootécnico
│   ├── avaliadores.py          # Avaliadores C1–C7
│   └── urls.py                 # (se houver views de indicadores)
├── templates/                   # Templates HTML
│   ├── base.html               # Layout principal
│   ├── dashboard.html          # Dashboard
│   ├── accounts/
│   │   └── login.html          # Tela de login
│   ├── animais/                # Templates de animais
│   ├── eventos/                # Templates de eventos
│   ├── programas/              # Templates de programas
│   └── config_tecnica/         # Templates de config
├── static/                      # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
├── media/                       # Upload de usuários (fotos, etc)
├── .env                        # Variáveis de ambiente (NÃO versionado)
├── .env.production.template    # Template para produção
├── .gitignore                  # Configuração de git
├── requirements.txt            # Dependências Python
├── manage.py                   # CLI do Django
└── db.sqlite3                  # Banco SQLite (NÃO versionado)
```

### Fluxo de Requisição
```
1. Usuário acessa URL
   ↓
2. Middleware PropriedadeMiddleware injeta request.propriedade_ativa
   ↓
3. View verifica @login_required (Django Auth)
   ↓
4. View filtra queryset por propriedade_ativa
   ↓
5. Template renderiza com contexto (Alpine.js, HTMX se necessário)
   ↓
6. Resposta HTML + static files (CSS, JS via WhiteNoise)
```

### Padrão de Automação (Eventos)
```
Usuário registra evento (ex: Parto)
   ↓
Signal ou view cria Animal + ProgramaAcompanhamento
   ↓
Signal ou view dispara avaliadores (ex: avaliar_evento_parto)
   ↓
Avaliadores criam ResultadoConformidade (C5, C6)
   ↓
Dashboard recalcula KPIs na próxima requisição
```

---

## 5. MODELOS DE DADOS

### Propriedade (Core)
```python
class Propriedade(models.Model):
    nome: CharField
    cnpj_cpf: CharField (opcional)
    endereco: TextField (opcional)
    telefone: CharField (opcional)
    email: EmailField (opcional)
    responsavel_tecnico: CharField (opcional)
    ativa: BooleanField = True
    criado_em: DateTimeField (auto_now_add)
    atualizado_em: DateTimeField (auto_now)
    
    __str__(): nome
    Meta: ordering = ['-ativa', 'nome']
```

### Usuário (Accounts)
```python
class Usuario(AbstractUser):
    # Herda de AbstractUser do Django
    telefone: CharField (opcional)
    
    REQUIRED_FIELDS = ['email']
    
class UsuarioPerfil(models.Model):
    usuario: ForeignKey(Usuario)
    propriedade: ForeignKey(Propriedade)
    papel: CharField = choices(['admin', 'tecnico', 'produtor', 'auxiliar'])
    ativo: BooleanField = True
    criado_em: DateTimeField
    
    class Meta: unique_together = [['usuario', 'propriedade']]
```

### Animal (Animais)
```python
class Animal(models.Model):
    propriedade: ForeignKey(Propriedade)
    identificacao: CharField (unique_together com propriedade)
    nome: CharField (opcional)
    sexo: CharField = choices(['F', 'M'])
    categoria: CharField = choices(['vaca', 'terneira', 'bezerro', 'novilha'])
    raca: CharField
    raca_descricao: TextField (opcional)
    data_nascimento: DateField (opcional)
    mae: ForeignKey(Animal, null=True) # Auto-referência
    pai_identificacao: CharField (opcional)
    situacao: CharField = choices(['ativa', 'morta', 'vendida', 'descartada', 'transferida'])
    data_saida: DateField (opcional)
    motivo_saida: TextField (opcional)
    observacoes: TextField (opcional)
    criado_em: DateTimeField
    atualizado_em: DateTimeField
    
    # Properties calculadas:
    idade_dias: int
    idade_meses: float
    lote_atual: Lote (derivado de MovimentacaoLote)
    
    def __str__(): f"{self.identificacao} - {self.nome}"
    Meta: unique_together = [['propriedade', 'identificacao']]
```

### Ciclo Reprodutivo (Animais)
```python
class CicloReprodutivo(models.Model):
    propriedade: ForeignKey(Propriedade)
    vaca: ForeignKey(Animal)
    numero_lactacao: PositiveIntegerField
    data_cobertura: DateField (opcional)
    touro_semen: CharField (opcional)
    data_previsao_parto: DateField (opcional)
    data_secagem: DateField (opcional)
    tratamento_secagem: TextField (opcional)
    data_entrada_pre_parto: DateField (opcional)
    lote_pre_parto: ForeignKey(Lote, null=True)
    ecc_entrada_pre_parto: DecimalField (1.0-5.0, opcional)
    situacao: CharField = choices(['gestando', 'encerrado_parto', 'encerrado_aborto', 'encerrado_outro'])
    criado_em: DateTimeField
    
    # Properties:
    dias_secos: int (data_secagem até data_parto)
    dias_pre_parto: int (data_entrada até data_parto)
```

### Parto (Eventos)
```python
class Parto(models.Model):
    propriedade: ForeignKey(Propriedade)
    ciclo: OneToOneField(CicloReprodutivo)
    terneira: ForeignKey(Animal) # Animal nascido
    data_parto: DateField
    hora_parto: TimeField (opcional)
    facilidade: IntegerField = choices([0,1,2,3]) # normal, pequena, tração, cesariana
    houve_assistencia: BooleanField
    parto_gemelar: BooleanField
    peso_nascimento: DecimalField (kg, opcional)
    vitalidade: CharField = choices(['normal', 'lento', 'fraco', 'natimorto'])
    tempo_levantar_min: IntegerField (opcional)
    lesoes_anormalidades: TextField (opcional)
    registrado_por: ForeignKey(Usuario)
    criado_em: DateTimeField
    
    # Signal: atualiza ciclo.situacao = 'encerrado_parto'
    # Signal: cria ProgramaAcompanhamento (se terneira.sexo == 'F')
    # Signal: dispara avaliar_evento_parto() → C5, C6
```

### Colostragem (Eventos)
```python
class Colostragem(models.Model):
    propriedade: ForeignKey(Propriedade)
    terneira: ForeignKey(Animal)
    data_hora: DateTimeField
    volume_ml: PositiveIntegerField
    origem: CharField = choices(['mae', 'banco', 'sucedaneo', 'outra_vaca'])
    lote_banco: ForeignKey(BancoColostro, null=True)
    metodo: CharField = choices(['mamada_direta', 'mamadeira', 'sonda', 'balde'])
    brix_percentual: DecimalField (opcional)
    temperatura_c: DecimalField (opcional)
    ingestao_confirmada: BooleanField = True
    responsavel: ForeignKey(Usuario)
    observacoes: TextField (opcional)
    criado_em: DateTimeField
    
    # Property:
    tempo_apos_nascimento_horas: float (calculado via parto.hora_parto)
    
    # Signal: dispara avaliar_evento_colostragem() → C1, C2, C3
```

### Pesagem (Eventos)
```python
class Pesagem(models.Model):
    propriedade: ForeignKey(Propriedade)
    animal: ForeignKey(Animal)
    data: DateField
    peso_kg: DecimalField
    idade_dias_registrada: PositiveIntegerField (opcional)
    altura_garupa_cm: PositiveIntegerField (opcional)
    perimetro_toracico_cm: PositiveIntegerField (opcional)
    ecc: DecimalField (1.0-5.0, opcional)
    responsavel: ForeignKey(Usuario)
    observacoes: TextField (opcional)
    criado_em: DateTimeField
    
    # Signal: dispara avaliar_evento_pesagem() → C7
```

### ResultadoConformidade (Indicadores)
```python
class ResultadoConformidade(models.Model):
    propriedade: ForeignKey(Propriedade)
    animal: ForeignKey(Animal)
    criterio: ForeignKey(CriterioConformidade, null=True)
    meta_desenvolvimento: ForeignKey(MetaDesenvolvimento, null=True)
    evento_tipo: CharField # 'parto', 'colostragem', 'umbigo', 'pesagem'
    evento_id: PositiveIntegerField
    valor_observado: CharField (opcional)
    valor_referencia: CharField (opcional)
    desvio: DecimalField (opcional)
    resultado: CharField = choices(['conforme', 'nao_conforme', 'dado_ausente', 'nao_aplicavel'])
    motivo_ausencia: TextField (se resultado == 'dado_ausente')
    criado_em: DateTimeField
    
    class Meta: 
        unique_together = [['animal', 'criterio', 'evento_tipo', 'evento_id']]
    # Regra: imutável após criação (não editar)
```

---

## 6. FUNCIONALIDADES IMPLEMENTADAS

### 6.1 Gestão de Propriedades ✅
```
/admin-sistema/propriedades/
- Listar todas
- Criar nova (PropriedadeForm — sem campo 'ativa')
- Editar (PropriedadeEditForm — com campo 'ativa')
- Selecionar ativa (POST)
- Soft delete (ativa=False)
```

### 6.2 Gestão de Usuários ✅
```
/admin-sistema/usuarios/
- Listar todos
- Criar novo (hash automático de senha)
- Editar (reset de senha)
- Desativar (is_active=False)
- Vincular a propriedade (/admin-sistema/vinculos/novo/)
```

### 6.3 Gestão de Animais ✅
```
/animais/
- Listar terneiras ativas
- Listar vacas
- Criar nova terneira (cadastro manual)
- Criar nova vaca
- Visualizar ficha completa (Animal + eventos + programa)
- Editar dados cadastrais (não altera categoria)
- Gráfico peso vs meta (Chart.js)
- GMD calculado
```

### 6.4 Ciclo Reprodutivo ✅
```
/animais/vacas/<pk>/ciclo/novo/
- Criar ciclo reprodutivo (ativa gestação)
- Dados de cobertura, previsão, secagem
- Conexão com Parto (OneToOne)
```

### 6.5 Registro de Eventos ✅

**Parto:**
```
/eventos/parto/novo/<ciclo_pk>/
- Cria Animal nascido
- Cria ProgramaAcompanhamento (se fêmea)
- Atualiza ciclo.situacao
- Dispara avaliadores C5 + C6
```

**Colostragem:**
```
/eventos/colostragem/<terneira_pk>/
- Múltiplas colostragens por terneira
- Cálculo automático de tempo_apos_nascimento
- Dispara avaliadores C1 + C2 + C3
```

**Cura de Umbigo:**
```
/eventos/umbigo/<terneira_pk>/
- Registro de aplicações
- Avaliação do coto (seco, inchaço, etc)
- Dispara avaliador C4
```

**Pesagem:**
```
/eventos/pesagem/<animal_pk>/
- Histórico completo
- GMD calculado
- Dispara avaliador C7
```

**Ocorrência Sanitária:**
```
/eventos/sanitario/<animal_pk>/
- Abrir ocorrência (tipo, data, tratamento)
- Encerrar ocorrência
- Histórico preservado
```

**Vacinação:**
```
/eventos/vacinacao/<animal_pk>/
- Registrar vacina, data, lote
- Histórico completo
```

**Desaleitamento:**
```
/eventos/desaleitamento/<terneira_pk>/
- Data, método, peso, idade
- Muda categoria automaticamente (terneira → novilha)
```

**Banco de Colostro:**
```
/eventos/banco-colostro/
- CRUD de lotes
- Referência em colostragem
```

### 6.6 Programa de Acompanhamento ✅
```
/programas/
- Lista de programas ativos
- Visualizar detalhes (dias decorridos, % concluído)
- Indicador de checkpoint pendente (165-195 dias)
- Realizar checkpoint (POST)
- Checkpoint calcula automaticamente
```

### 6.7 Projeção Reprodutiva ✅
```
/programas/projecao/<terneira_pk>/
- Classificação de trajetória (atenção/crítico/em dia)
- Data prevista para IA
- Comparação com meta
```

### 6.8 Novilhas Aptas ✅
```
/programas/aptas/
- Lista de novilhas prontas para primeira IA
- Filtro por data de aptidão
```

### 6.9 Primeira IA ✅
```
/programas/ia/<terneira_pk>/
- Registrar primeira cobertura
- Muda categoria (novilha → vaca)
- Encerra escopo do programa
```

### 6.10 Dashboard ✅
```
/
- Zona 1: Alertas críticos e operacionais (10 tipos)
- Zona 2: Status (período: 30d/90d/180d)
  * Desempenho: terneiras, novilhas, nascimentos, GMD
  * Conformidade: 6 KPIs (verde/amarelo/vermelho)
  * Sanitário: diarreia, pneumonia, onfalite
  * Reprodutivo: novilhas, trajetórias, checkpoints
- Zona 3: Tendência 6 meses (4 gráficos Chart.js)
  1. Taxa colostragem ≤2h vs meta 90%
  2. GMD médio vs meta 0.75 kg/dia
  3. Incidência sanitária vs metas
  4. % terneiras dentro da curva vs meta 80%
```

### 6.11 Configurações Técnicas ✅
```
/config/
- Protocolos (versionados, CRUD)
- Metas de desenvolvimento (curvas de peso)
- Metas reprodutivas
- Critérios de conformidade (C1-C7, CRUD)
- Referenciais técnicos (9 pré-carregados)
```

### 6.12 Admin do Sistema ✅
```
/admin-sistema/
- Painel geral para superusuários
- CRUD propriedades, usuários, vínculos
- Seleção rápida de propriedade ativa
```

---

## 7. FUNCIONALIDADES PARCIAIS

### ⚠️ Sistema de Permissões por Papel
**Status:** Modelo existe, lógica NÃO implementada
- Papéis: admin, tecnico, produtor, auxiliar
- ❌ Views NÃO verificam papel
- ❌ Todos os usuários autenticados têm acesso total
- **TODO:** Implementar decorators `@permission_required` ou mixins

### ⚠️ MovimentacaoLote
**Status:** Modelo pronto, UI NÃO existe
- ✅ Lógica de "lote atual" funciona
- ❌ Sem formulário de movimentação
- **TODO:** Criar view e template para registrar movimentações

### ⚠️ ProtocoloAlimentar + RegistroAlimentacaoDiario
**Status:** Modelos completos, views/templates NÃO existem
- ❌ URLs não mapeadas
- ❌ Views não criadas
- **TODO:** Implementar interface ou remover modelos não utilizados

### ⚠️ Critérios C8-C10 (Desaleitamento)
**Status:** Códigos no modelo, avaliadores NÃO implementados
- ✅ CriterioConformidade permite C8, C9, C10
- ❌ Avaliador `avaliar_evento_desaleitamento()` não existe
- **TODO:** Implementar função ou documentar exclusão

---

## 8. DECISÕES DE DESIGN

### 8.1 Multi-Tenancy
**Decisão:** Isolamento completo por propriedade (Propriedade tem múltiplos animais, usuários, etc)
**Implementação:** Middleware injeta `request.propriedade_ativa`, queries filtram por propriedade
**Regra:** Superusuário acessa qualquer propriedade ativa; usuário comum apenas propriedades vinculadas

### 8.2 Imutabilidade de Eventos
**Decisão:** Parto, Colostragem, Pesagem, etc. são imutáveis após criação
**Motivo:** Edições invalidariam conformidades já calculadas
**Alternativa:** Permitir edição com recálculo automático (não implementado)

### 8.3 Conformidade = Avaliação Automática
**Decisão:** Ao registrar evento, avaliadores criam ResultadoConformidade automaticamente
**Implementação:** Signals ou views disparam `avaliar_evento_*()`
**Regra:** Dado ausente ≠ zero; conformidade diferencia 4 estados (conforme, nao_conforme, dado_ausente, nao_aplicavel)

### 8.4 Categoria Automática
**Decisão:** Categoria do animal muda automaticamente via eventos
- Parto: mãe permanece vaca, nascido é terneira/bezerro
- Desaleitamento: terneira → novilha (automático)
- IA: novilha → vaca (automático)

**Regra:** Nunca editar categoria manualmente pela UI

### 8.5 Lote Atual = Última MovimentacaoLote
**Decisão:** Lote não é campo direto no Animal, derivado de histórico
**Motivo:** Permite rastreabilidade completa
**Implementação:** Property que busca `ultima_movimentacao().lote`

### 8.6 Protocolos Versionados
**Decisão:** Alterar protocolo = criar nova versão, nunca editar versão existente
**Motivo:** Rastreabilidade de qual protocolo era vigente em cada data

### 8.7 Primeiro Acesso Automático
**Decisão:** Primeira propriedade sempre criada com `ativa=True`
**Implementação:** PropriedadeForm NÃO tem campo `ativa` (criação); PropriedadeEditForm TEM (edição)

---

## 9. INTEGRAÇÃO COM BANCO DE DADOS

### Desenvolvimento
```
SQLite: db.sqlite3 (local)
Conectado automaticamente por Django
```

### Produção — Opções

#### Opção A: PostgreSQL em Neon (Recomendado)
```
URL: postgresql://user:pass@ep-xxxxx.neon.tech/terneiras
Plano gratuito: 3 projetos, 3GB storage
requirements.txt já tem: psycopg2-binary==2.9.9

Passos:
1. Criar conta em neon.tech
2. Criar projeto PostgreSQL
3. Copiar URL de conexão
4. Adicionar ao .env.production: DATABASE_URL=...
5. settings.py usar dj-database-url para parse
```

#### Opção B: Supabase PostgreSQL
```
URL: postgresql://user:pass@db.xxxxx.supabase.co/postgres
Plano gratuito: 500MB storage, 2 projects
```

#### Opção C: Render PostgreSQL
```
Integrado com Render hosting
Criar no dashboard do Render
```

### Migrações em Produção
```bash
# Local (desenvolvimento):
python manage.py migrate

# Produção (via web hook ou manual):
python manage.py migrate --noinput
```

### Status Atual
```
✅ Todas migrações aplicadas (17 apps)
✅ db.sqlite3 contém dados de teste
✅ Banco pode ser resetado sem problema (dados de teste)
```

---

## 10. FRONTEND E INTERFACE

### 10.1 Template Base (base.html)
```
- Navbar com logo (static/img/logobranco.png)
- Sidebar com menu
- Seção "Administração" (apenas superusuário)
- Breadcrumb
- Conteúdo dinâmico
- Footer
- CDN: Bootstrap 5.3.3, Alpine.js 3, HTMX 1.9, Chart.js 4
```

### 10.2 Tela de Login (login.html)
```
- STANDALONE (não herda base.html)
- Background.png: 1448×1086px (arte + área verde com texto)
- Logo em card branco sobreposto
- CSS embutido (sem arquivo .css separado)
- Autenticação Django nativa
- Suporta "Lembrar-me"
```

### 10.3 Dashboard (dashboard.html)
```
- 3 zonas de layout
- Alertas com Badge (crítico=vermelho, operacional=amarelo)
- Status com KPIs (verde/amarelo/vermelho)
- 4 Gráficos Chart.js (tendência 6 meses)
- Responsivo (Bootstrap grid)
```

### 10.4 Formulários
```
- Bootstrap form classes (form-control, form-label, etc)
- Validação Django side + Alpine.js side
- Select2 para ForeignKey (se necessário)
- HTMX para operações AJAX
```

### 10.5 Tabelas
```
- Bootstrap table classes
- Paginação (se >20 linhas)
- Ordenação por coluna
- Filtros inline (Alpine.js)
```

---

## 11. SEGURANÇA E AUTENTICAÇÃO

### 11.1 Autenticação
```
✅ Django Auth integrado
✅ @login_required em todas as views
✅ Middleware PropriedadeMiddleware valida propriedade ativa
✅ Usuário sem propriedade vê página "sem_propriedade.html"
```

### 11.2 Autorização (PENDENTE)
```
⚠️ Sistema de papéis existe mas NÃO é verificado
⚠️ Qualquer usuário autenticado acessa tudo
TODO: Implementar decorators de permissão
```

### 11.3 CSRF Protection
```
✅ Token CSRF em todos os forms ({% csrf_token %})
✅ Middleware CSRF ativo
✅ settings.py: CSRF_TRUSTED_ORIGINS (para produção)
```

### 11.4 Variáveis Sensíveis
```
.env (NÃO versionado):
- SECRET_KEY: deve ser forte em produção
- DEBUG: False em produção
- ALLOWED_HOSTS: incluir domínio de produção

⚠️ CRÍTICO: SECRET_KEY atual é insegura (django-insecure-...)
TODO: Gerar nova chave para produção
```

### 11.5 Headers de Segurança
```
✅ SecurityMiddleware ativo
✅ X-Frame-Options: DENY (clickjacking)
TODO: Adicionar CSP headers se necessário
```

---

## 12. DEPLOYMENT E PRODUÇÃO

### 12.1 Checklist Pré-Deploy

```
SEGURANÇA:
☐ SECRET_KEY alterada (gerar com: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
☐ DEBUG = False em .env.production
☐ ALLOWED_HOSTS inclui domínio de produção
☐ CSRF_TRUSTED_ORIGINS configurado
☐ Usar HTTPS obrigatoriamente

BANCO DE DADOS:
☐ PostgreSQL configurado (Neon/Supabase/Render)
☐ migrations executadas: python manage.py migrate --noinput
☐ Static files coletados: python manage.py collectstatic --noinput

STATIC FILES:
☐ WhiteNoise configurado (já está em settings.py)
☐ STATIC_ROOT apontando para diretório correto
☐ CDN ou servidor static configurado

APLICAÇÃO:
☐ requirements.txt revisado
☐ Variáveis de ambiente carregadas via python-decouple
☐ Logs configurados (syslog ou arquivo)
☐ Monitoramento ativo (Sentry, DataDog, etc)

BACKUP:
☐ Estratégia de backup do PostgreSQL definida
☐ Retenção de backups: mínimo 7 dias

PERFORMANCE:
☐ Cache configurado (Redis ou memcache)
☐ Database queries otimizadas (select_related, prefetch_related)
☐ Compressão gzip ativa

COMPLIANCE:
☐ Política de privacidade publicada
☐ Conformidade com LGPD (se Brasil)
☐ TLS/HTTPS obrigatório
```

### 12.2 Deploy no Render.com (Sugerido)

```
1. Criar conta em render.com
2. Conectar repositório GitHub (sammsuu274-art/TERNEIRASPRO)
3. Criar Web Service:
   - Name: terneiraspro
   - Region: us-east (ou mais próximo)
   - Branch: main
   - Build command: pip install -r requirements.txt && python manage.py collectstatic --noinput
   - Start command: gunicorn gestao_terneiras.wsgi:application
   - Environment variables:
     * SECRET_KEY=[gerar nova]
     * DEBUG=False
     * ALLOWED_HOSTS=terneiraspro.onrender.com
     * DATABASE_URL=postgresql://...
     * CSRF_TRUSTED_ORIGINS=https://terneiraspro.onrender.com

4. Criar PostgreSQL Database:
   - Name: terneiraspro-db
   - Database: terneiras
   - User: terneiras_user
   - Copiar DATABASE_URL

5. Deploy automático: cada push em main dispara build
```

### 12.3 Dependências para Produção
```
Adicionar a requirements.txt:
- gunicorn==21.2.0 (WSGI server)
- psycopg2-binary==2.9.9 (já incluído)
- python-decouple==3.8 (já incluído)
- django-environ (alternativa a decouple, opcional)
- dj-database-url (parse DATABASE_URL, opcional)
```

### 12.4 WSGI Application (gestao_terneiras/wsgi.py)
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
application = get_wsgi_application()

# Gunicorn usará: gunicorn gestao_terneiras.wsgi:application
```

### 12.5 Cloudflare Tunnel (Futuro)
```
⚠️ AINDA NÃO CONFIGURADO

cloudflared versão 2026.8.2 instalado no Raspberry Pi
Aguardando autorização para:
1. Login no Cloudflare: cloudflared tunnel login
2. Criar túnel: cloudflared tunnel create terneiras
3. Configurar rota DNS
4. Iniciar tunnel automaticamente via systemd

Benefício: expõe TERNEIRAS sem abrir portas no roteador
```

---

## 13. CHECKLIST DE IMPLEMENTAÇÃO

### Antes do Deploy

```
CÓDIGO:
☐ Nenhum arquivo .py com TODO não resolvido
☐ Nenhuma importação não utilizada (linter: flake8)
☐ Tipo hints em functions críticas
☐ Docstrings em models e views principais
☐ Testes unitários para avaliadores (C1-C7)
☐ Testes de integração para fluxos críticos (parto → programa → checkpoint)

BANCO:
☐ Migrações sem conflitos
☐ Dados de teste removidos (ou reset script criado)
☐ Índices em colunas frequentemente consultadas
☐ Constraints em unique_together, foreign keys

FRONTEND:
☐ Nenhum console.error em navegador
☐ Responsivo em mobile (viewport meta tag)
☐ Acessibilidade básica (labels, alt text, aria-label)
☐ Performance: Lighthouse score >80

DOCUMENTAÇÃO:
☐ README.md com quick start
☐ .env.production.template completo
☐ Guia de deployment em DEPLOY.md
☐ Troubleshooting em TROUBLESHOOTING.md

SEGURANÇA:
☐ Senhas não logadas (settings.py)
☐ SQL injection prevenido (Django ORM)
☐ XSS prevenido (template escaping)
☐ CSRF protection ativa
☐ Sem hardcoded secrets em código
```

### Após Deploy (Testes em Produção)

```
FUNCIONALIDADE:
☐ Login/logout funciona
☐ Múltiplas propriedades isoladas
☐ Criar animal e registrar parto
☐ Avaliadores disparam e criam conformidades
☐ Dashboard calcula e exibe KPIs
☐ Gráficos renderizam corretamente

PERFORMANCE:
☐ Dashboard carrega em <3s
☐ Listagem de 1000 animais em <2s
☐ Nenhuma N+1 query
☐ Static files servidos com cache

MONITORAMENTO:
☐ Logs centralizados
☐ Alertas para erros críticos
☐ Uptime monitored (Pingdom, UptimeRobot)
☐ Database backups automáticos
```

---

## 14. PROBLEMAS CONHECIDOS E PENDÊNCIAS

### 🔴 CRÍTICOS

#### 1. System de Papéis Não Funcional
**Problema:** Papéis (admin, tecnico, produtor, auxiliar) existem no modelo mas views NÃO verificam
**Impacto:** Qualquer usuário autenticado acessa tudo
**Solução:** Implementar decorators `@permission_required` em views críticas
**Prioridade:** 🔴 CRÍTICA (segurança)

#### 2. SECRET_KEY Insegura
**Problema:** Configuração padrão: `django-insecure-...`
**Impacto:** Vulnerabilidade em produção
**Solução:** Gerar chave forte (ver 12.1)
**Prioridade:** 🔴 CRÍTICA (segurança)

#### 3. Template form_colostragem.html usa {{ meta_volume }} não passado
**Problema:** View `registrar_colostragem()` não passa `meta_volume` no contexto
**Impacto:** Campo exibe vazio
**Solução:** Calcular `meta_volume = peso_nascimento * 0.10` e passar no contexto
**Prioridade:** 🟠 ALTA (usabilidade)

### 🟠 ALTOS

#### 4. Critérios C8-C10 (Desaleitamento) Não Implementados
**Problema:** Avaliadores para desaleitamento não existem
**Impacto:** Desaleitamento registrado fora de padrões sem alerta
**Solução:** Implementar `avaliar_evento_desaleitamento()` ou documentar exclusão
**Prioridade:** 🟠 ALTA (conformidade)

#### 5. MovimentacaoLote Sem UI
**Problema:** Modelo pronto mas sem formulário
**Impacto:** Lotes não podem ser gerenciados pela UI
**Solução:** Criar view e template
**Prioridade:** 🟠 ALTA (funcionalidade)

#### 6. Recálculo Após Edição Não Automático
**Problema:** Editar data_nascimento não recalcula conformidades/projeções
**Impacto:** Dados podem ficar inconsistentes
**Solução:** Implementar recálculo automático ou bloquear edição de dados críticos
**Prioridade:** 🟠 ALTA (integridade)

### 🟡 MÉDIOS

#### 7. Metas dos Gráficos Hardcoded
**Problema:** Valores fixos em `_buscar_metas_graficos()`
**Impacto:** Metas não customizáveis por propriedade
**Solução:** Vir de CriterioConformidade
**Prioridade:** 🟡 MÉDIA (configurabilidade)

#### 8. ProtocoloAlimentar Sem Interface
**Problema:** Modelos existem mas views/templates não
**Impacto:** Funcionalidade planejada inacessível
**Solução:** Implementar ou remover modelos não utilizados
**Prioridade:** 🟡 MÉDIA (cleanup)

#### 9. Ausência de Validações Técnicas
**Problema:** Sistema aceita peso absurdo, idade incompatível, etc
**Impacto:** Qualidade dos dados comprometida
**Solução:** Implementar validadores em models
**Prioridade:** 🟡 MÉDIA (qualidade)

#### 10. Conformidade Sem Interface de Consulta
**Problema:** Dados existem mas UI só mostra KPIs agregados
**Impacto:** Falta visibilidade operacional
**Solução:** Criar tela de detalhamento de não-conformidades
**Prioridade:** 🟡 MÉDIA (visibilidade)

---

## REFERÊNCIAS

### Documentação Oficial
- Django 4.2: https://docs.djangoproject.com/en/4.2/
- Bootstrap 5: https://getbootstrap.com/docs/5.3/
- Alpine.js: https://alpinejs.dev/
- HTMX: https://htmx.org/
- Chart.js: https://www.chartjs.org/

### Configuração de Deploy
- Render.com: https://render.com/docs
- Neon PostgreSQL: https://neon.tech/docs
- Gunicorn: https://gunicorn.org/
- WhiteNoise: https://whitenoise.evans.io/

### Segurança
- OWASP: https://owasp.org/www-project-django-security/
- Django Security: https://docs.djangoproject.com/en/4.2/topics/security/

---

## CONTATO E DÚVIDAS

Para dúvidas técnicas durante a implementação:
1. Consulte `DOCUMENTACAO_AGENTE.md` (referência técnica)
2. Verifique `CHANGELOG.md` (histórico de alterações)
3. Leia `TELA_LOGIN_LAYOUT.md` (design da login)
4. Revise `.kiro/steering/projeto.md` (regras permanentes)

---

**Documento preparado para implementação**  
**Versão: 1.0 — Agosto 2026**  
**Status: Pronto para Desenvolvimento**
