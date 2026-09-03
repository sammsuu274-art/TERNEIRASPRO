# GUIA DE IMPLEMENTAÇÃO — TerneirasPro para Equipe de Desenvolvimento

**Versão:** 1.0  
**Data:** Agosto 2026  
**Público:** Desenvolvedores Python/Django  
**Tempo Estimado:** 40-60 horas (bugs + melhorias + deploy)

---

## PARTE 1: ANTES DE COMEÇAR

### 1.1 Acesso ao Repositório

```bash
# Clone o repositório
git clone git@github.com:sammsuu274-art/TERNEIRASPRO.git
cd TERNEIRASPRO

# Estamos no branch main (único branch atualmente)
git branch -a
```

### 1.2 Setup Local (Python + Django)

```bash
# Criar virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env (copiar de .env.production.template)
cp .env.production.template .env

# Editar .env para desenvolvimento
# DEBUG=True
# SECRET_KEY=django-insecure-dev-key-mude-em-producao
# ALLOWED_HOSTS=localhost,127.0.0.1
```

### 1.3 Banco de Dados Local

```bash
# Aplicar migrações
python manage.py migrate

# Carregar dados de referência (9 referenciais técnicos)
python manage.py seed_referenciais

# Carregar critérios de conformidade (C1-C7)
python manage.py seed_criterios --propriedade 1

# Criar superusuário (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@test.local
# Password: admin123

# Iniciar servidor
python manage.py runserver
# Acesso: http://127.0.0.1:8000
```

### 1.4 Ler Documentação

**Ordem de leitura obrigatória:**
1. `LEIA_PRIMEIRO.md` — Navegação (você está aqui)
2. `DOCUMENTACAO_AGENTE.md` — Especificação completa (FONTE OFICIAL)
3. `GUIA_IMPLEMENTACAO_PARA_EQUIPE.md` — Para developers
4. `AUDITORIA_PRODUCAO.md` — Checklist pré-deploy

**Documentos complementares:**
- `IMPLEMENTACAO_LOGIN.md` — Design da tela de login
- `TELA_LOGIN_LAYOUT.md` — CSS da login (não alterar sem justificativa)
- `MANUAL_DO_USUARIO.md` — Guia operacional
- `.kiro/steering/projeto.md` — Regras permanentes do projeto

---

## PARTE 2: BUGS A CORRIGIR (Prioridade)

### 🔴 CRÍTICO #1: form_colostragem.html — meta_volume vazio

**Arquivo:** `templates/eventos/form_colostragem.html`  
**Problema:** Template exibe `{{ meta_volume }}` mas view não passa variável no contexto

**Passo 1: Verificar o template**
```html
<!-- templates/eventos/form_colostragem.html — procurar por: -->
<div class="form-text">
    Volume recomendado: {{ meta_volume }} ml (10% do peso ao nascer)
</div>
```

**Passo 2: Corrigir a view**
```python
# eventos/views.py — função registrar_colostragem()

def registrar_colostragem(request, terneira_pk):
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=request.propriedade_ativa, sexo='F')
    
    # Buscar peso de nascimento
    parto = Parto.objects.filter(terneira=terneira).first()
    peso_nascimento = parto.peso_nascimento if parto else None
    
    # Calcular meta de volume
    meta_volume = None
    if peso_nascimento:
        meta_volume = peso_nascimento * 100 * 0.10  # 10% do peso em ml
    
    if request.method == 'POST':
        form = ColostragemForm(request.POST, instance=None)
        if form.is_valid():
            colostragem = form.save(commit=False)
            colostragem.propriedade = request.propriedade_ativa
            colostragem.terneira = terneira
            colostragem.responsavel = request.user
            colostragem.save()
            
            # Dispara avaliador
            from indicadores.avaliadores import avaliar_evento_colostragem
            avaliar_evento_colostragem(colostragem)
            
            return redirect('animais:ficha_terneira', pk=terneira_pk)
    else:
        form = ColostragemForm()
    
    context = {
        'form': form,
        'terneira': terneira,
        'meta_volume': meta_volume,  # ADICIONAR ISSO
    }
    return render(request, 'eventos/form_colostragem.html', context)
```

**Passo 3: Testar**
- Acessar `/eventos/colostragem/<pk>/`
- Verificar que campo "Volume recomendado" exibe valor calculado
- Registrar colostragem e verificar que avaliador C1/C2/C3 dispara

**Tempo estimado:** 15 minutos

---

### 🔴 CRÍTICO #2: Sistema de Papéis — Implementar Verificação

