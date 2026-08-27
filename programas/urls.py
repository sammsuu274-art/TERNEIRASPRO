from django.urls import path
from . import views

app_name = 'programas'

urlpatterns = [
    path('', views.lista_programas, name='lista_programas'),
    path('<int:pk>/', views.detalhe_programa, name='detalhe_programa'),
    path('<int:pk>/checkpoint/', views.checkpoint_ses_meses, name='checkpoint'),
    path('checkpoint/<int:pk>/', views.detalhe_checkpoint, name='detalhe_checkpoint'),
    path('projecao/<int:terneira_pk>/', views.projecao_reprodutiva, name='projecao_reprodutiva'),
    path('aptas/', views.lista_aptas_reproducao, name='lista_aptas_reproducao'),
    path('ia/<int:terneira_pk>/', views.registrar_cobertura_ia, name='registrar_ia'),
]
