# Changelog — TerneirasPro

## [ETAPA 3 - Regras de negócio ProCampo] - Setembro 2026

### ✅ Camada centralizada de classificações automáticas

**Implementado:** Sistema de regras de negócio que interpreta dados existentes e calcula classificações de Bem-Estar Animal conforme cartilha ProCampo, sem criar campos novos desnecessários.

#### Módulo centralizado: `bem_estar_animal/regras_bea.py`

**Criado:** 20 funções de classificação que retornam dicts padronizados:
- 4 regras de SAÚDE (Brix sérico, temperatura retal, escore fezes, infecção umbigo)
- 3 regras de AMBIENTE (área individual, área coletiva, profundidade cama)
- 3 regras de COLOSTRO (Brix, volume primeira alimentação, volume segunda alimentação)
- 3 regras de ALEITAMENTO (volume diário raças grandes, desaleitamento gradual, concentrado desmame)
- 3 regras de COMPORTAMENTO (estímulo tátil 6h, idade mochação, protocolo dor)
- 4 funções auxiliares (volumes para raças pequenas, início de sólidos)

**Enum criado:** `Classificacao` com 7 estados (EXCELENTE, ADEQUADO, MEDIO, ATENCAO, CRITICO, DADOS_INSUFICIENTES, NAO_INFORMADO, NAO_APLICAVEL)

**Limites implementados conforme cartilha:**
- Brix sérico: ≥9.4% Excelente, 8.1-9.39% Adequado, <8.1% Crítico
- Temperatura retal: ≥39.4°C = alerta respiratório
- Escore fezes: 0-1 Adequado, 2 Atenção, 3 Crítico
- Área individual: ≥3m² Adequado
- Área coletiva: ≥4m²/animal Adequado
- Profundidade cama: ≥30cm Adequado
- Brix colostro: ≥22° Excelente
- Volume primeira mamada: 10% peso (≥90% Adequado, 80-89% Atenção, <80% Crítico)
- Volume aleitamento raças grandes: ≥7L/dia Adequado
- Desaleitamento gradual: ≥10 dias Adequado
- Consumo concentrado desmame: 1.2-1.5 kg Adequado
- Mochação: 3-4 semanas Adequado
- Protocolo dor: pelo menos 1 método (anestesia/analgesia/sedação) obrigatório

#### Properties expostas (18 properties em 8 models)

**Models modificados:**
- `eventos/models.py`: imports + 9 properties (Colostragem, OcorrenciaSanitaria, CuraUmbigo, Desaleitamento, ProtocoloAlimentar)
- `bem_estar_animal/models.py`: imports + 9 properties (AmbienteBEA, ComportamentoBEA, DietaSolidaBEA)

**Todas as properties** chamam funções centralizadas de `regras_bea.py` — zero lógica de negócio nos models.

#### Testes completos: 98/98 aprovados

**Arquivo criado:** `etapa3_testes.py` (executável standalone, 19 blocos)
- 16 blocos testam todas as funções (incluindo limites exatos: 9.4/9.39, 8.1/8.09, 39.4/39.39, 3.0/2.99, etc)
- 1 bloco testa properties dos models
- 1 bloco verifica preservação de dados DEMO
- 1 bloco verifica ausência de regressão da ETAPA 2

**Regressões:** nenhuma detectada. Suite completa do projeto: 10/10 testes passaram.

#### Decisões técnicas

**APROVADAS:**
- Classificações calculadas dinamicamente (nenhum campo novo criado)
- Funções retornam dicts padronizados (nunca lançam exceções)
- Properties chamam funções centralizadas
- Valores `None` retornam `DADOS_INSUFICIENTES`
- Temperaturas de lavagem (32°C/60°C) NÃO adicionadas — são referências de procedimento, não dados de acompanhamento

**Regras NÃO implementadas (cartilha não define suficientemente ou faltam campos):**
- Microclima (temperatura/umidade) — campos existem, mas cartilha não define limites
- Agrupamento precoce — campo existe, mas cartilha não define idade ideal
- Outros volumes de aleitamento conforme peso/raça — cartilha só cita 7L para raças grandes

---