**Problema:** Papéis existem (admin, tecnico, produtor, auxiliar) mas views NÃO verificam  
**Impacto:** Qualquer usuário autenticado acessa tudo

**Passo 1: Criar decorators**

```python
# core/decorators.py — criar novo arquivo

from functools import wraps
from django.http import HttpResponseForbidden, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import UsuarioPerfil

def permission_required(papeis):
    """
    Decorator que verifica se usuário tem um dos papéis necessários.
    
    Uso:
        @permission_required(['admin', 'tecnico'])
        def minha_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Buscar perfil do usuário na propriedade ativa
            perfil = UsuarioPerfil.objects.filter(
                usuario=request.user,
                propriedade=request.propriedade_ativa,
                ativo=True
            ).first()
            
            # Superusuário tem acesso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Usuário comum: verificar papel
            if not perfil or perfil.papel not in papeis:
                return HttpResponseForbidden(
                    "Você não tem permissão para acessar este recurso. "
                    f"Papéis permitidos: {', '.join(papeis)}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def admin_required(view_func):
    """Shortcut para views que requerem apenas admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            perfil = UsuarioPerfil.objects.filter(
                usuario=request.user,
                propriedade=request.propriedade_ativa,
                papel='admin',
                ativo=True
            ).first()
            if not perfil:
                return HttpResponseForbidden("Apenas administradores podem acessar.")
        return view_func(request, *args, **kwargs)
    return wrapper
```

**Passo 2: Aplicar em views críticas**

```python
# core/views_admin.py

from core.decorators import permission_required, admin_required

@admin_required
def painel_admin(request):
    """View já requer admin, é boa prática adicionar decorator explicitamente"""
    # ...

@admin_required
def criar_propriedade(request):
    # ...

@permission_required(['admin', 'tecnico'])
def criar_protocolo(request):
    """Apenas admin e técnico podem criar protocolos"""
    # ...

# animais/views.py

@permission_required(['admin', 'tecnico', 'produtor', 'auxiliar'])
def registrar_parto(request, ciclo_pk):
    """Qualquer perfil pode registrar eventos"""
    # ...

@admin_required
def deletar_animal(request, pk):
    """Apenas admin pode deletar"""
    # ...
```

**Passo 3: Testar**
- Login com usuário 'tecnico' → tenta acessar painel admin → recebe 403
- Login com usuário 'admin' → acessa painel admin → sucesso
- Criar testes unitários para decorator

**Tempo estimado:** 45 minutos (código + testes)

---

### 🟠 ALTA #3: SECRET_KEY Insegura — Gerar Chave Forte

**Problema:** `settings.py` tem valor padrão inseguro

**Passo 1: Gerar nova chave**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Exemplo output:
# z6#_7$@!vx9wnk2m4pq8r3s1t0u5v9w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6
```

**Passo 2: Adicionar a `.env.production`**
```
SECRET_KEY=z6#_7$@!vx9wnk2m4pq8r3s1t0u5v9w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6
DEBUG=False
ALLOWED_HOSTS=terneiraspro.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://terneiraspro.onrender.com
```

**Passo 3: Adicionar headers de segurança a settings.py**
```python
# gestao_terneiras/settings.py — adicionar no final

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Parse DATABASE_URL (se usar PostgreSQL)
    import dj_database_url
    if 'DATABASE_URL' in os.environ:
        DATABASES['default'] = dj_database_url.config(conn_max_age=600)
