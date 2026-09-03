# 🎬 ROTEIRO DE GRAVAÇÃO — TerneirasPro
## Demonstração Profissional do Sistema

> **Data:** Agosto 2026  
> **Sistema:** TerneirasPro v4.2.16  
> **Dados:** Carga fictícia coerente com 3 cenários (BOM, MÉDIO, RUIM)

---

## 🎯 OBJETIVO DA DEMONSTRAÇÃO

Mostrar o TerneirasPro como um sistema integrado de gestão técnica da recria de terneiras, desde o parto até a primeira inseminação, com:

- Acompanhamento completo do histórico
- Cálculos automáticos de indicadores
- Alertas inteligentes
- Dashboard com KPIs
- Gráficos interativos
- Conformidade e qualidade de manejo

---

## ⏱️ DURAÇÃO RECOMENDADA

- **Rápida (5-7 min):** Apenas dashboard + 1 terneira
- **Completa (12-15 min):** Dashboard + 3 terneiras + programas + alertas
- **Técnica (20-25 min):** Completa + detalhes de conformidade + cálculos

---

## 🚀 PREPARAÇÃO

### 1. Iniciar o servidor

```bash
cd ~/TERNEIRAS
./iniciar_servidor.sh
```

**Esperado:** Servidor iniciando em `http://127.0.0.1:8000`

### 2. Fazer login

- URL: http://127.0.0.1:8000
- Login: **admin**
- Senha: **admin123**

**Esperado:** Direcionamento automático para Dashboard

---

## 📊 PARTE 1: DASHBOARD (2-3 min)

### O que mostrar

**Localização:** `/` (página inicial)

#### Zona 1 — Alertas
- ✅ **Banner verde:** "Tudo em dia" (sistema sem alertas críticos)
- ✅ **Alertas operacionais:** Checkpoints pendentes, sem pesagem recente, etc.

**O que contar:**
- "O sistema monitora 10 tipos de alertas em tempo real"
- "Alertas críticos em vermelho, operacionais em amarelo"
- "Aqui mostramos apenas os críticos agora para a propriedade"

#### Zona 2 — Status (KPIs)
- **Período:** 30/90/180 dias
- **Desempenho:** Quantas terneiras ativas, nascimentos (F/M), GMD médio
- **Conformidade:** 6 KPIs (colostragem tempo, volume, Brix, umbigo, dias secos, peso/idade)
- **Sanitário:** Incidência de diarreia, pneumonia
- **Reprodutivo:** Novilhas, trajetórias, checkpoints

**O que mostrar:**
- "Vamos ver o status dos últimos 90 dias"
- Apontar para KPIs com cores (verde = bom, amarelo = atenção, vermelho = crítico)
- "Os indicadores de conformidade são calculados automaticamente"

#### Zona 3 — Gráficos de tendência (6 meses)
1. **Colostragem ≤2h (%)** — mostra se primeira colostragem foi rápida
2. **GMD aleitamento (kg/dia)** — crescimento diário
3. **Incidência sanitária (%)** — diarreia e pneumonia
4. **% terneiras dentro da curva** — desenvolvimento vs. meta

**O que contar:**
- "Cada gráfico tem uma meta (linha azul)"
- "Os dados vêm dos lançamentos operacionais que você vê agora"
- "Nenhum indicador é calculado manualmente"

---

## 🐄 PARTE 2: REBANHO (3-4 min)

### 2.1 Vacas/Matrizes — `/animais/vacas/`

**O que mostrar:**

Lista de 3 vacas:
- **V-001-H — Valeria** (Holandês) — Cenário BOM
- **V-002-H — Eva** (Holandês) — Cenário MÉDIO
- **V-003-J — Jara** (Jersey) — Cenário RUIM

**Clicar em V-001-H (Valeria):**

1. **Dados cadastrais:** Identificação, raça, data nascimento
2. **Ciclo reprodutivo:** Data cobertura, previsão parto, secagem, pré-parto
3. **Status:** "Ciclo encerrado — Parto realizado"

**O que contar:**
- "Valeria é matriz Holandês, com ciclos reprodutivos rastreados"
- "Cada ciclo gera uma terneira. Depois do parto, o sistema começa a acompanhar a filha"
- "Os dias secos (60 dias) e pré-parto (21 dias) são avaliados automaticamente"

### 2.2 Terneiras/Novilhas — `/animais/`

**Localização:** Menu → "Rebanho" → "Terneiras"

**O que mostrar:**

