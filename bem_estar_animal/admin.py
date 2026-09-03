from django.contrib import admin
from .models import (
    AmbienteBEA, ComportamentoBEA, VisitaPresencialBEA, 
    ConsentimentoBEA, EvidenciasBEA,
    JornadaProCampo, DietaSolidaBEA, PlanoAcaoBEA
)


@admin.register(AmbienteBEA)
class AmbienteBEAAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_avaliacao', 'tipo_alojamento', 'fase_alojamento', 'dimensao_baia_m2', 'profundidade_cama_cm')
    list_filter = ('data_avaliacao', 'tipo_alojamento', 'fase_alojamento', 'local_paricao', 'score_sujidade')
    search_fields = ('terneira__identificacao', 'terneira__nome')
    date_hierarchy = 'data_avaliacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('terneira', 'data_avaliacao', 'responsavel_avaliacao')
        }),
        ('Parição e Alojamento', {
            'fields': ('local_paricao', 'tipo_alojamento', 'fase_alojamento', 'dimensao_baia_m2', 'numero_animais_baia')
        }),
        ('Cama', {
            'fields': ('tipo_cama', 'profundidade_cama_cm', 'score_sujidade')
        }),
        ('Microclima', {
            'fields': ('tem_aquecimento', 'cortinas_adequadas', 'tem_sombra', 'tem_ventilacao')
        }),
        ('Higiene de Utensílios', {
            'fields': ('freq_lavagem_mamadeiras', 'freq_lavagem_sondas', 'freq_lavagem_bebedouros',
                      'freq_lavagem_baldes', 'freq_lavagem_cochos', 'freq_desinfeccao_baias',
                      'produto_higiene', 'tem_pop_elaborado', 'limpeza_acida_semanal')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(ComportamentoBEA)
class ComportamentoBEAAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_avaliacao', 'estimulo_6h', 'mocacao_realizada', 'idade_agrupamento_dias')
    list_filter = ('data_avaliacao', 'estimulo_6h', 'mocacao_realizada', 'tipo_agrupamento')
    search_fields = ('terneira__identificacao', 'terneira__nome')
    date_hierarchy = 'data_avaliacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('terneira', 'data_avaliacao', 'responsavel_avaliacao')
        }),
        ('Estímulo Tátil', {
            'fields': ('estimulo_6h', 'continuidade_diaria')
        }),
        ('Agrupamento e Enriquecimento', {
            'fields': ('idade_agrupamento_dias', 'tipo_agrupamento', 'tem_enriquecimento', 'tipo_enriquecimento')
        }),
        ('Mochação', {
            'fields': ('mocacao_realizada', 'mocacao_idade_semanas', 'mocacao_metodo')
        }),
        ('Protocolo de Mitigação de Dor', {
            'fields': ('protocolo_dor_anestesia', 'protocolo_dor_analgesia', 'protocolo_dor_sedacao')
        }),
        ('Tetas Supranumerárias', {
            'fields': ('remocao_tetas_realizada', 'protocolo_dor_tetas')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(VisitaPresencialBEA)
class VisitaPresencialBEAAdmin(admin.ModelAdmin):
    list_display = ('propriedade', 'data_visita', 'tipo_visita', 'numero_visita', 'responsavel_tecnico', 'jornada')
    list_filter = ('data_visita', 'tipo_visita', 'propriedade')
    search_fields = ('propriedade__nome', 'responsavel_tecnico__nome', 'produtor_visitado__nome')
    date_hierarchy = 'data_visita'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('propriedade', 'jornada', 'data_visita', 'tipo_visita', 'numero_visita')
        }),
        ('Participantes', {
            'fields': ('responsavel_tecnico', 'produtor_visitado')
        }),
        ('Conteúdo da Visita', {
            'fields': ('observacoes_gerais', 'problemas_identificados', 'acoes_recomendadas')
        }),
    )
    
    readonly_fields = ('criada_em',)


