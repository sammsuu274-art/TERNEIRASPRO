from django.contrib import admin
from .models import ProgramaAcompanhamento, CheckpointSesMeses, ProjecaoReprodutiva, CoberturaIA


@admin.register(ProgramaAcompanhamento)
class ProgramaAcompanhamentoAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_inicio', 'duracao_dias', 'status', 'percentual_concluido')
    list_filter = ('status',)
    raw_id_fields = ('terneira',)


@admin.register(CheckpointSesMeses)
class CheckpointSesMesesAdmin(admin.ModelAdmin):
    list_display = ('programa', 'data_avaliacao', 'idade_dias', 'peso_kg', 'percentual_meta', 'status_checkpoint', 'status_trajetoria')
    list_filter = ('status_checkpoint', 'status_trajetoria')


@admin.register(ProjecaoReprodutiva)
class ProjecaoReprodutivaAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_calculo', 'peso_atual_kg', 'peso_alvo_kg', 'data_estimada', 'status_trajetoria')
    list_filter = ('status_trajetoria',)


@admin.register(CoberturaIA)
class CoberturaIAAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data', 'tipo', 'numero_servico', 'resultado')
    list_filter = ('tipo', 'resultado')
