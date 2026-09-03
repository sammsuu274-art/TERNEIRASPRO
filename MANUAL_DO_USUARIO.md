# Manual do Usuário — TerneirasPro
> Sistema de gestão técnica de terneiras leiteiras  
> Versão: Agosto 2026 (Atualizado)

---

## 📢 NOVIDADE: Manual completamente revisado!

Este manual foi atualizado em Agosto 2026 com base em auditoria completa do sistema. Novas seções adicionadas:

✅ **Seção 27** — "O Sistema Trabalha por Você" — explica todas as 50+ automações  
✅ **Seção 28** — "Dados Mínimos para Cada Evento" — o que registrar no mínimo  
✅ **Seção 29** — "Exemplo Prático" — seguir uma terneira do parto até checkpoint  
✅ **Seção 28-39** — Conformidades C1-C7 explicadas em detalhes  
✅ **Seção 30** — Diagnóstico: "Por que minha conformidade está baixa?"  
✅ **Seção 31-40** — Limitações, novidades, atalhos, glossário  

**Se você é novo no sistema:** leia seções 1-15 em ordem (fluxo completo)  
**Se você já conhece:** vá direto para seção 27+ (novos conteúdos)  
**Se tem dúvida sobre conformidade:** vá para seção 28 (C1-C7 explicados)  

---

## 🚀 INÍCIO RÁPIDO

### 1. Acessar o sistema
1. Abra o navegador e acesse: `http://127.0.0.1:8000`
2. Faça login com suas credenciais
3. Se é o primeiro acesso, configure sua propriedade

### 2. Primeiro acesso (administrador)
Se você é o primeiro usuário do sistema:
1. Login como admin
2. Sistema redireciona automaticamente para configuração inicial
3. Preencha dados da sua propriedade (nome obrigatório)
4. Clique "Criar Propriedade"
5. Pronto! Você será direcionado para o dashboard

---

## 📋 CONFIGURAÇÃO INICIAL

