from django.db import models


RESULTADO_CHOICES = [
    ('conforme',       'Conforme'),
    ('nao_conforme',   'Não conforme'),
    ('dado_ausente',   'Dado ausente'),
    ('nao_aplicavel',  'Não aplicável'),
]


class ResultadoConformidade(models.Model):
    """
    Resultado da avaliação de um evento específico contra um CriterioConformidade.

    Regras fundamentais:
    - Imutável após criação. Nunca editar — se houver correção, criar novo resultado.
    - 'dado_ausente' é um resultado válido, não um erro. Indica que os dados
      necessários para avaliar não estavam disponíveis no momento do evento.
    - Armazenado (não recalculado) porque o critério pode mudar. O resultado
      histórico deve refletir o critério vigente no momento do evento.
    """

    animal = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='resultados_conformidade', verbose_name='Animal',
    )
    criterio = models.ForeignKey(
        'config_tecnica.CriterioConformidade', on_delete=models.CASCADE,
        related_name='resultados', verbose_name='Critério',
        null=True, blank=True,
        help_text='Null apenas para conformidade de peso_por_idade (usa MetaDesenvolvimento)',
    )
    meta_desenvolvimento = models.ForeignKey(
        'config_tecnica.MetaDesenvolvimento', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Meta de desenvolvimento',
        help_text='Usado apenas para conformidade de peso por idade',
    )

    # Contexto do evento avaliado
    data_evento = models.DateField('Data do evento')
    evento_tipo = models.CharField(
        'Tipo do evento', max_length=50,
        help_text='Nome do model avaliado: Parto, Colostragem, CuraUmbigo, Pesagem, Desaleitamento',
    )
    evento_id = models.PositiveIntegerField('ID do evento')

    # Valores
    valor_observado = models.DecimalField(
        'Valor observado', max_digits=10, decimal_places=3,
        null=True, blank=True,
        help_text='Null quando resultado = dado_ausente',
    )
    valor_referencia = models.DecimalField(
        'Valor de referência (limite)', max_digits=10, decimal_places=3,
        null=True, blank=True,
    )
    desvio = models.DecimalField(
        'Desvio (observado − referência)', max_digits=10, decimal_places=3,
        null=True, blank=True,
        help_text='Positivo = acima do limite, negativo = abaixo',
    )

    # Resultado
    resultado = models.CharField('Resultado', max_length=20, choices=RESULTADO_CHOICES)
    motivo_ausencia = models.CharField(
        'Motivo do dado ausente', max_length=200, blank=True,
        help_text='Explica por que o dado não estava disponível',
    )

    # Auditoria
    calculado_em = models.DateTimeField('Calculado em', auto_now_add=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Resultado de conformidade'
        verbose_name_plural = 'Resultados de conformidade'
        ordering = ['-data_evento', 'animal']
        indexes = [
            models.Index(fields=['animal', 'data_evento']),
            models.Index(fields=['criterio', 'resultado']),
            models.Index(fields=['evento_tipo', 'evento_id']),
        ]

    def __str__(self):
        criterio_str = str(self.criterio) if self.criterio else 'Peso por idade'
        return f'{self.animal} | {criterio_str} | {self.get_resultado_display()} | {self.data_evento}'

    @property
    def conforme(self):
        return self.resultado == 'conforme'

    @property
    def tem_dado(self):
        return self.resultado != 'dado_ausente'
