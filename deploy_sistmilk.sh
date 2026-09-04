#!/bin/bash
# ==============================================================================
# DEPLOY AUTOMÁTICO - TERNEIRASPRO NO PYTHONANYWHERE
# Username: sistmilk
# ==============================================================================

set -e

echo "🚀 Iniciando atualização do TerneirasPro..."

# Backup do banco
echo "📦 Fazendo backup do banco de dados..."
cd ~/TERNEIRAS
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "Banco não encontrado (primeira vez?)"

# Baixar código atualizado
echo "⬇️  Baixando código do GitHub..."
git pull origin main

# Ativar venv
echo "🔧 Ativando ambiente virtual..."
source ~/venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt --quiet

# Aplicar migrations
echo "🗄️  Aplicando migrations do banco..."
python manage.py migrate

# Coletar estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Verificar
echo "✅ Verificando sistema..."
python manage.py check --deploy

# Recarregar site
echo "🔄 Recarregando site..."
touch /var/www/sistmilk_pythonanywhere_com_wsgi.py

echo ""
echo "✅ ================================"
echo "✅  DEPLOY CONCLUÍDO COM SUCESSO!"
echo "✅ ================================"
echo ""
echo "🌐 Acesse: https://sistmilk.pythonanywhere.com"
echo ""