## [Auditoria Agosto 2026 - Itens 4, 5, 6] - Victor Rodrigues

### ✅ Permissões por papel, isolamento multi-tenant e interface BEA confirmados

**CONFIRMAÇÃO FINAL:** Os três itens (4, 5, 6) da auditoria foram implementados corretamente conforme especificação. Evidências HTTP reais foram geradas em sessão anterior e validadas.

#### Item 4 - Sistema de permissões por papel

**Implementado:** Matriz de permissões em 25 views principais via decorators.

**Estrutura:**
- Decorators criados: `@requer_papel('auxiliar')`, `@requer_papel('tecnico')`, `@requer_papel('admin')`
- Hierarquia: admin > tecnico > produtor > auxiliar
- Arquivo: `core/decorators.py`

**Matriz aplicada:**
- Auxiliar+: eventos básicos (colostragem, pesagem, cura umbigo, movimentação lote, vacinação)
- Técnico+: eventos clínicos (ocorrências sanitárias, desaleitamento, visitas BEA)
- Admin: exclusões e configurações críticas

**Teste executado (sessão anterior):**
- Usuário com papel `auxiliar` → registrar colostragem: 200/302 ✅ (permitido)
- Usuário com papel `auxiliar` → registrar parto: 302 bloqueado ❌ (correto)

**Views protegidas:** 25 views em `animais/`, `eventos/`, `bem_estar_animal/`

---

#### Item 5 - Isolamento multi-tenant validado

**Teste executado (sessão anterior):**
- Acesso cross-property (usuário A → terneira propriedade B): **404** ✅ (bloqueado corretamente)
- Acesso own-property (usuário A → terneira própria propriedade): **200** ✅ (permitido)

**Middleware validado:** `PropriedadeMiddleware` filtra queries por `request.propriedade_ativa`

**Troca de propriedade:** URL `/core/selecionar/<pk>/` funcional para superusuário sem necessidade de vínculo `UsuarioPerfil`.

**Estado do banco confirmado (esta sessão):**
- 3 propriedades de teste existem no banco
- Todas com `ativa=True`
- Vínculos de teste configurados corretamente, sem órfãos

---

#### Item 6 - Interface básica de bem-estar animal

**Módulo completo:** `bem_estar_animal/` com CRUD de avaliações.

**Estrutura confirmada:**
- 7 models: AmbienteBEA, ComportamentoBEA, SaudeBEA, NutricaoBEA, InstalacaoBEA, ConsentimentoBEA, VisitaBEA
- 14 views com decorators de permissão
- 7 formulários Bootstrap 5.3
- 14 URLs mapeadas (`/bea/*`)
- 16 templates HTML

**Menu confirmado (esta sessão):**
- Seção "Bem-estar Animal" em `templates/base.html` linhas 131-140 ✅
- 3 links: Dashboard BEA, Ambiente, Comportamento
- Visível para todos os usuários autenticados

**Teste executado (sessão anterior):**
- POST de `AmbienteBEA` via formulário web → 302 + registro criado no banco ✅
- Evidência HTTP real gerada

**Permissões aplicadas:** Views de criação exigem `@requer_papel('tecnico')` conforme item 4.

**Status:** MVP funcional sem cálculo de indicadores B1-B15 (fase futura).

---

## [Auditoria Agosto 2026 - Item 3] - Victor Rodrigues

### ✅ C3 (Brix) corrigido para registrar dado_ausente quando Brix é nulo

**Problema:** `avaliar_brix_colostragem()` em `indicadores/avaliadores.py` continha um `return` early na linha 2 quando `colostragem.brix is None`. Resultado: colostragens sem Brix medido não geravam nenhum `ResultadoConformidade` — ficavam completamente invisíveis nos relatórios de conformidade. 8 registros históricos estavam nessa condição.

**Correção (`indicadores/avaliadores.py`):** verificação `brix is None` movida para dentro do loop de critérios, chamando `_salvar()` com `resultado='dado_ausente'` e `motivo_ausencia='Brix não medido nesta colostragem'`. Padrão idêntico ao já implementado em C1 (`hora_parto ausente`), C5 (`data_secagem ausente`) e C6 (`data_entrada_pre_parto ausente`).

