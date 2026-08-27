# Manual do Usuário — TerneirasPro
> Sistema de gestão técnica de terneiras leiteiras  
> Versão: Agosto 2026

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
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
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

### 27. Configurar critérios específicos

**Ajustar parâmetros técnicos:**
1. **Configurações** > **Critérios de Conformidade**
2. Exemplo - editar critério "Colostragem Tempo":
   - **Valor referência**: 2 (horas)
   - **Operador**: ≤ (menor ou igual)
   - **Raça**: Todas ou específica
   - **Ativo**: Sim
3. Salvar → afeta novas avaliações

---

## ⚠️ LIMITAÇÕES CONHECIDAS

### 28. O que ainda não está disponível

**✅ Volume recomendado de colostro:**
- Campo agora exibe corretamente "Meta: ~4200ml (10% do peso)"
- Sistema calcula automaticamente baseado no peso ao nascer ou primeira pesagem

**✅ Metas dos gráficos mais inteligentes:**
- Metas agora buscam referenciais técnicos configurados no sistema
- Adaptam-se aos padrões da sua propriedade

**✅ Edição de eventos:**
- Colostragem pode ser editada nas primeiras 24 horas após registro
- Sistema recalcula conformidades automaticamente após edição
- Na ficha da terneira, clique no evento e depois em "Editar"

**✅ Movimentação de lotes:**
- Interface completa para mover animais entre lotes
- Preserva histórico completo de movimentações
- Na ficha do animal, clique em "Mover para Lote"

### 25. Limitações conhecidas

**Sistema de permissões:**
- Todos os usuários autenticados têm acesso total às funcionalidades
- Papéis (admin, técnico, produtor, auxiliar) existem mas não são verificados
- Planejado para versão futura

**Validações automáticas:**
- Sistema aceita alguns valores fora do padrão (peso muito alto, etc.)
- Recomenda-se conferir dados antes de salvar

**Edição de eventos antigos:**
- Apenas colostragem pode ser editada (nas primeiras 24h)
- Outros eventos (parto, pesagem, etc.) são permanentes
- Para correções: contate o administrador do sistema

---

## � NOVIDADES DA ÚLTIMA ATUALIZAÇÃO

### 27. O que foi melhorado recentemente

**✅ Volume recomendado de colostro:**
- Campo agora exibe corretamente "Meta: ~4200ml (10% do peso)"
- Sistema calcula automaticamente baseado no peso ao nascer ou primeira pesagem

**✅ Metas dos gráficos mais inteligentes:**
- Metas agora buscam referenciais técnicos configurados no sistema
- Adaptam-se aos padrões da sua propriedade

**✅ Edição de eventos:**
- Colostragem pode ser editada nas primeiras 24 horas após registro
- Sistema recalcula conformidades automaticamente após edição
- Na ficha da terneira, clique no evento e depois em "Editar"

**✅ Movimentação de lotes:**
- Interface completa para mover animais entre lotes
- Preserva histórico completo de movimentações
- Na ficha do animal, botão "Mover para Lote"

**✅ Exclusão de eventos:**
- Colostragem e pesagens podem ser excluídas com confirmação
- Sistema remove automaticamente as conformidades relacionadas
- Na ficha do animal, botão "Excluir" ao lado de cada evento

**✅ Limpeza de dados de teste:**
- Comando para remover todos os dados fictícios de uma vez
- Mantém estrutura (propriedades, usuários, configurações)
- Útil para começar com dados reais

---

## 🚀 FORMAS DE INICIAR O SERVIDOR

### A. Script automático (RECOMENDADO) ⭐

**Método mais fácil:**
```bash
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
./iniciar_servidor.sh
```

Ou simplesmente **clique duas vezes** no arquivo `iniciar_servidor.sh` no gerenciador de arquivos!

**O que o script faz:**
- ✅ Detecta se servidor já está rodando
- ✅ Verifica se tudo está configurado
- ✅ Ativa o ambiente virtual automaticamente
- ✅ Verifica o sistema (check)
- ✅ Coleta arquivos estáticos
- ✅ Inicia o servidor com mensagens coloridas
- ✅ Mostra URL e login

**💡 Gerenciar servidor existente:**
```bash
./gerenciar_servidor.sh status    # Ver se está rodando
./gerenciar_servidor.sh stop      # Parar servidor
./gerenciar_servidor.sh start     # Iniciar servidor
./gerenciar_servidor.sh restart   # Reiniciar servidor
./gerenciar_servidor.sh logs      # Ver logs
```

### B. Atalho na área de trabalho 🖥️

1. Procure o ícone **"TerneirasPro"** na sua área de trabalho
2. Clique duas vezes para iniciar
3. O terminal abrirá automaticamente
4. Acesse: `http://127.0.0.1:8000`