### 3. Configurar referenciais técnicos
**Via terminal (uma única vez):**
```bash
cd ~/TERNEIRAS
source venv/bin/activate
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

### 4. Configurar metas de desenvolvimento
1. Vá em **Configurações** > **Metas de Desenvolvimento**
2. Clique **"Nova Meta"**
3. Preencha:
   - Nome: "Crescimento Holandês Fêmeas"
   - Raça: Holandês
   - Sexo: Fêmea
   - Ativa: Sim
4. Na próxima tela, adicione **pontos da curva de crescimento**:
   - 0 dias: 40 kg
   - 30 dias: 55 kg
   - 60 dias: 75 kg
   - 90 dias: 95 kg
   - 120 dias: 115 kg
   - 180 dias: 155 kg
5. Salvar

### 5. Configurar meta reprodutiva
1. **Configurações** > **Meta Reprodutiva** > **"Nova"**
2. Preencha:
   - Nome: "Padrão Holandês"
   - Raça: Holandês
   - Idade mínima (dias): 420 (14 meses)
   - Peso mínimo (kg): 380
   - Ativa: Sim

---

## 🐄 FLUXO OPERACIONAL COMPLETO

### 6. Cadastrar uma vaca (matriz)

**Passo 1: Criar a vaca**
1. **Rebanho** > **Vacas** > **"Nova Vaca"**
2. Preencha dados:
   - **Identificação**: Ex: 1001 (obrigatório)
   - **Nome**: Ex: Estrela (opcional)
   - **Raça**: Ex: Holandês
   - **Data de nascimento**: Se souber
   - **Situação**: Ativa
3. Salvar

**Passo 2: Criar ciclo reprodutivo**
1. Na ficha da vaca, clique **"Novo Ciclo Reprodutivo"**
2. Preencha:
   - **Número da lactação**: 1, 2, 3...
   - **Data da cobertura/IA**: Ex: 15/03/2026
   - **Touro/sêmen**: Nome do touro
   - **Previsão do parto**: Ex: 11/12/2026 (280 dias após IA)
   - **Data da secagem**: Ex: 15/10/2026 (60 dias antes)
   - **Data entrada pré-parto**: Ex: 20/11/2026 (21 dias antes)
3. Salvar

### 7. Registrar o parto

**Quando a vaca parir:**
1. **Eventos** > **Partos** ou na ficha do ciclo clicar **"Registrar Parto"**
2. **Dados do parto:**
   - **Data**: 11/12/2026
   - **Hora**: 14:30 (importante para colostragem!)
   - **Facilidade**: Normal / Assistência / Tração / Cesariana
   - **Peso ao nascer**: Ex: 42 kg (importante!)
   - **Vitalidade**: Normal / Lento / Fraco / Natimorto

3. **Dados do animal nascido:**
   - **Identificação**: Ex: 2001 (única)
   - **Sexo**: F (fêmea) ou M (macho)
   - **Raça**: Mesmo da mãe (padrão)

4. Salvar

**O que acontece automaticamente:**
- ✅ Terneira criada no sistema
- ✅ Programa de acompanhamento iniciado (se fêmea)
- ✅ Ciclo reprodutivo encerrado
- ✅ Conformidades C5 e C6 avaliadas (dias secos e pré-parto)

### 8. Primeira colostragem (CRÍTICO - nas primeiras 2 horas!)

**Imediatamente após o parto:**
1. **Eventos** > **Colostragem** ou ficha da terneira > **"Registrar Colostragem"**
2. Preencha:
   - **Data e hora**: Ex: 11/12/2026 15:00 (30 min após parto)
   - **Volume**: Ex: 4200 ml — o sistema mostra automaticamente a meta recomendada (10% do peso)
   - **Origem**: Mãe biológica / Banco / Outra vaca
   - **Método**: Mamada direta / Mamadeira / Sonda
   - **Brix**: Ex: 24% (importante medir!)
   - **Ingestão confirmada**: Sim
3. Salvar

**Conformidades automáticas:**
- ✅ C1: Tempo ≤ 2h após nascimento
- ✅ C2: Volume ≥ 10% do peso vivo
- ✅ C3: Brix ≥ 22%

**💡 Dica:** Se errar algum dado, você pode editar nas primeiras 24 horas. Vá na ficha da terneira, clique no evento e depois em "Editar".

### 9. Cuidados imediatos

**Cura do umbigo (primeiras horas):**
1. **Eventos** > **Cura Umbigo** ou ficha da terneira
2. Registre:
   - **Data/hora**: Logo após nascimento
   - **Produto**: Ex: Iodo 7%
   - **Método**: Imersão / Aspersão / Pincel
   - **Avaliação do umbigo**: Marque condições observadas
3. Salvar → ✅ C4: Tempo de cura avaliado

### 10. Acompanhamento do crescimento

**Pesagens regulares (semanal/quinzenal):**
1. **Eventos** > **Pesagem** ou ficha da terneira > **"Nova Pesagem"**
2. Registre:
   - **Data**: Ex: 18/12/2026
   - **Peso**: Ex: 48 kg (7 dias após nascimento)
   - **Método**: Balança / Fita / Estimativa
3. Salvar

**O sistema calcula automaticamente:**
- GMD (Ganho Médio Diário)
- Posição na curva de crescimento (meta vs. real)
- ✅ C7: Conformidade peso/idade

### 11. Eventos sanitários (conforme necessário)

**Se houver doença:**
1. **Eventos** > **Ocorrência Sanitária**
2. Preencha:
   - **Tipo**: Diarreia / Pneumonia / Onfalite / Outras
   - **Data início**: Quando notou
   - **Sinais clínicos**: Descreva sintomas
   - **Gravidade**: Leve / Moderada / Grave
   - **Tratamento**: Medicamentos aplicados
3. **Para encerrar**: Edite a ocorrência e marque "Data de encerramento"

**Vacinações:**
1. **Eventos** > **Vacinação**
2. Registre cada vacina com data, produto e lote

### 12. Desaleitamento (6-8 semanas)

**Quando terneira estiver pronta:**
1. **Eventos** > **Desaleitamento** ou ficha da terneira
2. Preencha:
   - **Data**: Ex: 29/01/2027
   - **Método**: Gradual / Abrupto
   - **Peso no desaleitamento**: Ex: 85 kg
   - **Idade**: Calculada automaticamente
3. Salvar

**Automático:**
- ✅ Categoria muda de "terneira" para "novilha"

**💡 Dica:** O sistema mostra o lote atual da terneira. Para mover para outro lote (ex: Pós-desaleitamento), vá na ficha da terneira e clique "Mover para Lote".

### 13. Checkpoint de 6 meses

**Entre 165-195 dias de vida:**
1. **Programas** > lista programas > encontre o programa da terneira
2. Clique **"Realizar Checkpoint"**
3. Sistema mostra relatório automático:
   - Peso atual vs. meta
   - GMD médio no período
   - Conformidades obtidas
   - Eventos sanitários
   - Recomendações
4. Clique **"Confirmar Checkpoint"**

**Automático:**
- ✅ Status do programa muda para "encerrado"
- ✅ Cálculo de projeção reprodutiva

### 14. Projeção para reprodução

**Após checkpoint:**
1. **Programas** > **"Projeção Reprodutiva"** ou ficha da novilha
2. Sistema calcula:
   - Data prevista para atingir peso mínimo
   - Data prevista para idade mínima
   - Classificação da trajetória (verde/amarelo/vermelho)

### 15. Primeira cobertura/IA (14+ meses)

**Quando novilha estiver apta:**
1. **Programas** > **"Novilhas Aptas"** (lista automática)
2. Para cada novilha apta > **"Registrar IA"**
3. Preencha:
   - **Data da cobertura**: Ex: 15/06/2027
   - **Touro/sêmen**: Nome do reprodutor
   - **Método**: Monta natural / IA
4. Salvar

**Automático:**
- ✅ Categoria muda de "novilha" para "vaca"
- ✅ Escopo do sistema encerrado para este animal

---

## 📊 DASHBOARD E MONITORAMENTO

### 16. Interpretar o dashboard

**Zona 1 - Alertas (vermelho/amarelo):**
- **Críticos**: Colostragem pendente, doença grave, peso muito baixo
- **Operacionais**: Sem pesagem >30 dias, checkpoint pendente

**Zona 2 - Status (30/90/180 dias):**
- **Desempenho**: Quantas terneiras ativas, GMD médio
- **Conformidade**: % de conformes em cada critério (C1-C7)
- **Sanitário**: Incidência de diarreia, pneumonia
- **Reprodutivo**: Quantas novilhas, checkpoints realizados

**Zona 3 - Tendência (6 meses):**
- Gráfico 1: % colostragem ≤ 2h (meta 90%)
- Gráfico 2: GMD médio (meta 0,75 kg/dia)
- Gráfico 3: % diarreia e pneumonia
- Gráfico 4: % terneiras dentro da curva peso

### 17. Interpretar conformidades

**Resultados possíveis:**
- 🟢 **Conforme**: Animal atingiu o critério
- 🔴 **Não conforme**: Animal não atingiu o critério
- ⚪ **Dado ausente**: Informação necessária não foi registrada
- ⚫ **Não aplicável**: Critério não se aplica ao animal

**Taxa de conformidade** = Conformes ÷ (Conformes + Não conformes)  
*Obs: "Dado ausente" não conta no cálculo*

---

## 🏥 CASOS ESPECIAIS

### 18. Terneira órfã ou comprada

**Se não nasceu na propriedade:**
1. **Rebanho** > **Terneiras** > **"Nova Terneira"**
2. Preencha dados básicos (identificação, data nascimento, raça)
3. **NÃO terá:** parto de origem, conformidades automáticas C1-C6
4. **Terá:** programa de acompanhamento (se data nascimento informada)

### 19. Gêmeos

**No registro do parto:**
1. Marque "Parto gemelar: Sim"
2. **Primeiro animal**: registre normalmente
3. **Segundo animal**: após salvar, clique "Adicionar gêmeo"
4. Ambos ficam vinculados ao mesmo parto

### 20. Banco de colostro

**Para gerenciar estoque:**
1. **Eventos** > **Banco de Colostro** > **"Novo Lote"**
2. Registre:
   - Data da coleta
   - Vaca doadora
   - Volume coletado (L)
   - Brix
   - Localização no freezer
3. **Para usar**: Na colostragem, selecione "Origem: Banco" e escolha o lote

### 21. Mortalidade

**Se terneira morrer:**
1. **Ficha da terneira** > **"Editar"**
2. Mude **Situação** para "Morta"
3. Preencha **Data da saída** e **Motivo**
4. Animal sai das estatísticas ativas mas histórico é preservado

### 22. Movimentação entre lotes

**Para organizar por fase de criação:**
1. **Ficha do animal** > **"Mover para Lote"**
2. Selecione:
   - **Data**: da movimentação
   - **Lote destino**: Aleitamento / Pós-desaleitamento / Recria / etc.
   - **Motivo**: Ex: "Desaleitamento realizado"
3. Salvar

**Histórico completo:** O sistema preserva todas as movimentações anteriores

### 23. Excluir eventos registrados incorretamente

**⚠️ Use com cuidado - exclusão é permanente!**

**Para excluir uma colostragem:**
1. **Ficha da terneira** > encontre a colostragem na lista
2. Clique no botão **"Excluir"** (ícone de lixeira)
3. Confirme a exclusão
4. As conformidades relacionadas também serão removidas

**Para excluir uma pesagem:**
1. **Ficha do animal** > seção de pesagens
2. Clique no botão **"Excluir"** ao lado da pesagem
3. Confirme a exclusão
4. A conformidade C7 relacionada também será removida

**Eventos que podem ser excluídos:**
- ✅ Colostragem (qualquer, a qualquer tempo)
- ✅ Pesagem (qualquer, a qualquer tempo)

**Eventos que NÃO podem ser excluídos pela UI:**
- ❌ Parto (criar animal é permanente)
- ❌ Desaleitamento (mudança de categoria é irreversível)
- ❌ IA/Cobertura (fim do escopo do sistema)

💡 **Dica:** Se precisar corrigir dados de um parto ou desaleitamento, entre em contato com o administrador do sistema ou use o Django Admin (`/admin/`)

### 24. Limpar todos os dados de teste

**Se você tem dados fictícios e quer começar do zero:**

1. Abra o terminal na pasta do projeto
2. Execute o comando:
```bash
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
source venv/bin/activate
python manage.py limpar_dados_teste --confirmar --propriedade 1
```

**O que será removido:**
- ✅ Todos os animais (vacas, terneiras, bezerros)
- ✅ Todos os eventos (partos, colostragens, pesagens, vacinações, etc.)
- ✅ Todos os programas de acompanhamento e checkpoints
- ✅ Todos os resultados de conformidade

**O que será mantido:**
- ✅ Sua propriedade e configurações
- ✅ Usuários e vínculos
- ✅ Lotes (estrutura organizacional)
- ✅ Protocolos, metas e referenciais técnicos

⚠️ **Esta ação não pode ser desfeita!** Faça backup do arquivo `db.sqlite3` antes, se necessário.

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS

### 25. Gerenciar usuários (apenas admin)

**Criar usuário:**
1. **Administração** > **Usuários** > **"Novo Usuário"** (seção vermelha na sidebar)
2. Defina login e senha
3. **Importante**: Criar usuário NÃO dá acesso! Precisa vincular.

**Vincular usuário à fazenda:**
1. **Administração** > **Vínculos** > **"Novo Vínculo"**
2. Escolha usuário, propriedade e papel:
   - **Admin**: acesso total
   - **Técnico**: veterinário/zootecnista
   - **Produtor**: proprietário
   - **Auxiliar**: funcionário
3. ⚠️ **Atenção**: No momento, todos os papéis têm o mesmo acesso (melhoria futura)

### 26. Múltiplas propriedades (apenas admin)

**Para trabalhar com várias fazendas:**
1. **Administração** > **Propriedades** > **"Nova Propriedade"**
2. Para trocar entre fazendas: use o seletor no topo da tela
3. Cada propriedade é completamente isolada (animais, eventos, configurações)

---

## ⚙️ O SISTEMA TRABALHA POR VOCÊ - AUTOMAÇÕES EXPLICADAS

### 27. Tudo que o sistema faz automaticamente

Enquanto você registra dados básicos, o TerneirasPro **automaticamente**:

#### ✅ Ao registrar um PARTO:
1. Cria a terneira/bezerro no banco de dados
2. Vincula à vaca mãe (campo `mae`)
3. Se fêmea: cria ProgramaAcompanhamento automaticamente
4. Se fêmea: define data de início = data do parto
5. Se fêmea: calcula data de checkpoint (165-195 dias depois)
6. Muda situação do ciclo reprodutivo para "encerrado_parto"
7. **Avalia C5 (dias secos)** — verifica se ≥45 e ≤75 dias
8. **Avalia C6 (dias pré-parto)** — verifica se ≥21 dias
9. Registra quem fez o registro (campo `registrado_por`)

#### ✅ Ao registrar uma COLOSTRAGEM:
1. **Avalia C1 (tempo)** — verifica se ≤2h após nascimento
2. **Avalia C2 (volume)** — verifica se ≥10% do peso vivo
3. **Avalia C3 (Brix)** — verifica se ≥22%
4. Calcula `tempo_apos_nascimento_horas` automaticamente
5. Se resultado for "Dado Ausente", explica PORQUÊ (ex: "hora_parto não registrada")

#### ✅ Ao registrar CURA DE UMBIGO:
1. **Avalia C4 (tempo)** — verifica se ocorreu nas primeiras horas
2. Cria conformidade com resultado

#### ✅ Ao registrar uma PESAGEM:
1. **Avalia C7 (peso/idade)** — compara com curva de crescimento meta
2. Calcula GMD (Ganho Médio Diário) se houver pesagem anterior
3. Interpola onde está a terneira na curva (ex: "52% entre 60 e 90 dias")
4. Marca se está dentro/fora da curva

#### ✅ Ao registrar DESALEITAMENTO:
1. Muda categoria de "terneira" para "novilha" automaticamente
2. Continua programa de acompanhamento
3. Ativa cálculo de projeção reprodutiva

#### ✅ Ao registrar PRIMEIRA IA/COBERTURA:
1. Muda categoria de "novilha" para "vaca" automaticamente
2. Encerra o escopo do sistema para esse animal
3. Marca: "A partir daqui, animal é vaca adulta"

#### ✅ No CHECKPOINT (6 meses):
1. Calcula relatório automático:
   - Peso inicial vs. peso atual
   - GMD médio do período
   - % conformidades atingidas
   - Eventos sanitários
   - Recomendações de trajetória
2. Muda status programa para "encerrado"
3. Atualiza projeção reprodutiva

#### ✅ No DASHBOARD - ALERTAS:
1. Detecta colostragem pendente (se ≥2h sem registrar)
2. Detecta pesagem ausente (se ≥30 dias sem pesar)
3. Detecta ocorrência sanitária aberta >7 dias
4. Detecta peso crítico (<90% da meta)
5. Detecta mortes recentes
6. Detecta checkpoints pendentes (165-195 dias não confirmado)
7. Mostra em vermelho 🔴 (crítico) ou amarelo 🟡 (atenção)

#### ✅ No DASHBOARD - INDICADORES:
1. Calcula "Terneiras ativas" (situacao='ativa' E categoria='terneira')
2. Calcula "Novilhas" (categoria='novilha')
3. Calcula "Nascimentos" (partos último período)
4. Calcula "GMD médio" (todas terneiras do período)
5. Calcula "Mortalidade %" (mortes / total nascidos)
6. Calcula "Incidência diarreia %" (diarreia / terneiras)
7. Calcula "Incidência pneumonia %"
8. Calcula "% na curva de peso"
9. Calcula 7 conformidades (C1-C7)

#### ✅ No DASHBOARD - GRÁFICOS:
1. Gráfico 1: % colostragem ≤2h (últimos 6 meses, com linha meta 90%)
2. Gráfico 2: GMD médio aleitamento (últimos 6 meses, com linha meta 0.75 kg/dia)
3. Gráfico 3: Incidência sanitária (diarreia + pneumonia)
4. Gráfico 4: % terneiras na curva de peso

**Resumo:** O sistema faz 50+ cálculos automáticos. Você só registra fatos básicos (data, peso, hora, etc.)

---

## 🎯 DADOS MÍNIMOS PARA CADA EVENTO

Para o sistema funcionar bem, registre **pelo menos**:

### Parto (mínimo para conformidades básicas):
- ✅ Data do parto
- ✅ **Hora do parto** ← IMPORTANTE para C1 (colostragem)
- ✅ **Peso ao nascer** ← IMPORTANTE para C2 (volume colostro)
- ✅ Sexo do nascido
- ✅ Identificação do nascido

### Colostragem (para C1, C2, C3):
- ✅ Data e hora
- ✅ Volume fornecido (ml)
- ✅ **Brix** ← Se não tiver equipamento, OK deixar vazio (será "Dado Ausente")

### Cura de umbigo (para C4):
- ✅ Data e hora

### Pesagem (para C7 e GMD):
- ✅ Data
- ✅ **Peso** ← Crítico
- ✅ Pelo menos 2 pesagens (para calcular GMD)

### Ciclo reprodutivo da vaca (para C5, C6):
- ✅ **Data de secagem** ← Para C5 (dias secos)
- ✅ **Data entrada pré-parto** ← Para C6 (dias pré-parto)

### Meta de Desenvolvimento (para C7):
- ✅ Criar para cada raça
- ✅ Adicionar pelo menos 5 pontos de curva (0, 30, 60, 90, 180 dias)

---

## 📈 EXEMPLO: Seguindo uma terneira do nascimento até checkpoint

**Dia 0 - Nasce (11 de dezembro 2026)**
```
Você faz: Registra parto (data 11/12, hora 14:30, peso 42kg)
Sistema faz automaticamente:
  ✅ Cria terneira "T-2001" no banco
  ✅ Cria ProgramaAcompanhamento (data_inicio=11/12/2026)
  ✅ Calcula checkpoint para 15/04/2027 (165-195 dias)
  ✅ Avalia C5 e C6 (se vaca teve dias secos/pré-parto registrados)
