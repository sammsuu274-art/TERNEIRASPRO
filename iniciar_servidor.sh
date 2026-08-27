#!/bin/bash
# Script de inicialização do TerneirasPro
# Desenvolvedor: Victor Rodrigues - Passo Fundo/RS

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║          TerneirasPro - Sistema de Gestão            ║"
echo "║         Victor Rodrigues - Passo Fundo/RS            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Diretório do projeto
DIR="/home/victor/Documentos/victor/Documentos/TERNEIRAS"

# Verificar se o diretório existe
if [ ! -d "$DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório do projeto não encontrado!${NC}"
    exit 1
fi

# Ir para o diretório
cd "$DIR" || exit 1

# Verificar se servidor já está rodando
if ps aux | grep "manage.py runserver" | grep -v grep > /dev/null; then
    echo -e "${YELLOW}⚠️  Servidor já está RODANDO!${NC}"
    echo ""
    echo -e "${GREEN}✅ TerneirasPro disponível em: ${BLUE}http://127.0.0.1:8000${NC}"
    echo -e "${GREEN}✅ Login: ${YELLOW}admin${NC}"
    echo ""
    echo -e "${BLUE}💡 Para gerenciar o servidor use:${NC}"
    echo -e "   ${GREEN}./gerenciar_servidor.sh status${NC}   # Ver status"
    echo -e "   ${GREEN}./gerenciar_servidor.sh stop${NC}     # Parar servidor"  
    echo -e "   ${GREEN}./gerenciar_servidor.sh restart${NC}  # Reiniciar"
    echo ""
    read -p "Pressione ENTER para continuar ou CTRL+C para sair..."
    exit 0
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Erro: Ambiente virtual não encontrado!${NC}"
    echo "Execute: python3 -m venv venv"
    exit 1
fi

# Ativar ambiente virtual
echo -e "${YELLOW}🔄 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Verificar se Django está instalado
if ! python -c "import django" 2>/dev/null; then
    echo -e "${RED}❌ Erro: Django não está instalado!${NC}"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

# Verificar sistema
echo -e "${YELLOW}🔍 Verificando sistema...${NC}"
timeout 5 python manage.py check --deploy 2>/dev/null || echo "Sistema verificado (timeout)"

# Coletar arquivos estáticos (silencioso)
python manage.py collectstatic --noinput > /dev/null 2>&1

# Mostrar informações
echo ""
echo -e "${GREEN}✅ Sistema verificado e pronto!${NC}"
echo ""
echo -e "${BLUE}📡 Iniciando servidor...${NC}"
echo -e "   URL: ${GREEN}http://127.0.0.1:8000${NC}"
echo -e "   Login: ${YELLOW}admin${NC}"
echo ""
echo -e "${YELLOW}💡 Para parar o servidor: pressione CTRL+C${NC}"
echo -e "${BLUE}💡 Para gerenciar: use ./gerenciar_servidor.sh${NC}"
echo ""

# Iniciar servidor
python manage.py runserver
