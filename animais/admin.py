from django.contrib import admin
from .models import Animal, Lote, MovimentacaoLote, CicloReprodutivo


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('identificacao', 'nome', 'sexo', 'raca', 'categoria', 'situacao', 'data_nascimento', 'propriedade')
    list_filter = ('sexo', 'raca', 'categoria', 'situacao', 'propriedade')
    search_fields = ('identificacao', 'nome')
    raw_id_fields = ('mae',)


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'propriedade', 'ativo', 'total_animais')
    list_filter = ('tipo', 'ativo', 'propriedade')


@admin.register(MovimentacaoLote)
class MovimentacaoLoteAdmin(admin.ModelAdmin):
    list_display = ('animal', 'lote', 'data', 'registrado_por')
    list_filter = ('lote', 'data')
    raw_id_fields = ('animal',)


@admin.register(CicloReprodutivo)
class CicloReprodutivoAdmin(admin.ModelAdmin):
    list_display = ('vaca', 'numero_lactacao', 'data_previsao_parto', 'data_secagem', 'situacao')
    list_filter = ('situacao',)
    raw_id_fields = ('vaca',)