Lista de 3 novilhas (antes eram terneiras, agora foram desaleitadas):
- **T-101-H** — De Valeria (BOM)
- **T-102-H** — De Eva (MÉDIO)
- **T-103-J** — De Jara (RUIM)

**Clicar em T-101-H (melhor desenvolvimento):**

#### Ficha da novilha

**Seção 1: Dados cadastrais**
- Identificação, raça, data nascimento (idade atual)
- Categoria: "Novilha" (antes era "Terneira" até os 60 dias)
- Mãe: Valeria

**Seção 2: Origem**
- Parto: Data, hora, facilidade (0=normal), peso nascimento (42kg), vitalidade

**O que contar:**
- "Nasceu de parto normal com 42kg"
- "O sistema rastreou tudo desde o primeiro dia"

**Seção 3: Crescimento**
- **Gráfico:** Peso real vs peso meta (linha verde)
- **Pesagens:** 6 registros com GMD calculado
  - 15 dias: 55kg
  - 30 dias: 70kg
  - 45 dias: 85kg
  - 60 dias: 100kg
  - 75 dias: 115kg
  - 90 dias: 130kg
- **GMD total:** 1,0 kg/dia (excelente)

**O que contar:**
- "O GMD (Ganho Médio Diário) é calculado automaticamente"
- "Essa novilha tem ganho de 1kg por dia — excelente desenvolvimento"
- "A linha verde mostra a meta, os pontos vermelhos são as pesagens reais"

**Seção 4: Eventos sanitários**
- 2 ocorrências registradas (diarreia, pneumonia)
- Ambas curadas

**O que contar:**
- "Tivemos 2 episódios sanitários — ambos tratados e resolvidos"
- "O histórico completo fica registrado"

**Seção 5: Colostragem**
- 4 registros nos primeiros dias
- Volume, Brix, método, origem

**O que contar:**
- "Colostragem adequada (C1, C2, C3 calculadas automaticamente)"
- "Volume e qualidade (Brix) foram registrados"

**Seção 6: Desaleitamento**
- Data: 60 dias de vida
- Peso: 130kg
- Categoria automaticamente mudou de "terneira" para "novilha"

**O que contar:**
- "Desaleitamento ocorreu aos 60 dias com peso adequado"
- "O sistema automaticamente mudou a categoria"

**Seção 7: Programa de Acompanhamento**
- Status: "Encerrado"
- Dias decorridos: 180 dias ✅
- Checkpoint realizado

#### Checkpoint de 6 meses

**Clicar em "Checkpoint realizado":**

**O que mostrar:**
- Data: Aos 180 dias de vida
- **Peso na avaliação:** 290kg
- **Peso meta:** 310kg
- **% da meta atingida:** 93,5% ✅
- **GMD total no período:** 1,37 kg/dia ✅
- **Trajetória:** FAVORÁVEL ✅
- **Status:** Adequado ✅

**O que contar:**
- "Checkpoint é uma avaliação consolidada aos 6 meses"
- "Calcula GMD, peso vs meta, história sanitária, etc."
- "Trajetória FAVORÁVEL significa está pronta para reprodução"
- "Sistema avalia 10+ indicadores automaticamente"

---

## 📋 PARTE 3: COMPARAÇÃO DE CENÁRIOS (2-3 min)

**Agora mostrar as outras 2 terneiras para comparação:**

### Cenário MÉDIO — T-102-H (De Eva)

**Clicar em T-102-H:**

**Diferenças visíveis:**
- Peso ao nascer: 39,5kg (vs 42kg do BOM)
- Ganho de peso: 0,75 kg/dia (vs 1,0 kg/dia)
- Peso aos 180 dias: 250kg (vs 290kg)
- % da meta: 80,6% (vs 93,5%)
- Ocorrências: 3 episódios sanitários (vs 2)
- Trajetória: ATENÇÃO (vs FAVORÁVEL)

**O que contar:**
- "Desenvolvimento normal, mas não excelente"
- "Ainda adequado para reprodução, mas requer monitoramento"

### Cenário RUIM — T-103-J (De Jara)

**Clicar em T-103-J:**

**Diferenças críticas:**
- Peso ao nascer: 36kg (bem menor)
- Vitalidade: FRACO (vs NORMAL)
- Ganho de peso: 0,50 kg/dia (baixo)
- Peso aos 180 dias: 200kg (bem abaixo da meta)
- % da meta: 64,5% (critério)
- Ocorrências: 4 episódios sanitários (diarreia, pneumonia, onfalite, febre)
- Trajetória: DESFAVORÁVEL 🔴
- **Status checkpoint:** CRÍTICO