```

**Dia 0 - Primeira colostragem (11 de dezembro, 15:30)**
```
Você faz: Registra colostragem (volume 4200ml, Brix 24%)
Sistema faz automaticamente:
  ✅ Avalia C1: tempo 1h após parto ≤2h → CONFORME ✅
  ✅ Avalia C2: 4200ml é 10% de 42kg → CONFORME ✅
  ✅ Avalia C3: Brix 24% ≥22% → CONFORME ✅
Dashboard mostra: Colostragem 100% ✅
```

**Dia 0 - Primeira pesagem (11 de dezembro, ao nascer)**
```
Você faz: Registra primeira pesagem (peso 42kg — confirmação do peso ao nascer)
Sistema faz automaticamente:
  ✅ Confirma peso para cálculos (usará 42kg para C2)
  ✅ Cria 1º ponto no gráfico de tendência
  ✅ Define baseline para cálculo de GMD
Dashboard mostra: 1ª pesagem registrada ✅
```

**Dia 1 - Cura de umbigo (12 de dezembro, 08:00)**
```
Você faz: Registra cura de umbigo
Sistema faz automaticamente:
  ✅ Avalia C4: ocorreu 18h após parto → CONFORME ✅
Dashboard mostra: Umbigo 100% ✅
```

**Dia 7 - Segunda pesagem (18 de dezembro, peso 48kg)**
```
Você faz: Registra pesagem
Sistema faz automaticamente:
  ✅ Avalia C7: 48kg está dentro da curva esperada → CONFORME ✅
  ✅ Calcula GMD: (48-42)/(18-11) = 0.857 kg/dia → Excelente!
  ✅ Cria 2º ponto no gráfico de tendência
