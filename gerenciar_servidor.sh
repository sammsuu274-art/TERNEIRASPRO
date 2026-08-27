#!/bin/bash
# Gerenciador do TerneirasPro
# Desenvolvedor: Victor Rodrigues - Passo Fundo/RS

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║       TerneirasPro - Gerenciador do Servidor         ║"
echo "║         Victor Rodrigues - Passo Fundo/RS            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Função para verificar se servidor está rodando
check_server() {
    local pid=$(ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$pid" ]; then
        echo -e "${GREEN}✅ Servidor está RODANDO${NC}"
        echo -e "   PID: ${YELLOW}$pid${NC}"
        echo -e "   URL: ${BLUE}http://127.0.0.1:8000${NC}"
        
        # Testar se responde
        if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 | grep -q "200\|302"; then
            echo -e "   Status: ${GREEN}Respondendo corretamente${NC}"
        else
            echo -e "   Status: ${YELLOW}Processo ativo mas não responde (carregando?)${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ Servidor NÃO está rodando${NC}"
        return 1
    fi
}

# Função para parar servidor
stop_server() {
    local pids=$(ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}')
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}🛑 Parando servidor...${NC}"
        for pid in $pids; do
            echo -e "   Matando processo PID: $pid"
            kill $pid 2>/dev/null
        done
        sleep 2
        
        # Verificar se parou
        local remaining=$(ps aux | grep "manage.py runserver" | grep -v grep | wc -l)
        if [ $remaining -eq 0 ]; then
            echo -e "${GREEN}✅ Servidor parado com sucesso${NC}"
        else
            echo -e "${YELLOW}⚠️  Forçando parada...${NC}"
            pkill -f "manage.py runserver"
            sleep 1
            echo -e "${GREEN}✅ Servidor forçadamente parado${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  Servidor já estava parado${NC}"
    fi
}

# Função para iniciar servidor
start_server() {
    if check_server > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Servidor já está rodando!${NC}"
        check_server
        return 1
    fi
    
    echo -e "${YELLOW}🚀 Iniciando servidor...${NC}"
    cd "/home/victor/Documentos/victor/Documentos/TERNEIRAS" || exit 1
    
    # Verificar ambiente
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
        exit 1
    fi
    
    # Iniciar em background
    source venv/bin/activate
    nohup python manage.py runserver > /dev/null 2>&1 &
    
    # Aguardar inicialização
    echo -e "${YELLOW}⏳ Aguardando inicialização...${NC}"
    sleep 3
    
    # Verificar se iniciou
    if check_server > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Servidor iniciado com sucesso!${NC}"
        check_server
    else
        echo -e "${RED}❌ Falha ao iniciar servidor${NC}"
        exit 1
    fi
}

# Função para reiniciar
restart_server() {
    echo -e "${YELLOW}🔄 Reiniciando servidor...${NC}"
    stop_server
    sleep 2
    start_server
}

# Função para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Últimos logs do Django (últimas 20 linhas):${NC}"
    cd "/home/victor/Documentos/victor/Documentos/TERNEIRAS" || exit 1
    
    # Procurar arquivo de log se existir
    if [ -f "django.log" ]; then
        tail -20 django.log
    else
        echo -e "${YELLOW}ℹ️  Nenhum arquivo de log encontrado${NC}"
        echo -e "   O servidor está rodando em modo desenvolvimento"
    fi
}

# Menu principal
case "$1" in
    "status"|"")
        check_server
        ;;
    "start")
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        restart_server
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo -e "${BLUE}Uso: $0 [comando]${NC}"
        echo ""
        echo "Comandos disponíveis:"
        echo -e "  ${GREEN}status${NC}   - Verificar se servidor está rodando (padrão)"
        echo -e "  ${GREEN}start${NC}    - Iniciar servidor"
        echo -e "  ${GREEN}stop${NC}     - Parar servidor"
        echo -e "  ${GREEN}restart${NC}  - Reiniciar servidor"
        echo -e "  ${GREEN}logs${NC}     - Mostrar logs recentes"
        echo ""
        echo -e "${YELLOW}Exemplos:${NC}"
        echo "  $0 status     # Ver se está rodando"
        echo "  $0 stop       # Parar servidor"
        echo "  $0 start      # Iniciar servidor"
        echo ""
        ;;
esac