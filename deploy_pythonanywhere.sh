#!/bin/bash

# ==============================================================================
# SCRIPT DE DEPLOYMENT AUTOMÁTICO - TERNEIRASPRO NO PYTHONANYWHERE
# ==============================================================================
# 
# PROPÓSITO:
# Automatizar passos do deployment no PythonAnywhere
# Executar via Bash Console do PythonAnywhere
#
# MODO DE USO:
# 1. Fazer upload deste script para o PythonAnywhere
# 2. Dar permissão de execução: chmod +x deploy_pythonanywhere.sh
# 3. Executar: ./deploy_pythonanywhere.sh
#
# O QUE ESTE SCRIPT FAZ:
# ✓ Cria/atualiza ambiente virtual
# ✓ Instala dependências
# ✓ Coleta arquivos estáticos
# ✓ Aplica migrations
# ✓ Exibe instruções finais
#
# ==============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
PROJECT_DIR="$HOME/TERNEIRAS"
VENV_DIR="$HOME/venv"
PYTHON_VERSION="3.12"

# Funções de utilidade
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_step() {
    echo -e "${YELLOW}► $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ==============================================================================
# INÍCIO DO DEPLOYMENT
# ==============================================================================

print_header "DEPLOYMENT DO TERNEIRASPRO NO PYTHONANYWHERE"

# Step 1: Verificar ambiente
print_step "Verificando ambiente..."

if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Diretório do projeto não encontrado: $PROJECT_DIR"
    echo "Certifique-se de que o projeto foi enviado para ~/TerneirasPro"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    print_error "requirements.txt não encontrado em $PROJECT_DIR"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    print_error "manage.py não encontrado em $PROJECT_DIR"
    exit 1
fi

print_success "Projeto encontrado em $PROJECT_DIR"

# Step 2: Criar ou atualizar ambiente virtual
print_step "Configurando ambiente virtual (Python $PYTHON_VERSION)..."

if [ -d "$VENV_DIR" ]; then
    print_success "Ambiente virtual já existe"
else
    python$PYTHON_VERSION -m venv $VENV_DIR
    print_success "Ambiente virtual criado"
fi

# Step 3: Ativar ambiente virtual
source $VENV_DIR/bin/activate
print_success "Ambiente virtual ativado"

# Step 4: Atualizar pip
print_step "Atualizando pip, setuptools e wheel..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_success "pip atualizado"

# Step 5: Instalar dependências
print_step "Instalando dependências do projeto..."
cd $PROJECT_DIR
pip install -r requirements.txt

print_success "Dependências instaladas"

# Step 6: Verificar integridade
print_step "Verificando integridade das dependências..."
pip check
print_success "Nenhuma dependência quebrada"

# Step 7: Verificar .env
print_step "Verificando arquivo .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_error ".env não encontrado!"
    echo ""
    echo "Você precisa criar o arquivo .env com:"
    echo "  - SECRET_KEY (chave criptográfica)"
    echo "  - DEBUG=False"
    echo "  - ALLOWED_HOSTS (seu domínio do PythonAnywhere)"
    echo ""
    echo "Use como referência: .env.production.template"
    exit 1
fi
print_success ".env encontrado"

# Step 8: Aplicar migrations
print_step "Aplicando migrations do banco de dados..."
python manage.py migrate

print_success "Migrations aplicadas"

# Step 9: Coletar arquivos estáticos
print_step "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

print_success "Arquivos estáticos coletados"

# Step 10: Verificar configuração
print_step "Executando verificações de segurança..."
python manage.py check --deploy 2>&1 | grep -i "warning\|error" || print_success "Verificações OK"

# ==============================================================================
# RESUMO E PRÓXIMOS PASSOS
# ==============================================================================

print_header "DEPLOYMENT CONCLUÍDO COM SUCESSO!"

echo ""
echo "Próximas ações:"
echo ""
echo "1. Configurar Web App no PythonAnywhere:"
echo "   • Ir para: Web → Web app → Virtualenv"
echo "   • Informar: $VENV_DIR"
echo ""
echo "2. Configurar WSGI:"
echo "   • Ir para: Web → Web app → Code"
echo "   • Editar: /var/www/seu_username_pythonanywhere_com_wsgi.py"
echo "   • Usar arquivo: gestao_terneiras/wsgi.py"
echo ""
echo "3. Configurar Static Files:"
echo "   • Ir para: Web → Web app → Static files"
echo "   • URL: /static/"
echo "   • Directory: $PROJECT_DIR/staticfiles"
echo ""
echo "4. Configurar Source code:"
echo "   • Ir para: Web → Web app → Code"
echo "   • Source code: $PROJECT_DIR"
echo ""
echo "4. Recarregar aplicação:"
echo "   • No painel: Web → Web app → Reload"
echo "   • Ou via console: touch /var/www/seu_username_pythonanywhere_com_wsgi.py"
echo ""
echo "5. Testar:"
echo "   • Abrir: https://seu-username.pythonanywhere.com"
echo "   • Fazer login"
echo "   • Verificar dashboard"
echo ""
echo "Documentação: DEPLOYMENT_PYTHONANYWHERE.md"
echo ""

print_success "Tudo pronto! O sistema está pronto para entrar online."

