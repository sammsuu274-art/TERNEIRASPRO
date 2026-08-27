# TerneirasPro - Sistema de Gestão de Terneiras Leiteiras

> **Desenvolvedor:** Victor Rodrigues - Passo Fundo/RS  
> **Versão:** 4.2.16  
> **Django:** 4.2.16 | **Python:** 3.12.3

---

## 🚀 INÍCIO RÁPIDO

### Para iniciar o sistema:

**1. Clique duplo no arquivo:**
```
iniciar_servidor.sh
```

**2. Ou execute no terminal:**
```bash
cd /home/victor/Documentos/victor/Documentos/TERNEIRAS
./iniciar_servidor.sh
```

**3. Para gerenciar servidor existente:**
```bash
./gerenciar_servidor.sh status    # Ver se está rodando
./gerenciar_servidor.sh stop      # Parar
./gerenciar_servidor.sh restart   # Reiniciar
```

**4. Acesse no navegador:**
```
http://127.0.0.1:8000
```

**4. Faça login:**
- **Usuário:** `admin`
- **Senha:** [sua senha configurada]

---

## 📁 ARQUIVOS PRINCIPAIS

| Arquivo | Descrição |
|---------|-----------|
| `iniciar_servidor.sh` | **Script de inicialização** (clique duplo) |
| `gerenciar_servidor.sh` | **Gerenciador** (status, stop, start, restart) |
| `MANUAL_DO_USUARIO.md` | Manual completo para usuários finais |
| `DOCUMENTACAO_AGENTE.md` | **Fonte técnica oficial** — arquitetura, estado, regras, pendências |
| `CHANGELOG.md` | Histórico de mudanças e correções |
| `RESUMO_IMPLEMENTACAO.md` | Resumo histórico de uma sprint (não atualizar) |
| `IMPLEMENTACAO_LOGIN.md` | Decisões de design da tela de login |
| `TELA_LOGIN_LAYOUT.md` | Arquitetura CSS da tela de login (valores aprovados) |

---

## 🤖 PARA AGENTES DE IA E DESENVOLVEDORES

**Leia `DOCUMENTACAO_AGENTE.md` antes de qualquer ação no projeto.**

Este arquivo contém:
- Arquitetura completa e stack técnica
- Estado atual de implementação (74%, 35/47 funcionalidades)
- Regras de negócio permanentes
- Bugs conhecidos e decisões pendentes
- O que está fora do escopo (não implementar)
- Decisões técnicas aprovadas (não alterar sem justificativa)

As regras automáticas para agentes estão em `.kiro/steering/projeto.md`.

---

## ⚙️ CONFIGURAÇÃO AUTOMÁTICA (OPCIONAL)

### Para iniciar automaticamente no boot:

```bash
# Copiar service para systemd
sudo cp terneiraspro.service /etc/systemd/system/

# Habilitar inicialização automática
sudo systemctl enable terneiraspro

# Iniciar agora
sudo systemctl start terneiraspro

# Ver status
sudo systemctl status terneiraspro
```

Com isso, o sistema iniciará automaticamente toda vez que você ligar o computador!

---

## 🛠️ COMANDOS ÚTEIS

### Desenvolvimento:
```bash
# Ativar ambiente
source venv/bin/activate

# Verificar sistema
python manage.py check

# Backup do banco
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

### Limpeza:
```bash
# Limpar dados de teste (CUIDADO!)
python manage.py limpar_dados_teste --confirmar --propriedade 1
```

### Seeds:
```bash
# Dados iniciais
python manage.py seed_referenciais
python manage.py seed_criterios --propriedade 1
```

---

## 📊 FUNCIONALIDADES

- ✅ **Gestão de vacas** e ciclos reprodutivos
- ✅ **Registro de partos** (cria terneira automaticamente)  
- ✅ **Colostragem** com cálculo de meta automático
- ✅ **Acompanhamento de crescimento** (pesagens e GMD)
- ✅ **Eventos sanitários** (diarreia, pneumonia, etc.)
- ✅ **Desaleitamento** e checkpoint de 6 meses
- ✅ **Projeção reprodutiva** até primeira IA
- ✅ **Dashboard** com alertas e gráficos interativos
- ✅ **Conformidades** automáticas (C1-C7)
- ✅ **Multi-tenancy** (várias propriedades)
- ✅ **Movimentação de lotes**
- ✅ **Exclusão de eventos** (colostragem, pesagem)

---

## 🎯 STATUS

```
✅ Sistema: 74% implementado (35/47 funcionalidades)
✅ Banco: Limpo e pronto para produção  
✅ Servidor: Funcionando sem erros
✅ Documentação: Completa e atualizada
```

---

## 📞 SUPORTE

**Desenvolvedor:** Victor Rodrigues - Passo Fundo/RS  
**Documentação:** Consulte `MANUAL_DO_USUARIO.md`  
**Problemas técnicos:** Consulte `DOCUMENTACAO_AGENTE.md`

---

## 🏆 TECNOLOGIAS

- **Backend:** Django 4.2.16 + Python 3.12.3
- **Frontend:** Bootstrap 5.3 + Alpine.js + Chart.js
- **Banco:** SQLite (dev) / PostgreSQL (prod)
- **Servidor:** Django Development Server

**Sistema pronto para uso! 🎉**