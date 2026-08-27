from django.contrib import admin
from .models import (
    Parto, BancoColostro, Colostragem, CuraUmbigo,
    Pesagem, OcorrenciaSanitaria, Vacinacao,
    ProtocoloAlimentar, RegistroAlimentacaoDiario, Desaleitamento,
)


@admin.register(Parto)
class PartoAdmin(admin.ModelAdmin):
    list_display = ('ciclo', 'terneira', 'data_parto', 'facilidade', 'peso_nascimento', 'vitalidade')
    list_filter = ('facilidade', 'vitalidade', 'gemelar')
    raw_id_fields = ('ciclo', 'terneira')


@admin.register(BancoColostro)
class BancoColostroAdmin(admin.ModelAdmin):
    list_display = ('lote', 'data_coleta', 'volume_ml', 'brix', 'status', 'congelado')
    list_filter = ('status', 'congelado', 'propriedade')


@admin.register(Colostragem)
class ColostragemmAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_hora', 'volume_ml', 'origem', 'metodo', 'brix')
    raw_id_fields = ('terneira',)


@admin.register(CuraUmbigo)
class CuraUmbigoAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_hora', 'produto', 'suspeita_onfalite')
    raw_id_fields = ('terneira',)


@admin.register(Pesagem)
class PesagemAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data', 'peso_kg', 'altura_garupa_cm', 'metodo')
    list_filter = ('metodo',)
    raw_id_fields = ('animal',)


@admin.register(OcorrenciaSanitaria)
class OcorrenciaSanitariaAdmin(admin.ModelAdmin):
    list_display = ('animal', 'tipo', 'data_inicio', 'data_fim', 'resultado')
    list_filter = ('tipo', 'resultado')
    raw_id_fields = ('animal',)


@admin.register(Vacinacao)
class VacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data', 'vacina')
    raw_id_fields = ('animal',)


@admin.register(Desaleitamento)
class DesaleitamentoAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data', 'metodo', 'peso_kg', 'doenca_ativa')
    raw_id_fields = ('terneira',)