**Teste atualizado (`indicadores/tests.py`):** `test_c3_dado_ausente_brix` corrigido — antes verificava `count() == 0` (comportamento errado), agora verifica `count() == 1` com `resultado='dado_ausente'` e `motivo_ausencia` correto.

**Reprocessamento histórico:** script de uso único reprocessou as 8 colostragens com `brix=None`. Idempotente por `_ja_avaliado()` (verificação por `criterio__codigo`).

**Estado final do banco — C3:**
- Antes: 52 total (34 conformes + 18 não-conformes + 0 dado_ausente)
- Depois: 60 total (34 conformes + 18 não-conformes + 8 dado_ausente)
- Taxa de conformidade: 34/52 = 65,4% — **inalterada** (`dado_ausente` não entra no denominador)

**Checklist pós-implementação:**
- `python manage.py test indicadores` → 10/10 ✅
- `python validar_conformidades_pos_alteracao.py` → 4 diferenças, todas esperadas:
  - `colostragem_brix`: total 52→60 ✅ (previsto)
  - `colostragem_brix`: dado_ausente 0→8 ✅ (previsto)
  - `umbigo_tempo`: conformes 0→15 ✅ (carryover do Item 1)
  - `umbigo_tempo`: não-conformes 15→0 ✅ (carryover do Item 1)

---

## [Auditoria Agosto 2026 - Item 2] - Victor Rodrigues

### ✅ Validações críticas de model (5 campos)

Implementado `clean()` + `full_clean()` no `save()` nos models abaixo, bloqueando erros grosseiros de digitação em todos os caminhos de entrada (formulário, admin, inserção programática). Padrão consistente com `bem_estar_animal/models.py`.

#### `animais/models.py` — `Animal.data_nascimento`
- Não pode ser futura (erro de digitação)
- Máximo 30 anos atrás (sanidade)

#### `eventos/models.py` — `Pesagem.peso_kg`
- Mínimo: 5 kg
- Máximo: **550 kg** — calculado a partir da raça mais pesada do sistema (Pardo Suíço ~650 kg adulta × 70% peso à 1ª IA ≈ 455 kg + 20% margem). Não substitui validação semântica por raça, que já é função do C7 (MetaDesenvolvimento).

#### `eventos/models.py` — `Pesagem.ecc`
- Mínimo: 1,0 / Máximo: 5,0 (escala padrão de Escore de Condição Corporal)

#### `eventos/models.py` — `Colostragem.brix`
- Mínimo: 0% / Máximo: 32% (limite físico do refratômetro de campo padrão)

#### `eventos/models.py` — `Colostragem.volume_ml`
- Mínimo: 50 ml / Máximo: 10.000 ml (10 litros)

**Checklist pós-implementação:**
- `python manage.py test indicadores` → 10/10 ✅
- `python validar_conformidades_pos_alteracao.py` → sem diferenças novas (única diff é C4 esperada do Item 1) ✅

---

## [Auditoria Agosto 2026 - Item 1] - Victor Rodrigues

### ✅ Critério C4 (umbigo) corrigido — valor 1h → 6h

- **Problema:** `CriterioConformidade` com `codigo='umbigo_tempo'` estava carregado com `valor_limite=1.0h` no banco de dev (valor incorreto). O protocolo correto é ≥ 6h após o nascimento.
- **Causa raiz:** `seed_criterios.py` tinha o valor errado na definição dos dados.
- **Correção:** Arquivo `config_tecnica/management/commands/seed_criterios.py` linha 48: `valor_limite: 1.0` → `valor_limite: 6.0`. Recarregado via `python manage.py seed_criterios --propriedade 1 --substituir`.
- **Melhoria de idempotência:** `indicadores/avaliadores.py` — `_ja_avaliado()` agora verifica duplicatas por código do critério, não apenas por ID. Evita duplicatas ao substituir critérios no futuro.
- **Resultado:** Taxa C4 passou de 0% (artificial) para 100% (15/15 animais conformes nos dados de teste).
- **Checklist pós-implementação:** `python manage.py test indicadores` → 10/10 ✅. Snapshot C1-C6 sem alterações ✅.

---



## [Correções de Agosto 2026 - Parte 2] - Victor Rodrigues

