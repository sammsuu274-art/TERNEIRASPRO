from django.shortcuts import redirect, get_object_or_404
from .models import Propriedade


def selecionar_propriedade(request, pk):
    """Troca a propriedade ativa na sessão do usuário."""
    
    # Superuser pode acessar qualquer propriedade ativa
    if request.user.is_superuser:
        propriedade = get_object_or_404(Propriedade, pk=pk, ativa=True)
    else:
        # Usuário comum precisa ter vínculo ativo
        propriedade = get_object_or_404(
            Propriedade,
            pk=pk,
            usuarioperfil__usuario=request.user,
            usuarioperfil__ativo=True,
            ativa=True,
        )
    
    request.session['propriedade_ativa_id'] = propriedade.pk
    next_url = request.GET.get('next', '/')
    return redirect(next_url)