Dashboard mostra: Peso na curva 100% ✅, GMD 0,857 kg/dia 📈
```

**Dia 30 - Terceira pesagem (11 de janeiro, peso 70kg)**
```
Você faz: Registra pesagem
Sistema faz automaticamente:
  ✅ Avalia C7: 70kg está dentro da curva → CONFORME ✅
  ✅ Calcula GMD: (70-48)/(30 dias) = 0.733 kg/dia → OK (meta 0.75)
  ✅ Cria 3º ponto no gráfico de tendência
Dashboard mostra: GMD médio 0,795 kg/dia (entre as 3 pesagens) 📈
```

**Dia 180 - Checkpoint (15 de junho 2027, peso 155kg)**
```
Você faz: Clica em "Realizar Checkpoint" (165-195 dias ✅)
Sistema faz automaticamente:
  ✅ Gera relatório completo
  ✅ GMD médio total: 0,641 kg/dia (não ideal, precisa de ajuste alimentar)
  ✅ Conformidade total: 85% (2 critérios com "Dado Ausente")
  ✅ Muda status programa para "encerrado"
  ✅ Calcula projeção: "Apta para IA em agosto/2027"
  ✅ Cria resultado: "Trajetória AMARELA" (atenção, GMD abaixo do esperado)
Você recebe: Recomendação de aumentar alimentação a partir de agora
```

---

### 27b. Configurar critérios específicos

**Ajustar parâmetros técnicos:**
1. **Configurações** > **Critérios de Conformidade**
2. Exemplo - editar critério "Colostragem Tempo":
   - **Valor referência**: 2 (horas)
   - **Operador**: ≤ (menor ou igual)
   - **Raça**: Todas ou específica
   - **Ativo**: Sim
3. Salvar → afeta novas avaliações

---

## 📊 ENTENDER CONFORMIDADES (C1-C7)

### 28. Os 7 critérios automáticos explicados

O sistema avalia automaticamente 7 critérios técnicos baseados em literatura Embrapa. Cada critério gera um resultado: **Conforme** 🟢 | **Não Conforme** 🔴 | **Dado Ausente** ⚪ | **Não Aplicável** ⚫

#### C1 - Tempo até primeira colostragem
- **O quê:** Terneira recebeu colostro em ≤ 2 horas após nascimento?
- **Por quê:** Colostro tem anticorpos que protegem. Após 2h, absorção diminui drasticamente
- **Como:** Sistema calcula automaticamente usando hora do parto e hora da colostragem
- **Resultado "Dado Ausente" quando:** Hora do parto não foi registrada ou colostragem faltando

#### C2 - Volume relativo de colostro
- **O quê:** Primeira colostragem teve ≥ 10% do peso vivo da terneira?
- **Por quê:** 10% (ex: 42kg × 0,10 = 4,2L) garante imunidade passiva adequada
- **Como:** Sistema compara volume registrado com 10% do peso (ao nascer ou primeira pesagem)
- **Resultado "Dado Ausente" quando:** Peso ao nascer não informado E nenhuma pesagem registrada

#### C3 - Qualidade do colostro (Brix)
- **O quê:** Colostro tinha Brix ≥ 22%?
- **Por quê:** Brix mede densidade de imunoglobulinas (proteção)
- **Como:** Você registra o Brix ao fornecer colostragem
- **Resultado "Dado Ausente" quando:** Brix não foi medido/registrado

#### C4 - Tempo até primeira cura de umbigo
- **O quê:** Umbigo foi curado nas primeiras horas após nascimento?
- **Por quê:** Reduz risco de onfalite (infecção)
- **Como:** Sistema calcula intervalo entre parto e primeira cura de umbigo
- **Resultado "Dado Ausente" quando:** Hora do parto não registrada ou cura de umbigo faltando

#### C5 - Dias secos adequados
- **O quê:** Vaca teve entre 45-75 dias secos antes do parto (ideal 60 dias)?
- **Por quê:** Período seco regenera glândula mamária, essencial para saúde da terneira
- **Como:** Sistema calcula automaticamente: data de secagem até data de parto
- **Resultado "Dado Ausente" quando:** Data de secagem não registrada no ciclo reprodutivo

#### C6 - Dias pré-parto adequados
- **O quê:** Vaca ficou em pré-parto pelo menos 21 dias?
- **Por quê:** Tempo para adaptação fisiológica, maior qualidade de colostro
- **Como:** Sistema calcula automaticamente: data entrada pré-parto até parto
- **Resultado "Dado Ausente" quando:** Data de entrada em pré-parto não registrada

#### C7 - Peso adequado para idade
- **O quê:** Terneira está dentro da curva de crescimento esperada para a raça?
- **Por quê:** Peso baixo indica manejo ou nutrição inadequada
- **Como:** Sistema compara peso registrado vs. curva de crescimento meta
- **Resultado "Dado Ausente" quando:** Curva de crescimento não configurada para a raça OU nenhuma pesagem registrada

---

## 🔍 DIAGNÓSTICO: Por que minha conformidade está baixa?

### 29. Checklist de diagnóstico

**Se "Colostragem ≤ 2h" está em 0%:**
- [ ] Você registrou a hora do parto? (campo "Hora" é importante!)
- [ ] Você registrou a colostragem com hora correta?
- [ ] Há pelo menos uma colostragem registrada?
→ Corrija: volte ao parto e adicione a hora

**Se "Volume de colostro" está em 0%:**
- [ ] Você registrou o peso ao nascer no parto?
- [ ] OU você registrou uma pesagem nos primeiros dias?
- [ ] Na colostragem, você preencheu o volume em ml?
→ Corrija: volte ao parto e adicione peso ao nascer, OU faça uma pesagem

**Se "Brix do colostro" está em 0%:**
- [ ] Você tem equipamento para medir Brix (refratômetro)?
- [ ] Você preencheu o campo "Brix" ao registrar colostragem?
→ Corrija: compre um refratômetro ou revise se colostragem foi realmente fornecida (pode marcar como "Dado Ausente" se não tinha equipamento)

**Se "Cura de umbigo" está em 0%:**
- [ ] Você registrou cura de umbigo?
- [ ] Registrou a hora corretamente?
→ Corrija: registre a cura de umbigo

**Se "Dias secos" está em 0%:**
- [ ] Ao criar ciclo reprodutivo da vaca, você preencheu "Data da secagem"?
→ Corrija: volte ao ciclo e preencha data de secagem

**Se "Dias pré-parto" está em 0%:**
- [ ] Ao criar ciclo reprodutivo da vaca, você preencheu "Data entrada pré-parto"?
→ Corrija: volte ao ciclo e preencha data de entrada em pré-parto

**Se "Peso na curva" está em 0%:**
- [ ] Você criou Meta de Desenvolvimento para a raça?
- [ ] Meta está marcada como "Ativa"?
- [ ] Você registrou pesagens da terneira?
→ Corrija: crie meta de crescimento e registre pesagens

**Se muitas conformidades estão "Dados Ausentes":**
- ✅ Isso é NORMAL no começo!
- Significa que informações necessárias não foram registradas
- Conforme você registra dados, conformidades aparecem
- Recomendação: consulte a seção 28 acima para saber o que está faltando

---

## ⚠️ LIMITAÇÕES CONHECIDAS

### 30. Funcionalidades não implementadas ou parciais

**Sistema de permissões (INCOMPLETO):**
- ⚠️ Todos os usuários autenticados têm acesso total às funcionalidades
- Papéis (admin, técnico, produtor, auxiliar) existem no banco de dados mas **NÃO são verificados** no código
- O que isso significa: um usuário "auxiliar" pode fazer exatamente o mesmo que um "admin"
- Planejado para versão futura
- **Recomendação:** Use apenas com usuários de confiança no mesmo time

**Validações automáticas (AUSENTES):**
- Sistema NÃO valida valores fora do padrão:
  - Peso muito alto (5000kg passa)
  - Idade incompatível (desaleitamento antes de 30 dias)
  - Gestação incompatível (280 dias de diferença não é verificado)
- **Recomendação:** Confira dados antes de salvar, especialmente números

**Edição de eventos:**
- ✅ Apenas colostragem pode ser editada (nas primeiras 24h)
- ❌ Outros eventos (parto, pesagem, vacinação, etc.) são permanentes
- ❌ Desaleitamento NÃO pode ser editado (mudança de categoria é irreversível)
- ❌ IA/Cobertura NÃO pode ser editado (encerra escopo do sistema)
- **Para correções:** Entre em contato com o administrador do sistema ou use Django Admin (/admin/)

**Critérios C8-C10 (AUSENTES):**
- ⚠️ Desaleitamento é registrado mas **não é automaticamente avaliado**
- Não há validação de:
  - Idade mínima de desaleitamento
  - Idade máxima de desaleitamento
  - Peso mínimo no desaleitamento
- Será implementado em versão futura
- **Impacto:** Você pode registrar desaleitamento em qualquer idade/peso sem avisos

**Movimentação de lotes (PARCIAL):**
- ✅ Você pode mover animais entre lotes
- ✅ Sistema mantém histórico completo
- ❌ Não há validação de lote apropriado para categoria
  - Uma terneira pode ser movida para lote "Vacas secas" sem avisos
  - Recomendação: use nomes de lotes padronizados e confira sempre

**Protocolo alimentar (AUSENTE):**
- ⚠️ Modelos existem no banco de dados mas não há interface para usar
- Registro diário de alimentação não está acessível pela UI
- Será implementado ou removido em versão futura

**Metas dos gráficos (PARCIALMENTE CONFIGURÁVEL):**
- Metas dos 4 gráficos do dashboard buscam referenciais técnicos
- ⚠️ Metas ainda podem ter valores hardcoded em alguns casos
- Se precisar alterar: entre em contato com administrador

**Controle de estoque de colostro (AUSENTE):**
- ✅ Você pode registrar lotes no banco de colostro
- ❌ Sistema NÃO deduz volume automaticamente ao usar
- ❌ Não há alertas de estoque baixo
- **Recomendação:** Controle estoque manualmente

**Histórico de alterações (AUSENTE):**
- Você pode editar dados cadastrais de animais
- Sistema registra quando foi criado/atualizado (campos `criado_em`, `atualizado_em`)
- ❌ Não há log de QUEM alterou ou O QUE mudou especificamente
- Alterações maliciosas/acidentais não são rastreáveis
- **Recomendação:** Use com usuários de confiança

**Recuperação de senha por e-mail (AUSENTE):**
- Sistema não envia e-mail automaticamente
- Se esqueceu senha: contate o administrador
- Admin pode resetar via `/admin-sistema/usuarios/<pk>/editar/`

---

## 🎉 NOVIDADES DA ÚLTIMA ATUALIZAÇÃO

### 31. O que foi melhorado recentemente

**✅ Volume recomendado de colostro:**
- Campo agora exibe corretamente "Meta: ~4200ml (10% do peso)"
- Sistema calcula automaticamente baseado no peso ao nascer ou primeira pesagem
- Use como referência para fornecer colostro adequado

**✅ Metas dos gráficos mais inteligentes:**
- Metas agora buscam referenciais técnicos configurados no sistema
- Adaptam-se aos padrões da sua propriedade
- Podem ser ajustadas em Configurações > Critérios de Conformidade

**✅ Edição de eventos (colostragem):**
- Colostragem pode ser editada nas primeiras 24 horas após registro
- Sistema recalcula conformidades automaticamente após edição
- Na ficha da terneira, clique no evento e depois em "Editar"
- Outros eventos (parto, pesagem) continuam imutáveis

**✅ Movimentação de lotes com histórico:**
- Interface completa para mover animais entre lotes
- Preserva histórico completo de movimentações
- Na ficha do animal, botão "Mover para Lote"
- Útil para organizar por fase: aleitamento → pós-desaleitamento → recria

**✅ Exclusão de eventos com confirmação:**
- Colostragem e pesagens podem ser excluídas com confirmação
- Sistema remove automaticamente as conformidades relacionadas
- Na ficha do animal, botão "Excluir" ao lado de cada evento
- ⚠️ Ação é permanente e não pode ser desfeita

**✅ Comando para limpar dados de teste:**
- Comando para remover todos os dados fictícios de uma vez
- Mantém estrutura (propriedades, usuários, configurações)
- Útil para começar com dados reais após testes

**✅ Dashboard com KPIs consolidados:**
- 3 zonas: Alertas, Status, Tendência
- 4 gráficos Chart.js mostrando 6 meses de histórico
- 13 indicadores acompanhados automaticamente
- 10 tipos de alertas automáticos

**✅ Automações totais:**
- Terneira criada automaticamente ao registrar parto
- Programa de acompanhamento criado automaticamente
- Categorias mudam automaticamente (terneira → novilha → vaca)
- Conformidades avaliadas automaticamente após cada evento
- Checkpoints calculados automaticamente
- Projeções reprodutivas atualizadas automaticamente

---

## 🚀 FORMAS DE INICIAR O SERVIDOR (RESUMO)

### A. Script automático (RECOMENDADO) ⭐

**Método mais fácil:**
```bash
./iniciar_servidor.sh
```

Ou **clique duas vezes** no arquivo `iniciar_servidor.sh`

### B. Atalho na área de trabalho 🖥️

Procure o ícone **"TerneirasPro"** e clique duas vezes

### C. Manualmente no terminal

```bash
source venv/bin/activate
python manage.py runserver
```

### D. Iniciar automaticamente no boot 🚀

```bash
sudo systemctl enable terneiraspro
sudo systemctl start terneiraspro
```

---

## 🆘 SUPORTE, DICAS E NAVEGAÇÃO RÁPIDA

### 32. Comandos Django úteis

**Criar dados de teste (para popular o dashboard):**
```bash
python manage.py seed_dados_teste
```

**Limpar TODOS os dados de teste/fictícios:**
```bash
# Apenas verificar o que seria removido:
python manage.py limpar_dados_teste