```

**Passo 4: Atualizar requirements.txt**
```
Django==4.2.16
python-decouple==3.8
Pillow==10.4.0
whitenoise==6.7.0
psycopg2-binary==2.9.9
gunicorn==21.2.0          # NOVO
dj-database-url==2.1.0    # NOVO
```

**Tempo estimado:** 20 minutos

---

### 🟠 ALTA #4: Critérios C8-C10 (Desaleitamento) — Implementar Avaliadores

**Problema:** Desaleitamento pode ser registrado fora dos padrões sem alerta  
**Critérios:**
- C8: `desaleitamento_idade_minima` (idade mínima para desaleitamento)
- C9: `desaleitamento_idade_maxima` (idade máxima)
- C10: `desaleitamento_peso_minimo` (peso mínimo)

**Passo 1: Criar avaliador em indicadores/avaliadores.py**

```python
def avaliar_evento_desaleitamento(desaleitamento):
    """
    Avalia conformidade do desaleitamento (C8, C9, C10).
    
    C8: Idade mínima para desaleitamento
    C9: Idade máxima para desaleitamento
    C10: Peso mínimo no desaleitamento
    """
    from indicadores.models import ResultadoConformidade
    from config_tecnica.models import CriterioConformidade
    from django.db.models import Q
    
    animal = desaleitamento.terneira
    propriedade = animal.propriedade
    
    # C8: Idade mínima
    try:
        criterio_c8 = CriterioConformidade.objects.get(
            propriedade=propriedade,
            codigo='desaleitamento_idade_minima'
        )
        
        idade_dias = (desaleitamento.data - animal.data_nascimento).days
        idade_minima = int(criterio_c8.valor_referencia or 60)
        
        resultado_c8 = 'conforme' if idade_dias >= idade_minima else 'nao_conforme'
        motivo_c8 = f"Desaleitamento aos {idade_dias} dias (mínimo: {idade_minima})"
        
        ResultadoConformidade.objects.get_or_create(
            animal=animal,
            criterio=criterio_c8,
            evento_tipo='desaleitamento',
            evento_id=desaleitamento.id,
            defaults={
                'propriedade': propriedade,
                'valor_observado': str(idade_dias),
                'valor_referencia': str(idade_minima),
                'resultado': resultado_c8,
                'desvio': str(idade_dias - idade_minima),
            }
        )
    except CriterioConformidade.DoesNotExist:
        pass  # Critério não configurado para esta propriedade
    
    # C9: Idade máxima
    try:
        criterio_c9 = CriterioConformidade.objects.get(
            propriedade=propriedade,
            codigo='desaleitamento_idade_maxima'
        )
        
        idade_dias = (desaleitamento.data - animal.data_nascimento).days
        idade_maxima = int(criterio_c9.valor_referencia or 90)
        
        resultado_c9 = 'conforme' if idade_dias <= idade_maxima else 'nao_conforme'
        
        ResultadoConformidade.objects.get_or_create(
            animal=animal,
            criterio=criterio_c9,
            evento_tipo='desaleitamento',
            evento_id=desaleitamento.id,
            defaults={
                'propriedade': propriedade,
                'valor_observado': str(idade_dias),
                'valor_referencia': str(idade_maxima),
                'resultado': resultado_c9,
                'desvio': str(idade_dias - idade_maxima),
            }
        )
    except CriterioConformidade.DoesNotExist:
        pass
    
    # C10: Peso mínimo
    try:
        criterio_c10 = CriterioConformidade.objects.get(
            propriedade=propriedade,
            codigo='desaleitamento_peso_minimo'
        )
        
        peso_minimo = float(criterio_c10.valor_referencia or 75)  # kg
        peso_atual = desaleitamento.peso_kg
        
        if peso_atual is None:
            resultado_c10 = 'dado_ausente'
            motivo = 'Peso no desaleitamento não informado'
        else:
            resultado_c10 = 'conforme' if peso_atual >= peso_minimo else 'nao_conforme'
            motivo = f"Peso: {peso_atual}kg (mínimo: {peso_minimo}kg)"
        
        ResultadoConformidade.objects.get_or_create(
            animal=animal,
            criterio=criterio_c10,
            evento_tipo='desaleitamento',
            evento_id=desaleitamento.id,
            defaults={
                'propriedade': propriedade,
                'valor_observado': str(peso_atual) if peso_atual else None,
                'valor_referencia': str(peso_minimo),
                'resultado': resultado_c10,
                'motivo_ausencia': motivo if resultado_c10 == 'dado_ausente' else None,
            }
        )
    except CriterioConformidade.DoesNotExist:
        pass
```

**Passo 2: Disparar avaliador na view de desaleitamento**

```python
# eventos/views.py

def registrar_desaleitamento(request, terneira_pk):
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=request.propriedade_ativa)
    
    if request.method == 'POST':
        form = DesaleitamentoForm(request.POST)
        if form.is_valid():
            desaleitamento = form.save(commit=False)
            desaleitamento.propriedade = request.propriedade_ativa
            desaleitamento.terneira = terneira
            desaleitamento.save()
            
            # IMPORTANTE: Disparar avaliador
            from indicadores.avaliadores import avaliar_evento_desaleitamento
            avaliar_evento_desaleitamento(desaleitamento)
            
            # Atualizar categoria
            terneira.categoria = 'novilha'
            terneira.save()
            
            return redirect('animais:ficha_terneira', pk=terneira_pk)
    else:
        form = DesaleitamentoForm()
    
    return render(request, 'eventos/form_desaleitamento.html', {
        'form': form,
        'terneira': terneira,
    })
```

**Passo 3: Seed de critérios (no seed_criterios.py)**

```python
# Adicionar ao comando seed_criterios

