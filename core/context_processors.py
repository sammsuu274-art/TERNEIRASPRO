from accounts.models import UsuarioPerfil


def propriedade_ativa(request):
    """
    Disponibiliza a propriedade ativa e lista de propriedades do usuário em todos os templates.
    Superusuário enxerga todas as propriedades ativas, não apenas as vinculadas.
    """
    ctx = {
        'propriedade_ativa': None,
        'propriedades_usuario': [],
    }

    if request.user.is_authenticated:
        ctx['propriedade_ativa'] = getattr(request, 'propriedade_ativa', None)

        if request.user.is_superuser:
            from .models import Propriedade
            ctx['propriedades_usuario'] = list(
                Propriedade.objects.filter(ativa=True)
                .values_list('id', 'nome')
                .order_by('nome')
            )
        else:
            ctx['propriedades_usuario'] = list(
                UsuarioPerfil.objects.filter(
                    usuario=request.user,
                    propriedade__ativa=True,
                    ativo=True,
                ).select_related('propriedade')
                .values_list('propriedade__id', 'propriedade__nome')
                .order_by('propriedade__nome')
            )

    return ctx
