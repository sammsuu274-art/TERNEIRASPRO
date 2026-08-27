from django.contrib import admin
from .models import (
    Protocolo, MetaDesenvolvimento, PontoMetaDesenvolvimento,
    MetaReprodutiva, ReferencialTecnico, CriterioConformidade,
)


@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'versao', 'vigencia_inicio', 'vigencia_fim', 'vigente')
    list_filter = ('categoria', 'propriedade')


class PontoMetaInline(admin.TabularInline):
    model = PontoMetaDesenvolvimento
    extra = 3


@admin.register(MetaDesenvolvimento)
class MetaDesenvolvimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'raca', 'fonte', 'ativa')
    list_filter = ('raca', 'ativa')
    inlines = [PontoMetaInline]


@admin.register(MetaReprodutiva)
class MetaReprodutivaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'raca', 'peso_minimo_kg', 'percentual_peso_adulto', 'idade_alvo_meses', 'ativa')
    list_filter = ('raca', 'ativa')


@admin.register(ReferencialTecnico)
class ReferencialTecnicoAdmin(admin.ModelAdmin):
    list_display = ('indicador', 'valor_ideal', 'unidade', 'fonte', 'ano', 'ativo')
    list_filter = ('indicador', 'ativo')


@admin.register(CriterioConformidade)
class CriterioConformidadeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'valor_limite', 'unidade', 'escopo_raca', 'vigencia_inicio', 'vigente', 'ativo')
    list_filter = ('codigo', 'ativo', 'escopo_raca', 'propriedade')
    search_fields = ('codigo', 'descricao_custom')