**O que contar:**
- "Essa novilha teve nascimento complicado e desenvolvimento abaixo da meta"
- "Sistema marcou como CRÍTICO — recomenda monitoramento intensivo"
- "Múltiplos problemas sanitários impactaram o desenvolvimento"
- "Mesmo desaleitada, pode não estar pronta para reprodução"

---

## 📊 PARTE 4: PROGRAMAS DE ACOMPANHAMENTO (2-3 min)

**Localização:** Menu → "Programas" → "Acompanhamento"

**O que mostrar:**

Lista de 3 programas (um por terneira):
- Todos encerrados (180 dias completados)
- Checkpoints realizados

**Clicar em um programa:**

**Dados do programa:**
- Data início: Data do nascimento
- Duração: 180 dias ✅
- Status: Encerrado
- **Checkpoint realizado:** Link para detalhes

**Gráfico temporal:**
- Linha do tempo: Nascimento → 6 meses → Checkpoint realizado

**O que contar:**
- "Programa de acompanhamento rastreia os primeiros 6 meses"
- "Checkpoint é automático aos 180 dias"
- "Sistema avalia mais de 10 indicadores simultaneamente"

---

## 🐮 PARTE 5: REPRODUÇÃO — NOVILHAS APTAS (1-2 min)

**Localização:** Menu → "Programas" → "Aptas à Reprodução"

**O que mostrar:**

Lista de novilhas aptas (peso e idade ok):
- **T-101-H:** PRONTA ✅ (Trajetória favorável)
- **T-102-H:** PRONTA ⚠️ (Trajetória atenção)
- **T-103-J:** QUESTIONÁVEL 🔴 (Trajetória desfavorável)

**Clicar em T-101-H:**

**Dados para reprodução:**
- **Peso atual:** 320kg
- **Meta de peso:** 302,5kg ✅
- **ECC:** 2,75 (adequado)
- **Idade:** 13,1 meses (adequada)
- **GMD:** 0,75 kg/dia (excelente)

**Ação disponível:** "Registrar primeira IA/Cobertura"

**O que contar:**
- "Essa novilha está pronta para primeira inseminação"
- "Peso, idade, ECC — tudo verificado automaticamente"
- "Após primeira IA, o escopo do sistema encerra (passou para vaca adulta)"

---

## 🐮 PARTE 5: ACOMPANHAMENTO — PROJEÇÃO REPRODUTIVA (2-3 min)

**Localização:** Menu → "Programas" → "Acompanhamento"

**O que mostrar:**

Lista de 3 projeções reprodutivas (recalculadas a cada pesagem):
- T-101-H (BOM): Pronta, data próxima
- T-102-H (MÉDIO): Atenção, data estimada mais distante
- T-103-J (RUIM): Desfavorável, muito tempo até atingir meta

**Clicar em uma projeção (T-101-H):**

**Dados exibidos:**
- **Data do cálculo:** Hoje
- **Peso atual:** 320kg
- **Peso alvo:** 340kg
- **Diferença:** 20kg
- **GMD projetado:** 1,0 kg/dia
- **Dias até meta:** ~20 dias
- **Data estimada para IA:** ~15 de Setembro
- **Idade estimada:** 13,1 meses
- **Trajetória:** FAVORÁVEL ✅

**O que contar:**
- "A projeção reprodutiva é recalculada automaticamente a cada pesagem"
- "Usa o GMD histórico para estimar quando atingirá peso alvo"
- "Trajetória mostra se desenvolveu bem (favorável), normal (atenção) ou mal (desfavorável)"
- "Animais com trajetória favorável estão prontos para primeira IA"

---

## 🚚 PARTE 6: MOVIMENTAÇÃO DE LOTES (1-2 min)

**Voltar para ficha da terneira (T-101-H):**

**Localização:** Ficha → "Lotes e movimentações"

**O que mostrar:**

Histórico de 3 movimentações:
1. **Nascimento (0 dias):** Aleitamento
   - Data: Data do parto
   - Motivo: "Nascimento — Início aleitamento"

2. **Desaleitamento (60 dias):** Pós-desaleitamento
   - Data: 60 dias após nascimento
   - Motivo: "Desaleitamento — Mudança para pós-desaleitamento"

3. **Recria (120 dias):** Recria
   - Data: 60 dias após desaleitamento
   - Motivo: "Crescimento — Mudança para recria"

**Gráfico de lotes:** Timeline mostrando as transições

