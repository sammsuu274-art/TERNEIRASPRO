from django.contrib import admin
from .models import Propriedade


@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'municipio', 'estado', 'responsavel_tecnico', 'ativa')
    list_filter = ('ativa', 'estado')
    search_fields = ('nome', 'municipio', 'responsavel_tecnico')
