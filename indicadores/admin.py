from django.contrib import admin
from .models import ResultadoConformidade


@admin.register(ResultadoConformidade)
class ResultadoConformidadeAdmin(admin.ModelAdmin):
    list_display = (
        'animal', 'criterio_display', 'data_evento',
        'valor_observado', 'valor_referencia', 'desvio', 'resultado',
    )
    list_filter = ('resultado', 'evento_tipo', 'criterio')
    search_fields = ('animal__identificacao',)
    readonly_fields = (
        'animal', 'criterio', 'meta_desenvolvimento',
        'data_evento', 'evento_tipo', 'evento_id',
        'valor_observado', 'valor_referencia', 'desvio',
        'resultado', 'calculado_em',
    )
    date_hierarchy = 'data_evento'

    def criterio_display(self, obj):
        return str(obj.criterio) if obj.criterio else 'Peso por idade'
    criterio_display.short_description = 'Critério'

    def has_add_permission(self, request):
        return False  # Resultados só são criados pelos avaliadores

    def has_change_permission(self, request, obj=None):
        return False  # Resultados são imutáveis
