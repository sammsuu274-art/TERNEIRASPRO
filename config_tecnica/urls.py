from django.urls import path
from . import views

app_name = 'config_tecnica'

urlpatterns = [
    path('', views.painel_config, name='painel'),
    path('protocolos/', views.lista_protocolos, name='lista_protocolos'),
    path('protocolos/novo/', views.novo_protocolo, name='novo_protocolo'),
    path('metas/', views.lista_metas, name='lista_metas'),
    path('metas/nova/', views.nova_meta, name='nova_meta'),
    path('metas/<int:pk>/', views.detalhe_meta, name='detalhe_meta'),
    path('meta-reprodutiva/', views.lista_metas_reprodutivas, name='lista_metas_reprodutivas'),
    path('meta-reprodutiva/nova/', views.nova_meta_reprodutiva, name='nova_meta_reprodutiva'),
    path('referenciais/', views.lista_referenciais, name='lista_referenciais'),
    path('criterios/', views.lista_criterios, name='lista_criterios'),
    path('criterios/novo/', views.novo_criterio, name='novo_criterio'),
    path('criterios/<int:pk>/editar/', views.editar_criterio, name='editar_criterio'),
]
