from .models import Propriedade


class PropriedadeMiddleware:
    """
    Injeta a propriedade ativa na requisição.

    Regras:
    - Superusuário (is_superuser) tem acesso a qualquer propriedade.
      Se não tiver sessão ativa, pega a primeira propriedade existente.
      Se não existir nenhuma, permite acesso sem propriedade (para criar a primeira).
    - Usuário comum: precisa ter UsuarioPerfil vinculado a uma propriedade.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.propriedade_ativa = None
        request.is_master = False

        if request.user.is_authenticated:
            request.is_master = request.user.is_superuser
            propriedade_id = request.session.get('propriedade_ativa_id')

            if propriedade_id:
                try:
                    if request.user.is_superuser:
                        # Superusuário pode acessar qualquer propriedade ativa
                        request.propriedade_ativa = Propriedade.objects.get(
                            pk=propriedade_id, ativa=True,
                        )
                    else:
                        request.propriedade_ativa = Propriedade.objects.get(
                            pk=propriedade_id,
                            usuarioperfil__usuario=request.user,
                            ativa=True,
                        )
                except Propriedade.DoesNotExist:
                    request.session.pop('propriedade_ativa_id', None)

            # Sem propriedade ativa na sessão — tenta resolver automaticamente
            if not request.propriedade_ativa:
                if request.user.is_superuser:
                    # Superusuário: pega a primeira propriedade existente
                    prop = Propriedade.objects.filter(ativa=True).first()
                    if prop:
                        request.propriedade_ativa = prop
                        request.session['propriedade_ativa_id'] = prop.pk
                    # Se não existe nenhuma, deixa None — tela de primeiro acesso vai aparecer
                else:
                    from accounts.models import UsuarioPerfil
                    perfis = UsuarioPerfil.objects.filter(
                        usuario=request.user,
                        propriedade__ativa=True,
                        ativo=True,
                    ).select_related('propriedade')
                    if perfis.count() == 1:
                        request.propriedade_ativa = perfis.first().propriedade
                        request.session['propriedade_ativa_id'] = request.propriedade_ativa.pk

        response = self.get_response(request)
        return response
