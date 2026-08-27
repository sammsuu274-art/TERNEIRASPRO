from django.urls import path
from . import views

app_name = 'animais'

urlpatterns = [
    # Terneiras
    path('', views.lista_terneiras, name='lista_terneiras'),
    path('nova/', views.nova_terneira, name='nova_terneira'),
    path('<int:pk>/', views.detalhe_terneira, name='detalhe_terneira'),
    path('<int:pk>/editar/', views.editar_terneira, name='editar_terneira'),
    # Vacas mãe
    path('vacas/', views.lista_vacas, name='lista_vacas'),
    path('vacas/nova/', views.nova_vaca, name='nova_vaca'),
    path('vacas/<int:pk>/', views.detalhe_vaca, name='detalhe_vaca'),
    # Lotes
    path('lotes/', views.lista_lotes, name='lista_lotes'),
    path('lotes/novo/', views.novo_lote, name='novo_lote'),
    path('lotes/<int:pk>/', views.detalhe_lote, name='detalhe_lote'),
    # Ciclos reprodutivos
    path('vacas/<int:vaca_pk>/ciclo/novo/', views.novo_ciclo, name='novo_ciclo'),
]
