"""
Painel de administração do sistema — acessível apenas para superusuários.
Permite gerenciar propriedades, usuários e vínculos pela interface web.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Propriedade


def _exige_master(request):
    """Retorna True se o usuário NÃO é superusuário (para bloquear acesso)."""
    return not (hasattr(request, 'user') and request.user.is_superuser)


# ---------------------------------------------------------------------------
# PRIMEIRO ACESSO — criar a primeira propriedade
# ---------------------------------------------------------------------------

def primeiro_acesso(request):
    """
    Exibido quando superusuário não tem nenhuma propriedade cadastrada.
    Cria a propriedade e vincula o próprio usuário como admin.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Acesso restrito ao administrador do sistema.')
        return redirect('/')

    if Propriedade.objects.exists():
        # Já existe ao menos uma propriedade — ativa a primeira e vai para o dashboard
        prop = Propriedade.objects.first()
        prop.ativa = True
        prop.save(update_fields=['ativa'])
        from accounts.models import UsuarioPerfil
        UsuarioPerfil.objects.get_or_create(
            usuario=request.user,
            propriedade=prop,
            defaults={'papel': 'admin', 'ativo': True},
        )
        request.session['propriedade_ativa_id'] = prop.pk
        return redirect('/')

    if request.method == 'POST':
        from .forms import PropriedadeForm
        form = PropriedadeForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.ativa = True  # garante sempre ativa no primeiro acesso
            prop.save()
            # Vincula o superusuário como admin da propriedade
            from accounts.models import UsuarioPerfil
            UsuarioPerfil.objects.get_or_create(
                usuario=request.user,
                propriedade=prop,
                defaults={'papel': 'admin', 'ativo': True},
            )
            request.session['propriedade_ativa_id'] = prop.pk
            messages.success(request, f'Propriedade "{prop.nome}" criada com sucesso. Bem-vindo ao TerneirasPro!')
            return redirect('/')
    else:
        from .forms import PropriedadeForm
        form = PropriedadeForm()

    return render(request, 'admin_sistema/primeiro_acesso.html', {'form': form})


# ---------------------------------------------------------------------------
# PAINEL PRINCIPAL DO ADMIN
# ---------------------------------------------------------------------------

def painel_admin(request):
    if _exige_master(request):
        messages.error(request, 'Acesso restrito ao administrador do sistema.')
        return redirect('/')

    from accounts.models import Usuario, UsuarioPerfil

    ctx = {
        'n_propriedades': Propriedade.objects.filter(ativa=True).count(),
        'n_usuarios': Usuario.objects.filter(is_active=True).count(),
        'n_vinculos': UsuarioPerfil.objects.filter(ativo=True).count(),
        'propriedades': Propriedade.objects.filter(ativa=True).order_by('nome'),
    }
    return render(request, 'admin_sistema/painel_admin.html', ctx)


# ---------------------------------------------------------------------------
# GESTÃO DE PROPRIEDADES
# ---------------------------------------------------------------------------

def lista_propriedades(request):
    if _exige_master(request):
        return redirect('/')
    props = Propriedade.objects.all().order_by('nome')
    return render(request, 'admin_sistema/lista_propriedades.html', {'propriedades': props})


def nova_propriedade(request):
    if _exige_master(request):
        return redirect('/')

    from .forms import PropriedadeForm
    if request.method == 'POST':
        form = PropriedadeForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.ativa = True
            prop.save()
            messages.success(request, f'Propriedade "{prop.nome}" criada.')
            return redirect('core:lista_propriedades')
    else:
        form = PropriedadeForm()

    return render(request, 'admin_sistema/form_propriedade.html', {
        'form': form, 'titulo': 'Nova Propriedade',
    })


def editar_propriedade(request, pk):
    if _exige_master(request):
        return redirect('/')

    prop = get_object_or_404(Propriedade, pk=pk)
    from .forms import PropriedadeEditForm
    if request.method == 'POST':
        form = PropriedadeEditForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriedade atualizada.')
            return redirect('core:lista_propriedades')
    else:
        form = PropriedadeEditForm(instance=prop)

    return render(request, 'admin_sistema/form_propriedade.html', {
        'form': form, 'titulo': f'Editar — {prop.nome}', 'prop': prop,
    })


@require_POST
def selecionar_propriedade_admin(request, pk):
    """Troca a propriedade ativa para o superusuário."""
    if _exige_master(request):
        return redirect('/')
    prop = get_object_or_404(Propriedade, pk=pk, ativa=True)
    request.session['propriedade_ativa_id'] = prop.pk
    messages.success(request, f'Propriedade ativa: {prop.nome}')
    return redirect(request.POST.get('next', '/'))


# ---------------------------------------------------------------------------
# GESTÃO DE USUÁRIOS
# ---------------------------------------------------------------------------

def lista_usuarios(request):
    if _exige_master(request):
        return redirect('/')

    from accounts.models import Usuario, UsuarioPerfil
    usuarios = Usuario.objects.all().order_by('username').prefetch_related('perfis__propriedade')
    return render(request, 'admin_sistema/lista_usuarios.html', {'usuarios': usuarios})


def novo_usuario(request):
    if _exige_master(request):
        return redirect('/')

    from .forms import NovoUsuarioForm
    if request.method == 'POST':
        form = NovoUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário "{user.username}" criado.')
            return redirect('core:lista_usuarios')
    else:
        form = NovoUsuarioForm()

    return render(request, 'admin_sistema/form_usuario.html', {
        'form': form, 'titulo': 'Novo Usuário',
    })


def editar_usuario(request, pk):
    if _exige_master(request):
        return redirect('/')

    from accounts.models import Usuario
    from .forms import EditarUsuarioForm
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado.')
            return redirect('core:lista_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'admin_sistema/form_usuario.html', {
        'form': form, 'titulo': f'Editar — {usuario.username}', 'usuario': usuario,
    })


# ---------------------------------------------------------------------------
# GESTÃO DE VÍNCULOS (usuário ↔ propriedade)
# ---------------------------------------------------------------------------

def lista_vinculos(request):
    if _exige_master(request):
        return redirect('/')

    from accounts.models import UsuarioPerfil
    vinculos = UsuarioPerfil.objects.all().select_related('usuario', 'propriedade').order_by('propriedade__nome', 'usuario__username')
    return render(request, 'admin_sistema/lista_vinculos.html', {'vinculos': vinculos})


def novo_vinculo(request):
    if _exige_master(request):
        return redirect('/')

    from .forms import VinculoForm
    if request.method == 'POST':
        form = VinculoForm(request.POST)
        if form.is_valid():
            vinculo = form.save()
            messages.success(request, f'{vinculo.usuario} vinculado a {vinculo.propriedade} como {vinculo.get_papel_display()}.')
            return redirect('core:lista_vinculos')
    else:
        form = VinculoForm()

    return render(request, 'admin_sistema/form_vinculo.html', {
        'form': form, 'titulo': 'Novo Vínculo',
    })


@require_POST
def remover_vinculo(request, pk):
    if _exige_master(request):
        return redirect('/')

    from accounts.models import UsuarioPerfil
    vinculo = get_object_or_404(UsuarioPerfil, pk=pk)
    nome = str(vinculo)
    vinculo.delete()
    messages.success(request, f'Vínculo removido: {nome}')
    return redirect('core:lista_vinculos')