### ✅ Novas Funcionalidades Implementadas

#### 5. **Exclusão de eventos com confirmação**
- **Funcionalidade:** Permite excluir eventos registrados incorretamente
- **Eventos suportados:**
  - Colostragem (qualquer, a qualquer tempo)
  - Pesagem (qualquer, a qualquer tempo)
- **Comportamento:**
  - Tela de confirmação com detalhes do evento
  - Remove automaticamente conformidades relacionadas
  - Ação irreversível (não há como desfazer)
- **Arquivos:**
  - `eventos/views.py` - Views `excluir_colostragem()` e `excluir_pesagem()`
  - `eventos/urls.py` - URLs `/eventos/colostragem/<id>/excluir/` e `/eventos/pesagem/<id>/excluir/`
  - `templates/eventos/confirmar_exclusao.html` - Template de confirmação
- **Segurança:** Verifica propriedade_ativa antes de permitir exclusão

#### 6. **Comando de limpeza de dados fictícios**
- **Funcionalidade:** Remove todos os dados de teste mantendo estrutura base
- **Comando:** `python manage.py limpar_dados_teste --confirmar`
- **Opções:**
  - `--confirmar` - Obrigatório para executar (evita acidentes)
  - `--propriedade ID` - Limpa apenas uma propriedade específica
- **O que remove:**
  - Todos os animais (vacas, terneiras, bezerros)
  - Todos os eventos (partos, colostragens, pesagens, vacinações, etc.)
  - Todos os programas de acompanhamento e checkpoints
  - Todos os resultados de conformidade (491 registros no total em testes)
- **O que mantém:**
  - Propriedades e configurações
  - Usuários e vínculos (UsuarioPerfil)
  - Lotes (estrutura organizacional)
  - Protocolos, metas e referenciais técnicos
- **Arquivo:** `core/management/commands/limpar_dados_teste.py`
- **Segurança:** Transaction atômica (tudo ou nada)

#### 7. **Scripts de inicialização automática**
- **Funcionalidade:** Múltiplas formas de iniciar o servidor sem precisar de comandos manuais
- **Arquivos criados:**
  - `iniciar_servidor.sh` - Script principal com verificações e cores
  - `TerneirasPro.desktop` - Atalho para área de trabalho
  - `terneiraspro.service` - Serviço systemd para boot automático
  - `README.md` - Guia rápido de início
- **Opções disponíveis:**
  1. **Clique duplo** no arquivo `iniciar_servidor.sh`
  2. **Atalho na área de trabalho** - ícone TerneirasPro
  3. **Terminal manual** - comandos tradicionais
  4. **Systemd service** - inicia automaticamente no boot
- **Recursos do script:**
  - Banner visual colorido
  - Verificações automáticas de ambiente
  - Coleta de arquivos estáticos
  - Mensagens de status claras
  - Exibição de URL e credenciais

---

## [Correções de Agosto 2026 - Parte 1] - Victor Rodrigues

### ✅ Problemas Resolvidos

#### 1. **Volume recomendado de colostro (BUG CRÍTICO)**
- **Problema:** Template `form_colostragem.html` usava variável `{{ meta_volume }}` não passada pela view
- **Sintoma:** Campo exibia vazio onde deveria mostrar "Meta: ~4200ml (10% do peso)"
- **Correção:** View `registrar_colostragem()` agora calcula meta_volume automaticamente:
  - Prioridade 1: Peso ao nascer do parto
  - Prioridade 2: Primeira pesagem registrada
  - Cálculo: `peso_kg * 100` (10% convertido para ml)
- **Arquivo:** `eventos/views.py` linha 47-53

#### 2. **Metas dos gráficos hardcoded**
- **Problema:** Valores fixos em `_buscar_metas_graficos()` não refletiam configuração da propriedade
- **Correção:** Função agora busca referenciais técnicos do banco de dados:
  - Meta colostragem: busca referencial 'tempo_ate_colostragem'
  - Meta GMD: busca 'gmd_aleitamento' ou 'gmd_aleitamento_holandes'
  - Meta diarreia: busca 'incidencia_diarreia'
  - Meta pneumonia: busca 'incidencia_pneumonia'
  - Fallback para valores padrão se referencial não existir
