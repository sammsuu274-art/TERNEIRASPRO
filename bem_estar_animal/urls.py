from django.urls import path
from . import views

app_name = 'bem_estar_animal'

urlpatterns = [
    # Dashboard BEA
    path('', views.dashboard_bea, name='dashboard'),
    
    # Jornadas ProCampo
    path('jornadas/', views.lista_jornadas, name='lista_jornadas'),
    path('jornadas/nova/', views.nova_jornada, name='nova_jornada'),
    path('jornadas/<int:pk>/', views.detalhe_jornada, name='detalhe_jornada'),
    path('jornadas/<int:pk>/diagnostico/', views.diagnostico_jornada, name='diagnostico_jornada'),
    path('jornadas/<int:pk>/avaliacao/', views.avaliacao_jornada, name='avaliacao_jornada'),
    
    # Plano de Ação
    path('planos-acao/', views.lista_planos_acao, name='lista_planos_acao'),
    path('planos-acao/novo/', views.novo_plano_acao, name='novo_plano_acao'),
    path('planos-acao/<int:pk>/', views.detalhe_plano_acao, name='detalhe_plano_acao'),
    path('planos-acao/<int:pk>/editar/', views.editar_plano_acao, name='editar_plano_acao'),
    path('planos-acao/<int:pk>/alterar-situacao/', views.alterar_situacao_acao, name='alterar_situacao_acao'),
    
    # AmbienteBEA
    path('ambiente/', views.lista_ambiente_bea, name='lista_ambiente'),
    path('ambiente/novo/<int:terneira_pk>/', views.novo_ambiente_bea, name='novo_ambiente'),
    path('ambiente/<int:pk>/', views.detalhe_ambiente_bea, name='detalhe_ambiente'),
    
    # ComportamentoBEA
    path('comportamento/', views.lista_comportamento_bea, name='lista_comportamento'),
    path('comportamento/novo/<int:terneira_pk>/', views.novo_comportamento_bea, name='novo_comportamento'),
    path('comportamento/<int:pk>/', views.detalhe_comportamento_bea, name='detalhe_comportamento'),
    
    # VisitaPresencialBEA
    path('visitas/', views.lista_visitas_bea, name='lista_visitas'),
    path('visitas/nova/', views.nova_visita_bea, name='nova_visita'),
    path('visitas/<int:pk>/', views.detalhe_visita_bea, name='detalhe_visita'),
    
    # ConsentimentoBEA
    path('consentimentos/', views.lista_consentimentos_bea, name='lista_consentimentos'),
    path('consentimentos/novo/', views.novo_consentimento_bea, name='novo_consentimento'),
    path('consentimentos/<int:pk>/', views.detalhe_consentimento_bea, name='detalhe_consentimento'),
    
    # EvidenciasBEA
    path('evidencias/', views.lista_evidencias_bea, name='lista_evidencias'),
    path('evidencias/nova/', views.nova_evidencia_bea, name='nova_evidencia'),
    path('evidencias/<int:pk>/', views.detalhe_evidencia_bea, name='detalhe_evidencia'),
]