### C. Manualmente no terminal

```bash
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
source venv/bin/activate
python manage.py runserver
```

### D. Iniciar automaticamente no boot 🚀

**Para o sistema iniciar sozinho quando você ligar o computador:**

```bash
# 1. Copiar o service
sudo cp terneiraspro.service /etc/systemd/system/

# 2. Habilitar
sudo systemctl enable terneiraspro

# 3. Iniciar agora
sudo systemctl start terneiraspro

# 4. Ver status
sudo systemctl status terneiraspro
```

**Comandos úteis:**
```bash
sudo systemctl stop terneiraspro      # Parar
sudo systemctl restart terneiraspro   # Reiniciar
sudo systemctl disable terneiraspro   # Desabilitar boot
sudo journalctl -u terneiraspro -f    # Ver logs
```

💡 **Dica:** Com a Opção D, o TerneirasPro iniciará automaticamente!

---

## 🆘 SUPORTE E DICAS

### 28. Comandos úteis

**Formas de iniciar (escolha uma):**
```bash
# Opção 1: Script automático (RECOMENDADO)
./iniciar_servidor.sh

# Opção 2: Manual
source venv/bin/activate
python manage.py runserver
```

**Backup do banco:**
```bash
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

**Criar dados de teste:**
```bash
python manage.py seed_dados_teste
```

**Limpar TODOS os dados de teste/fictícios:**
```bash
# Apenas verificar o que seria removido:
python manage.py limpar_dados_teste

# Confirmar e executar limpeza (CUIDADO!):
python manage.py limpar_dados_teste --confirmar

# Limpar apenas uma propriedade específica:
python manage.py limpar_dados_teste --confirmar --propriedade 1
```

⚠️ **ATENÇÃO:** O comando de limpeza remove:
- Todos os animais (vacas, terneiras, bezerros)
- Todos os eventos (partos, colostragens, pesagens, etc.)
- Todos os programas e checkpoints
- Todas as conformidades calculadas

**Mantém intacto:**
- Propriedades
- Usuários e vínculos
- Lotes (estrutura)
- Protocolos, metas e referenciais técnicos

### 29. Navegação rápida

**Principais URLs:**
- Dashboard: `/`
- Lista terneiras: `/animais/`
- Lista vacas: `/animais/vacas/`
- Eventos: menu lateral
- Configurações: `/config/`
- Admin sistema: `/admin-sistema/` (só superuser)
- Django Admin: `/admin/` (dados brutos)

**URLs novas (últimas melhorias):**
- Editar colostragem: `/eventos/colostragem/<id>/editar/`
- Excluir colostragem: `/eventos/colostragem/<id>/excluir/`
- Excluir pesagem: `/eventos/pesagem/<id>/excluir/`
- Mover animal de lote: `/eventos/lote/mover/<animal_pk>/`

### 32. Fluxo recomendado diário

**Manhã:**
1. Verificar alertas no dashboard
2. Registrar pesagens da semana
3. Verificar ocorrências sanitárias abertas

**Após eventos:**
4. Registrar partos imediatamente
5. Colostragem nas primeiras 2 horas
6. Cura de umbigo no mesmo dia
7. Atualizar ocorrências sanitárias

**Semanal:**
8. Revisar conformidades no dashboard
9. Planejar checkpoints pendentes
10. Atualizar metas se necessário

---

## 📞 CONTATO E SUPORTE

**Desenvolvedor:** Victor Rodrigues - Passo Fundo/RS  
**E-mail:** [Disponível mediante solicitação]  
**Versão do manual:** Agosto 2026  
**Sistema:** TerneirasPro v4.2.16  
**Última atualização:** 14 de Agosto de 2026

**Suporte técnico:**
- Para dúvidas operacionais: consulte este manual
- Para problemas técnicos: entre em contato com o desenvolvedor
- Para documentação técnica: consulte `DOCUMENTACAO_AGENTE.md`
- Para histórico de mudanças: consulte `CHANGELOG.md`

**Recursos disponíveis:**
- ✅ Manual do usuário (este arquivo)
- ✅ Documentação técnica completa
- ✅ Changelog com todas as correções
- ✅ Sistema 74% implementado e funcional
- ✅ Servidor web integrado
- ✅ Interface moderna e responsiva

---

*Este manual cobre o uso normal do sistema TerneirasPro. Para informações técnicas sobre desenvolvimento, arquitetura e implementação, consulte DOCUMENTACAO_AGENTE.md no diretório raiz do projeto.*

**Versão do Django:** 4.2.16  
**Python:** 3.12.3  
**Bootstrap:** 5.3.3  
**Chart.js:** 4.4.4