**O que contar:**
- "Sistema rastreia em qual lote o animal está em cada momento"
- "Cada lote tem manejo específico: aleitamento → pós-desaleit → recria"
- "Essas mudanças são registradas com datas e motivos"
- "Permite auditoria completa do histórico de movimentação"

---

## 📊 PARTE 7: COMPARAÇÃO REPRODUTIVA (1-2 min)

**Voltar para lista de acompanhamento:**

**Mostrar as 3 projeções lado a lado:**

| Aspecto | BOM (T-101-H) | MÉDIO (T-102-H) | RUIM (T-103-J) |
|---------|---|---|---|
| **Peso atual** | 320kg | 280kg | 240kg |
| **Peso alvo** | 340kg | 340kg | 340kg |
| **GMD projeto** | 1,0 kg/d | 0,75 kg/d | 0,50 kg/d |
| **Dias até meta** | ~20 dias | ~80 dias | ~200 dias |
| **Data estimada** | Sept 2026 | Nov 2026 | Feb 2027 |
| **Trajetória** | FAVORÁVEL ✅ | ATENÇÃO ⚠️ | DESFAVORÁVEL 🔴 |

**O que contar:**
- "Essas projeções mostram claramente o impacto das decisões de manejo"
- "T-101-H (boa colostragem, sem problemas) estará pronta em ~20 dias"
- "T-102-H (colostragem reduzida) levará 4 meses — requer atenção"
- "T-103-J (múltiplos problemas) pode levar 7 meses — questionável para IA"
- "O sistema ajuda a tomar decisões sobre reprodução com base em dados reais"

---

## 🐄 PARTE 8: BANCO DE COLOSTRO (1-2 min)

**Localização:** Menu → "Eventos" → "Banco de Colostro"

**O que mostrar:**

Lista de 3 lotes:
- **Lote 1:** De Valeria, 5000ml, Brix 25,5%, Disponível ✅
- **Lote 2:** De Eva, 4000ml, Brix 22%, Disponível ✅
- **Lote 3:** De Jara, 3500ml, Brix 20,5%, Parcialmente utilizado

**O que contar:**
- "Colostro de excelente qualidade é estocado e rastreado"
- "Cada lote vincula vaca doadora, volume, Brix, data"
- "Permite usar colostro de qualidade mesmo de outros partos"

---

## 💡 PARTE 9: CONFORMIDADE E INDICADORES (2-3 min)

**Voltar ao Dashboard e apontar para:**

### Conformidades implementadas

| Código | Nome | Status | Descrição |
|--------|------|--------|-----------|
| **C1** | Colostragem — tempo | ✅ | Até 2h após parto |
| **C2** | Colostragem — volume | ✅ | ≥ 10% do peso vivo |
| **C3** | Colostragem — Brix | ✅ | ≥ 22% |
| **C4** | Cura de umbigo — tempo | ✅ | Conforme protocolo |
| **C5** | Dias secos — mínimo | ✅ | 45-75 dias |
| **C6** | Dias pré-parto | ✅ | ≥ 21 dias |
| **C7** | Peso por idade | ✅ | Conforme meta de desenvolvimento |

**O que contar:**
- "7 conformidades são calculadas automaticamente"
- "C1-C4 avaliam qualidade de manejo nos primeiros dias"
- "C5-C6 avaliam preparação da vaca mãe"
- "C7 avalia crescimento da terneira"
- "Cada conformidade tem resultado: Conforme, Não Conforme, Dado Ausente, Não Aplicável"

---

## 🎯 PARTE 9: FUNCIONALIDADES QUE NÃO CONSEGUEM DEMONSTRAR

Mencionar brevemente (fora do escopo da demonstração):

- ❌ **C8-C10** (Critérios de desaleitamento) — Planejados para próxima versão
- ❌ **Movimentação de lotes** — Modelo existe, UI não implementada
- ❌ **Protocolo alimentar** — Modelos prontos, sem interface
- ❌ **Sistema de permissões por papel** — Em desenvolvimento

**O que dizer:**
- "O sistema está em desenvolvimento contínuo"
- "Versão 4.2 cobre 74% das funcionalidades planejadas"
- "Próximas melhorias incluem X, Y, Z"

---

## ✅ ROTEIRO RÁPIDO (7-10 min)

Se tiver pouco tempo:

1. **Dashboard (1 min):** KPIs principais
2. **T-101-H (2 min):** Ficha completa + gráfico de peso
3. **Checkpoint (1 min):** Resultado e trajetória
4. **Acompanhamento (1 min):** Projeção reprodutiva
5. **Movimentação de lotes (1 min):** Timeline de lotes
6. **Banco de colostro (1 min):** Rastreabilidade
7. **Aptas à reprodução (1 min):** Status para IA