# Confirmar e executar limpeza (CUIDADO!):
python manage.py limpar_dados_teste --confirmar --propriedade 1
```

**Backup do banco:**
```bash
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

### 33. URLs de acesso rápido

**Públicas:**
- Dashboard: `/` (página inicial)
- Login: `/accounts/login/`

**Animais:**
- Lista terneiras: `/animais/`
- Nova terneira: `/animais/nova/`
- Lista vacas: `/animais/vacas/`
- Nova vaca: `/animais/vacas/nova/`
- Lista lotes: `/animais/lotes/`

**Eventos:**
- Colostragem: `/eventos/colostragem/<terneira_id>/`
- Pesagem: `/eventos/pesagem/<animal_id>/`
- Parto: `/eventos/parto/novo/<ciclo_id>/`
- Sanitário: `/eventos/sanitario/<animal_id>/`
- Desaleitamento: `/eventos/desaleitamento/<terneira_id>/`
- Banco colostro: `/eventos/banco-colostro/`

**Programas:**
- Programas: `/programas/`
- Aptas reprodução: `/programas/aptas/`

**Configurações:**
- Config técnica: `/config/`
- Metas desenvolvimento: `/config/metas/`
- Metas reprodutivas: `/config/meta-reprodutiva/`
- Critérios: `/config/criterios/`

