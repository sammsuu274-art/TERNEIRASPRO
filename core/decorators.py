"""
Decorators de permissão para controle de acesso baseado em papel.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def papel_minimo_required(*papeis_permitidos):
    """
    Decorator que verifica se o usuário tem um dos papéis especificados.
    
    Uso:
        @papel_minimo_required('admin', 'tecnico')
        def minha_view(request):
            ...
    
    Papéis disponíveis (ordem de privilégio):
        - 'admin': acesso total
        - 'tecnico': criação/edição
        - 'produtor': consulta + operacional básico
        - 'auxiliar': consulta apenas
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Superusuário sempre passa
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar se usuário tem perfil ativo na propriedade ativa
            if not hasattr(request, 'propriedade_ativa') or not request.propriedade_ativa:
                messages.error(request, 'Nenhuma propriedade ativa selecionada.')
                return redirect('/')
            
            # Buscar perfil do usuário para a propriedade ativa
            from accounts.models import UsuarioPerfil
            try:
                perfil = UsuarioPerfil.objects.get(
                    usuario=request.user,
                    propriedade=request.propriedade_ativa,
                    ativo=True
                )
            except UsuarioPerfil.DoesNotExist:
                messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
                return redirect('/')
            
            # Verificar se o papel do usuário está na lista permitida
            if perfil.papel in papeis_permitidos:
                return view_func(request, *args, **kwargs)
            
            # Permissão negada
            messages.error(request, f'Acesso negado. Esta ação requer um dos seguintes papéis: {", ".join(papeis_permitidos)}. Seu papel: {perfil.get_papel_display()}.')
            return redirect('/')
        
        return wrapper
    return decorator


def admin_only(view_func):
    """
    Atalho para @papel_minimo_required('admin').
    Apenas administradores podem acessar.
    """
    return papel_minimo_required('admin')(view_func)


def admin_ou_tecnico(view_func):
    """
    Atalho para @papel_minimo_required('admin', 'tecnico').
    Administradores e técnicos podem acessar.
    """
    return papel_minimo_required('admin', 'tecnico')(view_func)
