from django.shortcuts import redirect, get_object_or_404
from .models import Propriedade


def selecionar_propriedade(request, pk):
    """Troca a propriedade ativa na sessão do usuário."""
    propriedade = get_object_or_404(
        Propriedade,
        pk=pk,
        usuarioperfil__usuario=request.user,
        ativa=True,
    )
    request.session['propriedade_ativa_id'] = propriedade.pk
    next_url = request.GET.get('next', '/')
    return redirect(next_url)