**Admin (só superuser):**
- Painel admin: `/admin-sistema/`
- Usuários: `/admin-sistema/usuarios/`
- Propriedades: `/admin-sistema/propriedades/`
- Django Admin (dados brutos): `/admin/`

### 34. O que cada zona do dashboard mostra

**ZONA 1 - Alertas (vermelho/amarelo/verde):**
- 🔴 **Críticos:** colostragem pendente, doença grave aberta >7 dias, peso crítico <90%
- 🟡 **Operacionais:** sem pesagem >30 dias, checkpoint pendente, pré-parto sem protocolo
- 🟢 **Tudo em dia:** nenhum alerta ativo

**ZONA 2 - Status (últimos 30/90/180 dias - escolha o período):**
- **Desempenho:** terneiras ativas, novilhas, nascimentos F/M, GMD médio
- **Conformidade:** % conforme em cada critério (C1-C7)
- **Sanitário:** incidência de diarreia, pneumonia, onfalite
- **Reprodutivo:** novilhas, trajetórias, checkpoints realizados

**ZONA 3 - Tendência (6 últimos meses - 4 gráficos):**
- Gráfico 1: % colostragem ≤ 2h (meta 90%)
- Gráfico 2: GMD médio aleitamento (meta 0,75 kg/dia)
- Gráfico 3: % incidência sanitária (diarreia + pneumonia)
- Gráfico 4: % terneiras dentro da curva de peso (meta 80%)

