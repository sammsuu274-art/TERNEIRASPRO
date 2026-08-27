from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Parto
    path('parto/novo/<int:ciclo_pk>/', views.registrar_parto, name='registrar_parto'),
    # Colostragem
    path('colostragem/<int:terneira_pk>/', views.registrar_colostragem, name='registrar_colostragem'),
    path('colostragem/<int:pk>/editar/', views.editar_colostragem, name='editar_colostragem'),
    path('colostragem/<int:pk>/excluir/', views.excluir_colostragem, name='excluir_colostragem'),
    path('colostragem/<int:terneira_pk>/lista/', views.lista_colostragens, name='lista_colostragens'),
    # Umbigo
    path('umbigo/<int:terneira_pk>/', views.registrar_cura_umbigo, name='registrar_cura_umbigo'),
    # Pesagem
    path('pesagem/<int:animal_pk>/', views.registrar_pesagem, name='registrar_pesagem'),
    path('pesagem/<int:animal_pk>/complementar/', views.registrar_pesagem_complementar, name='registrar_pesagem_complementar'),
    path('pesagem/<int:pk>/excluir/', views.excluir_pesagem, name='excluir_pesagem'),
    path('pesagem/<int:animal_pk>/historico/', views.historico_pesagens, name='historico_pesagens'),
    # Ocorrência sanitária
    path('sanitario/<int:animal_pk>/', views.registrar_ocorrencia, name='registrar_ocorrencia'),
    path('sanitario/<int:pk>/encerrar/', views.encerrar_ocorrencia, name='encerrar_ocorrencia'),
    # Vacinação
    path('vacinacao/<int:animal_pk>/', views.registrar_vacinacao, name='registrar_vacinacao'),
    # Desaleitamento
    path('desaleitamento/<int:terneira_pk>/', views.registrar_desaleitamento, name='registrar_desaleitamento'),
    # Banco de colostro
    path('banco-colostro/', views.lista_banco_colostro, name='lista_banco_colostro'),
    path('banco-colostro/novo/', views.novo_banco_colostro, name='novo_banco_colostro'),
    # Movimentação de lotes
    path('lote/mover/<int:animal_pk>/', views.mover_animal_lote, name='mover_animal_lote'),
]
