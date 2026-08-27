from django.urls import path
from . import views, views_admin

app_name = 'core'

urlpatterns = [
    # Seleção de propriedade (usuário comum e superusuário)
    path('selecionar/<int:pk>/', views.selecionar_propriedade, name='selecionar_propriedade'),

    # Primeiro acesso (criar primeira propriedade)
    path('primeiro-acesso/', views_admin.primeiro_acesso, name='primeiro_acesso'),

    # Painel de administração do sistema
    path('admin-sistema/', views_admin.painel_admin, name='painel_admin'),

    # Propriedades
    path('admin-sistema/propriedades/', views_admin.lista_propriedades, name='lista_propriedades'),
    path('admin-sistema/propriedades/nova/', views_admin.nova_propriedade, name='nova_propriedade'),
    path('admin-sistema/propriedades/<int:pk>/editar/', views_admin.editar_propriedade, name='editar_propriedade'),
    path('admin-sistema/propriedades/<int:pk>/selecionar/', views_admin.selecionar_propriedade_admin, name='selecionar_propriedade_admin'),

    # Usuários
    path('admin-sistema/usuarios/', views_admin.lista_usuarios, name='lista_usuarios'),
    path('admin-sistema/usuarios/novo/', views_admin.novo_usuario, name='novo_usuario'),
    path('admin-sistema/usuarios/<int:pk>/editar/', views_admin.editar_usuario, name='editar_usuario'),

    # Vínculos
    path('admin-sistema/vinculos/', views_admin.lista_vinculos, name='lista_vinculos'),
    path('admin-sistema/vinculos/novo/', views_admin.novo_vinculo, name='novo_vinculo'),
    path('admin-sistema/vinculos/<int:pk>/remover/', views_admin.remover_vinculo, name='remover_vinculo'),
]