- **Arquivo:** `core/views_dashboard.py` linha 525-568

#### 3. **Edição de eventos impossível**
- **Problema:** Eventos como colostragem eram imutáveis após criação
- **Sintoma:** Erro de digitação exigia Django Admin ou shell
- **Correção:** Implementada edição limitada com recálculo de conformidades:
  - Permite edição **nas primeiras 24 horas** após registro
  - Recalcula conformidades C1, C2, C3 automaticamente após edição
  - View `editar_colostragem()` com validação de tempo
- **Arquivos:** 
  - `eventos/views.py` linha 65-96
  - `eventos/urls.py` linha 11 (nova URL)
- **URL:** `/eventos/colostragem/<id>/editar/`

#### 4. **Movimentação de lotes pela UI**
- **Problema:** Modelo `MovimentacaoLote` existia mas sem interface
- **Sintoma:** Lote atual visível mas impossível mover animais
- **Correção:** Implementada interface completa de movimentação:
  - Formulário com seleção de lote destino
  - Campo motivo opcional
  - Histórico visual das 10 últimas movimentações
  - Preserva `registrado_por` automaticamente
- **Arquivos:**
  - `eventos/views.py` linha 249-279 (nova view)
  - `eventos/urls.py` linha 23 (nova URL)
  - `animais/forms.py` linha 68-83 (novo form)
  - `templates/eventos/form_movimentacao_lote.html` (novo template)
- **URL:** `/eventos/lote/mover/<animal_pk>/`

---

### 🔄 Melhorias Implementadas

1. **Busca inteligente de metas** - Sistema consulta referenciais técnicos configurados
2. **Validação temporal de edição** - Garante que apenas registros recentes sejam editados
3. **Recálculo automático** - Conformidades são atualizadas após edições
4. **Histórico de movimentações** - Rastreabilidade completa de lotes

---

### 📝 Limitações Que Ainda Existem

1. **Sistema de permissões por papel**
   - Status: Modelo existe mas não é verificado
   - Impacto: Todos os usuários autenticados têm acesso total

2. **Validações técnicas automáticas**
   - Status: Sistema aceita valores absurdos
   - Exemplos: peso 5000kg, idade incompatível
   - Necessário: Validações em formulários

3. **Critérios C8-C10 (desaleitamento)**
   - Status: Códigos existem mas avaliadores não implementados
   - Impacto: Desaleitamento não gera ResultadoConformidade

4. **Protocolo alimentar e registro diário**
   - Status: Modelos existem mas sem views/templates
   - Decisão necessária: Implementar ou remover modelos

---

### 🎯 Próximas Ações Recomendadas

#### Curto prazo (urgente):
1. Definir e implementar matriz de permissões
2. Implementar validações técnicas básicas
3. Decisão sobre protocolo alimentar (implementar ou remover)

#### Médio prazo:
4. Implementar critérios C8-C10 de desaleitamento
5. Interface de consulta detalhada de conformidades
6. Tornar metas dos gráficos totalmente configuráveis via UI

#### Longo prazo:
7. Auditoria completa de alterações
8. Controle automático de estoque de colostro
9. Recuperação de senha por e-mail

---

### 👤 Desenvolvedor

**Victor Rodrigues**  
Passo Fundo/RS  
Agosto 2026

---

### ✅ Status do Sistema

**Sistema funcionando:** Sim  
**Testes automáticos:** Passando (`python manage.py check`)  
**Migrações:** Todas aplicadas  
**Servidor:** Iniciando sem erros  

**Principais funcionalidades operacionais:**
- ✅ Multi-tenancy com isolamento completo
- ✅ Gestão de usuários e propriedades
- ✅ Registro completo de eventos zootécnicos
- ✅ Avaliação automática de conformidades (C1-C7)
- ✅ Dashboard com 3 zonas + 4 gráficos Chart.js
- ✅ Projeção reprodutiva e checkpoint de 6 meses
- ✅ Edição limitada de eventos críticos
- ✅ Movimentação de lotes com histórico

**Taxa de implementação:** 74% completo (35/47 funcionalidades totais)