**💡 Dica:** Cada gráfico é interativo — clique nos pontos para ver valores exatos, passe mouse sobre legendas para filtrar series

### 35. Taxa de conformidade: como é calculada

**Fórmula:**
```
Taxa = Conformes ÷ (Conformes + Não Conformes) × 100%
```

**O que NÃO entra no cálculo:**
- ⚪ "Dado Ausente" — não requer ação, só indica falta de informação
- ⚫ "Não Aplicável" — critério não se aplica ao animal

**Exemplos:**
- 8 conformes + 2 não conformes = 8÷10 = 80% ✅
- 5 conformes + 5 não conformes + 2 dados ausentes = 5÷10 = 50% (dado ausente não entra)
- 10 conformes + 0 não conformes + 1 dado ausente = 10÷10 = 100% ✅

**Recomendação:** Trabalhe para ter ≥90% em cada critério

### 36. Fluxo recomendado diário

**MANHÃ:**
1. Abra dashboard — verifique alertas
2. Registre pesagens da semana
3. Verifique ocorrências sanitárias abertas

**APÓS EVENTOS:**
4. Registre partos **imediatamente**
5. Colostragem **nas primeiras 2 horas**
6. Cura de umbigo **no mesmo dia**
7. Atualize ocorrências sanitárias

**SEMANAL:**
8. Revise conformidades — veja quem está com "Dado Ausente"
9. Confira se todos têm pelo menos 1 pesagem/mês
10. Planeje checkpoints pendentes (165-195 dias)
11. Atualize metas se necessário