criterios_desaleitamento = [
    {
        'codigo': 'desaleitamento_idade_minima',
        'descricao': 'Idade mínima para desaleitamento',
        'valor_referencia': '60',  # dias
        'valor_minimo': '30',
        'valor_maximo': '120',
    },
    {
        'codigo': 'desaleitamento_idade_maxima',
        'descricao': 'Idade máxima para desaleitamento',
        'valor_referencia': '90',  # dias
        'valor_minimo': '30',
        'valor_maximo': '120',
    },
    {
        'codigo': 'desaleitamento_peso_minimo',
        'descricao': 'Peso mínimo no desaleitamento',
        'valor_referencia': '75',  # kg
        'valor_minimo': '40',
        'valor_maximo': '150',
    },
]
```

**Passo 4: Testar**
- Registrar desaleitamento com idade e peso abaixo do mínimo
- Verificar que ResultadoConformidade é criada com resultado='nao_conforme'
- Verificar dashboard exibe alerta

**Tempo estimado:** 1 hora

---

### 🟠 ALTA #5: Metas dos Gráficos — Remover Hardcode

**Problema:** Valores fixos em `_buscar_metas_graficos()` em `core/views_dashboard.py`

**Passo 1: Verificar código atual**

```python
# core/views_dashboard.py

def _buscar_metas_graficos(propriedade_id):
    return {
        'meta_colostro_tempo': 0.90,  # HARDCODED
        'meta_gmd': 0.75,             # HARDCODED
        'meta_diarreia': 0.15,        # HARDCODED
        'meta_peso_curva': 0.80,      # HARDCODED
    }
```

**Passo 2: Buscar de CriterioConformidade**

```python
def _buscar_metas_graficos(propriedade_id):
    from config_tecnica.models import CriterioConformidade
    
    criterios = CriterioConformidade.objects.filter(
        propriedade_id=propriedade_id,
        ativo=True
    ).values('codigo', 'valor_referencia')
    
    criterios_dict = {c['codigo']: c['valor_referencia'] for c in criterios}
    
    return {
        'meta_colostro_tempo': float(criterios_dict.get('colostragem_tempo', 0.90)),
        'meta_gmd': float(criterios_dict.get('peso_por_idade', 0.75)),
        'meta_diarreia': float(criterios_dict.get('incidencia_diarreia', 0.15)),
        'meta_peso_curva': float(criterios_dict.get('peso_por_idade', 0.80)),
    }
```

**Passo 3: Testar**
- Acessar dashboard
- Verificar que metas nos gráficos vêm de CriterioConformidade

**Tempo estimado:** 30 minutos

---

## PARTE 3: FUNCIONALIDADES PENDENTES (Sem Prioridade, Futuro)

### MovimentacaoLote — Implementar UI (Se Fizer Sentido)

**Status:** Modelo pronto, falta formulário

**Opção A: Implementar (3-4 horas)**
```
Criar view /animais/lotes/<pk>/mover/
Formulário: animal + data_movimentacao + novo_lote
Histórico preservado em MovimentacaoLote
```

**Opção B: Documentar como "futuro" (30 minutos)**
```
Colocar em backlog
Adicionar comentário no modelo
```

### ProtocoloAlimentar — Decidir Sorte

**Opção A: Remover modelos (não usados)**
```bash
# Se decidir remover:
python manage.py makemigrations
# Criar migration: 
#   - DELETE MODEL ProtocoloAlimentar
#   - DELETE MODEL RegistroAlimentacaoDiario
python manage.py migrate
```

**Opção B: Implementar UI (6-8 horas)**
```
Criar views, formulários, templates
Integrar com animal.programa
```

**Recomendação:** Remover se não está no escopo atual

---

## PARTE 4: TESTES

### 4.1 Testes Unitários (Mínimo Viável)

```python
# tests.py — criar arquivo em cada app

# indicadores/tests.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .avaliadores import avaliar_evento_parto, avaliar_evento_colostragem