@admin.register(ConsentimentoBEA)
class ConsentimentoBEAAdmin(admin.ModelAdmin):
    list_display = ('propriedade', 'produtor', 'consentimento_dados', 'consentimento_imagem', 'data_consentimento')
    list_filter = ('consentimento_dados', 'consentimento_imagem', 'data_consentimento')
    search_fields = ('propriedade__nome', 'produtor__nome')
    date_hierarchy = 'data_consentimento'


@admin.register(EvidenciasBEA)
class EvidenciasBEAAdmin(admin.ModelAdmin):
    list_display = ('tipo_evidencia', 'objeto_vinculado_nome', 'data_upload', 'usuario_upload')
    list_filter = ('tipo_evidencia', 'data_upload')
    search_fields = ('descricao', 'usuario_upload__nome')
    date_hierarchy = 'data_upload'


@admin.register(JornadaProCampo)
class JornadaProCampoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'propriedade', 'supervisor', 'produtor', 'status', 'data_inicio', 'total_visitas', 'baseline_realizado')
    list_filter = ('status', 'baseline_realizado', 'case_sucesso_gerado', 'data_inicio')
    search_fields = ('nome', 'propriedade__nome', 'supervisor__nome', 'produtor__nome')
    date_hierarchy = 'data_inicio'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'propriedade')
        }),
        ('Participantes', {
            'fields': ('supervisor', 'produtor', 'consentimento')
        }),
        ('Cronograma', {
            'fields': ('data_selecao_produtor', 'data_inicio', 'data_prevista_conclusao', 'data_conclusao')
        }),
        ('Controle', {
            'fields': ('status', 'minimo_visitas', 'baseline_realizado', 'case_sucesso_gerado')
        }),
        ('Objetivos e Observações', {
            'fields': ('objetivo_principal', 'observacoes', 'motivo_cancelamento')
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(DietaSolidaBEA)
class DietaSolidaBEAAdmin(admin.ModelAdmin):
    list_display = ('terneira', 'data_avaliacao', 'inicio_oferta_agua', 'inicio_concentrado_dias', 'inicio_volumoso_dias')
    list_filter = ('data_avaliacao', 'tipo_bebedouro', 'agua_fresca_disponivel')
    search_fields = ('terneira__identificacao', 'terneira__nome')
    date_hierarchy = 'data_avaliacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('terneira', 'jornada', 'data_avaliacao', 'responsavel_avaliacao')
        }),
        ('Água', {
            'fields': ('inicio_oferta_agua', 'fonte_agua', 'tipo_bebedouro', 'agua_fresca_disponivel')
        }),
        ('Concentrado', {
            'fields': ('inicio_concentrado_dias', 'tipo_racao', 'freq_abastecimento_concentrado', 
                      'consumo_concentrado_estimado_kg')
        }),
        ('Volumoso', {
            'fields': ('inicio_volumoso_dias', 'tipo_volumoso', 'freq_abastecimento_volumoso', 
                      'consumo_volumoso_estimado_kg')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(PlanoAcaoBEA)
class PlanoAcaoBEAAdmin(admin.ModelAdmin):
    list_display = ('indicador', 'jornada', 'dominio', 'status', 'prioridade', 'prazo', 'responsavel')
    list_filter = ('status', 'prioridade', 'dominio', 'prazo')
    search_fields = ('indicador', 'situacao_encontrada', 'acao_recomendada', 'jornada__nome')
    date_hierarchy = 'prazo'
    
    fieldsets = (
        ('Vinculação', {
            'fields': ('jornada', 'visita_origem')
        }),
        ('Identificação do Problema', {
            'fields': ('dominio', 'indicador', 'situacao_encontrada')
        }),
        ('Ação', {
            'fields': ('acao_recomendada', 'responsavel', 'prazo', 'prioridade')
        }),
        ('Controle', {
            'fields': ('status', 'data_conclusao', 'resultado_obtido')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
