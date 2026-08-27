from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


@never_cache
@csrf_protect
def login_view(request):
    """
    View de login moderna e funcional integrada ao Django Auth
    """
    # Se o usuário já está autenticado, redireciona para o dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'
        
        # Validação básica
        if not username or not password:
            messages.error(request, 'Usuário e senha são obrigatórios.')
            return render(request, 'accounts/login.html')
        
        # Tentativa de autenticação
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Configurar duração da sessão baseado em "lembrar-me"
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(0)  # Expira ao fechar o navegador
                
                # Redirecionamento inteligente
                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                
                messages.success(request, f'Bem-vindo ao TerneirasPro, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Sua conta está desativada. Entre em contato com o administrador.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """
    View de logout
    """
    username = request.user.username
    logout(request)
    messages.info(request, f'Você saiu do sistema. Até logo, {username}!')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """
    Dashboard principal do sistema
    """
    context = {
        'user': request.user,
        'title': 'Dashboard - TerneirasPro'
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def perfil_view(request):
    """
    Página de perfil do usuário
    """
    context = {
        'user': request.user,
        'title': 'Meu Perfil - TerneirasPro'
    }
    return render(request, 'accounts/perfil.html', context)


def check_user_status(request):
    """
    API endpoint para verificar status do usuário
    Usado para validações AJAX
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        try:
            from .models import Usuario
            user = Usuario.objects.get(username=username)
            
            return JsonResponse({
                'exists': True,
                'is_active': user.is_active,
                'full_name': user.nome_completo or user.username
            })
        except Usuario.DoesNotExist:
            return JsonResponse({
                'exists': False,
                'is_active': False,
                'full_name': ''
            })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)