class AvaliadoresTestCase(TestCase):
    def setUp(self):
        self.propriedade = Propriedade.objects.create(nome='Teste')
        self.usuario = Usuario.objects.create_user('test', 'test@test.local', 'pass')
        self.vaca = Animal.objects.create(
            propriedade=self.propriedade,
            identificacao='VAC001',
            categoria='vaca',
            sexo='F'
        )
        self.ciclo = CicloReprodutivo.objects.create(
            propriedade=self.propriedade,
            vaca=self.vaca,
            numero_lactacao=1
        )
    
    def test_conformidade_parto_dias_secos_conforme(self):
        """Testa C5: dias secos dentro do esperado"""
        data_parto = timezone.now().date()
        data_secagem = data_parto - timedelta(days=60)  # 60 dias secos
        
        self.ciclo.data_secagem = data_secagem
        self.ciclo.save()
        
        parto = Parto.objects.create(
            propriedade=self.propriedade,
            ciclo=self.ciclo,
            terneira=Animal.objects.create(
                propriedade=self.propriedade,
                identificacao='TER001',
                categoria='terneira',
                sexo='F'
            ),
            data_parto=data_parto,
            peso_nascimento=40,
            registrado_por=self.usuario
        )
        
        avaliar_evento_parto(parto)
        
        resultado = ResultadoConformidade.objects.filter(
            criterio__codigo='dias_secos_minimo'
        ).first()
        
        self.assertEqual(resultado.resultado, 'conforme')
```

**Tempo estimado:** 4-6 horas (suite básica)

---

### 4.2 Testes de Integração

```bash
# Fluxo completo: Parto → Colostragem → Conformidades
# Testar via Django TestClient

python manage.py test indicadores --verbosity=2
```

---

## PARTE 5: DEPLOYMENT

### 5.1 Preparar para Render.com

**Passo 1: Criar Procfile**
```
# Procfile (raiz do projeto)

web: gunicorn gestao_terneiras.wsgi:application
```

**Passo 2: Criar requirements-prod.txt (opcional)**
```
# requirements-prod.txt (ou adicionar a requirements.txt)

Django==4.2.16
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-decouple==3.8
Pillow==10.4.0
whitenoise==6.7.0
dj-database-url==2.1.0
```

**Passo 3: Atualizar settings.py para produção**
```python
# gestao_terneiras/settings.py

import os
import dj_database_url

if not DEBUG:
    # SSL/HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    
    # Database
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
```

**Passo 4: Fazer commit e push**
```bash
git add Procfile requirements.txt gestao_terneiras/settings.py
git commit -m "Preparar para deploy em Render.com"
git push -u origin main
```

### 5.2 Deploy no Render.com

1. Acesso: render.com
2. Conectar GitHub (sammsuu274-art/TERNEIRASPRO)
3. Criar Web Service:
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn gestao_terneiras.wsgi:application`
4. Criar PostgreSQL Database
5. Configurar environment variables (ver AUDITORIA_PRODUCAO.md)

---

## PARTE 6: CHECKLIST FINAL

```
ANTES DE COMEÇAR:
☐ Clonar repositório
☐ Setup venv + pip install
☐ Ler documentação (LEIA_PRIMEIRO.md → DOCUMENTACAO_AGENTE.md)
☐ python manage.py runserver funciona

CORRIGIR BUGS:
☐ form_colostragem.html — meta_volume (15 min)
☐ Sistema de papéis — permission_required decorator (45 min)
☐ SECRET_KEY — gerar chave forte (20 min)
☐ Critérios C8-C10 — implementar avaliadores (1 hora)
☐ Metas gráficos — remover hardcode (30 min)

TESTES:
☐ Testes unitários para avaliadores (4-6 horas)
☐ Testar fluxo completo: parto → programa → checkpoint
☐ Testar dashboard recalcula KPIs
☐ Testar permission_required bloqueia usuários sem papel

DOCUMENTAÇÃO:
☐ Atualizar README.md com quick start
☐ Criar DEPLOY.md com instruções Render
☐ Criar TROUBLESHOOTING.md

DEPLOYMENT:
☐ Procfile criado
☐ requirements.txt atualizado
☐ settings.py configurado para produção
☐ Git commit + push
☐ Deploy em Render.com
☐ Testar em produção (login, create animal, dashboard)
☐ Ativar backup automático de database

APÓS DEPLOY:
☐ Monitorar logs (Render dashboard)
☐ Testar acesso de fora
☐ Documentar qualquer problema encontrado
☐ Setup alertas de erro (Sentry opcional)
```

---

## SUPORTE

**Dúvidas técnicas?**
- Documentação técnica: `DOCUMENTACAO_AGENTE.md`
- Regras do projeto: `.kiro/steering/projeto.md`
- Issues GitHub: criar issue no repositório

**Problemas em produção?**
- Logs: Render dashboard → Logs
- Database: verificar conexão PostgreSQL
- Static files: executar `collectstatic` novamente

---

**Bom desenvolvimento!**

Tempo total estimado: **40-60 horas** (bugs + melhorias + testes + deploy)