---

## 🎬 ROTEIRO COMPLETO (20-25 min)

1. Dashboard (3 min)
2. Vacas/Matrizes (2 min)
3. T-101-H — Cenário BOM (4 min)
4. T-102-H — Cenário MÉDIO (2 min)
5. T-103-J — Cenário RUIM (2 min)
6. Programas de acompanhamento (2 min)
7. Acompanhamento — Projeção reprodutiva (2 min)
8. Movimentação de lotes (1 min)
9. Aptas à reprodução (1 min)
10. Banco de colostro (1 min)
11. Conformidades e indicadores (2 min)

**Total:** ~22 minutos

---

## 📝 SCRIPT DE NARRAÇÃO

### Abertura

> "Vou mostrar o TerneirasPro, um sistema completo de gestão técnica de terneiras leiteiras.
> 
> A propriedade aqui tem 3 terneiras em diferentes estágios de desenvolvimento:
> - Uma com excelente desenvolvimento (BOM)
> - Uma com desenvolvimento normal (MÉDIO)
> - Uma com desafios que requer atenção (RUIM)
> 
> Vamos acompanhar o histórico completo delas, desde o parto até à primeira inseminação."

### No Dashboard

> "No dashboard, temos 3 zonas:
> 
> **Zona 1 — Alertas:** Monitora 10 tipos de problemas críticos e operacionais.
> 
> **Zona 2 — Status:** KPIs consolidados de desempenho, conformidade, sanitário e reprodutivo.
> 
> **Zona 3 — Tendência:** 4 gráficos mostrando 6 meses de histórico com metas."

### Ficha da terneira

> "Na ficha de cada terneira, temos:
> - Histórico completo de eventos (parto, colostragem, pesagens, vacinações, etc.)
> - Gráfico de desenvolvimento com peso real vs. meta
> - Conformidades calculadas automaticamente (7 indicadores)
> - Checkpoint aos 6 meses com avaliação consolidada
> - Trajetória reprodutiva (favorável/atenção/desfavorável)"

### Fechamento

> "O que torna o TerneirasPro diferente:
> 
> ✅ **Automação completa** — Conformidades, indicadores, alertas calculados automaticamente
> 
> ✅ **Rastreabilidade total** — Histórico completo de cada animal desde o nascimento
> 
> ✅ **Dashboard executivo** — Visão consolidada em tempo real
> 
> ✅ **Baseado em ciência** — Referenciais técnicos Embrapa + literatura
> 
> ✅ **Pronto para produção** — Sistema 74% implementado e funcional
> 
> O resultado é uma ferramenta que melhora a qualidade de manejo, reduz mortalidade, otimiza custos e prepara melhor as terneiras para a vida reprodutiva."

---

## 🎥 DICAS TÉCNICAS DE GRAVAÇÃO

### O que deixar visível na tela

- ✅ URL: http://127.0.0.1:8000 (mostra é local)
- ✅ Nome do animal na ficha (confirma rastreabilidade)
- ✅ Datas dos eventos (mostra histórico)
- ✅ Números dos indicadores (mostra automação)
- ✅ Cores dos alertas (vermelho = crítico, amarelo = operacional, verde = OK)

### O que evitar

- ❌ Dados muito privados (CNPJ real, etc.)
- ❌ Detalhes de implementação técnica
- ❌ Funcionalidades não implementadas (foco nas que existem)
- ❌ Bugs ou erro na demonstração (praticar antes!)

### Dicas de execução

- 🎯 **Não fale rápido** — Deixar tempo para os espectadores acompanharem
- 📍 **Aponte na tela** — Use mouse para destacar elementos importantes
- ⏸️ **Pause entre seções** — Deixar claro quando muda de tópico
- 🎬 **Pratique antes** — Faça um dry run da demonstração
- 📱 **Use zoom** — Aumentar fonte se demonstrar em grande tela

---

## 📞 SUPORTE

- **Manual do usuário:** Veja `MANUAL_DO_USUARIO.md`
- **Documentação técnica:** Veja `DOCUMENTACAO_AGENTE.md`
- **Changelog:** Veja `CHANGELOG.md`

---

**Última atualização:** Agosto 2026  
**Versão:** TerneirasPro 4.2.16  
**Dados de demonstração:** Carga fictícia coerente com 3 cenários (BOM/MÉDIO/RUIM)