**MENSAL:**
12. Revise media de GMD — está acima de 0,75 kg/dia?
13. Confira se desaleitamentos estão na idade correta
14. Valide projeção reprodutiva das novilhas
15. Faça backup do banco (`cp db.sqlite3 backup_$(date).sqlite3`)

### 37. Atalhos de teclado e dicas práticas

**No navegador:**
- `Ctrl+L` — ir para barra de endereço (rápido mudar de página)
- `F5` — recarregar page (se dados não aparecem)
- `Ctrl+Shift+K` — abrir console (se tiver erro JavaScript)

**No dashboard:**
- Clique no período (30/90/180) para alterar janela de tempo
- Clique em "Ver todas" em qualquer card para expandir lista completa
- Período 30 dias = últimos 30 dias (não "mês corrente")

**Ao registrar eventos:**
- Sempre preencha **hora** (não só data) — importante para C1 e C4
- Sempre registre **peso** (ao nascer ou primeira pesagem) — importante para C2 e C7
- Se não tiver equipamento para Brix, está OK deixar vazio — conformidade será "Dado Ausente"

### 38. O que significa cada status de animal

**Terneira:**
- Fêmea nascida que ainda não foi desaleitada
- Tem programa automático

**Novilha:**
- Fêmea após desaleitamento até primeira IA
- Projeção reprodutiva ativa
- Quando atinge peso/idade mínimos → aparece em "Aptas à Reprodução"

**Vaca:**
- Fêmea após primeira IA
- Escopo do sistema encerrado para este animal
- Pode ter novos ciclos reprodutivos (será mãe de próxima geração)

**Bezerro:**
- Macho nascido
- Sem programa automático
- Saio do escopo do sistema (futuro será descarte ou reprodutor)

### 39. Glossário

| Termo | Significado |
|---|---|
| **GMD** | Ganho Médio Diário (kg/dia) — velocidade de ganho de peso |
| **Brix** | Medida de qualidade do colostro (densidade de proteínas/imunoglobulinas) |
| **Conformidade** | Aderência ao critério técnico (conforme / não conforme / dado ausente) |
| **Checkpoint** | Avaliação aos 6 meses — confirma se terneira está no caminho certo |
| **Projeção** | Cálculo de quando novilha estará apta para IA |
| **Trajetória** | Classificação: Verde=excelente, Amarelo=atenção, Vermelho=crítico |
| **Meta de Desenvolvimento** | Curva de peso esperado para raça e idade |
| **Ciclo Reprodutivo** | Período da cobertura até parto de uma vaca |
| **Dias Secos** | Período entre secagem da vaca e parto (ideal 60 dias) |
| **Pré-parto** | Últimos 21+ dias antes do parto (fêmea em preparação) |

### 40. Contato e recursos

**Documentação completa:**
- ✅ Este manual — uso do sistema
- ✅ `DOCUMENTACAO_AGENTE.md` — arquitetura e decisões técnicas
- ✅ `CHANGELOG.md` — histórico de implementações e bugs corrigidos
- ✅ `README.md` — overview do projeto

**Suporte:**
- **Dúvidas operacionais:** consulte este manual
- **Problemas técnicos:** entre em contato com o administrador
- **Bugs ou sugestões:** documente no CHANGELOG.md

**Desenvolvedor:**  
Victor Rodrigues — Passo Fundo/RS

**Versão do sistema:**  
Django 4.2.16 | Python 3.12 | Bootstrap 5.3 | Chart.js 4.4

**Última atualização do manual:** Agosto 2026