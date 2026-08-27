from django.db import models


CATEGORIA_PROTOCOLO_CHOICES = [
    ('colostragem', 'Colostragem'),
    ('umbigo', 'Cura de umbigo'),
    ('alimentacao', 'Alimentação'),
    ('vacinacao', 'Vacinação'),
    ('desaleitamento', 'Desaleitamento'),
    ('pre_parto', 'Pré-parto'),
    ('sanitario', 'Sanitário / Tratamentos'),
    ('reproducao', 'Reprodução'),
    ('geral', 'Geral'),
]

RACA_CHOICES = [
    ('holandes', 'Holandês'),
    ('jersey', 'Jersey'),
    ('girolando', 'Girolando'),
    ('gir_leiteiro', 'Gir Leiteiro'),
    ('guzera', 'Guzerá'),
    ('pardo_suico', 'Pardo Suíço'),
    ('mestaca', 'Mestiça'),
    ('todas', 'Todas as raças'),
]


class Protocolo(models.Model):
    """Como a propriedade pretende executar determinada atividade. Versionado."""

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='protocolos', verbose_name='Propriedade',
    )
    nome = models.CharField('Nome', max_length=200)
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIA_PROTOCOLO_CHOICES)
    descricao = models.TextField('Descrição')
    versao = models.PositiveSmallIntegerField('Versão', default=1)
    vigencia_inicio = models.DateField('Vigência inicial')
    vigencia_fim = models.DateField('Vigência final', null=True, blank=True,
                                    help_text='Deixe em branco para protocolo vigente')
    criado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Criado por',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Protocolo'
        verbose_name_plural = 'Protocolos'
        ordering = ['nome', '-versao']

    def __str__(self):
        status = 'Vigente' if not self.vigencia_fim else 'Encerrado'
        return f'{self.nome} v{self.versao} ({status})'

    @property
    def vigente(self):
        return self.vigencia_fim is None


class MetaDesenvolvimento(models.Model):
    """
    Curva de peso-alvo por raça e idade.
    Define os pontos de referência para avaliar o crescimento da terneira.
    """

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='metas_desenvolvimento',
    )
    nome = models.CharField('Nome da curva', max_length=200,
                             help_text='Ex: Meta Holandês — Embrapa')
    raca = models.CharField('Raça', max_length=30, choices=RACA_CHOICES)
    fonte = models.CharField('Fonte', max_length=200, blank=True,
                              help_text='Ex: Embrapa, Protocolo interno, NRC 2001')
    vigencia_inicio = models.DateField('Vigência inicial')
    vigencia_fim = models.DateField('Vigência final', null=True, blank=True)
    ativa = models.BooleanField('Ativa', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Meta de desenvolvimento'
        verbose_name_plural = 'Metas de desenvolvimento'

    def __str__(self):
        return f'{self.nome} ({self.get_raca_display()})'


class PontoMetaDesenvolvimento(models.Model):
    """Ponto específico na curva de desenvolvimento: idade → peso esperado."""

    TIPO_CHOICES = [
        ('peso', 'Peso (kg)'),
        ('altura', 'Altura na garupa (cm)'),
        ('perimetro', 'Perímetro torácico (cm)'),
    ]

    meta = models.ForeignKey(
        MetaDesenvolvimento, on_delete=models.CASCADE,
        related_name='pontos', verbose_name='Meta',
    )
    tipo = models.CharField('Tipo de medida', max_length=20, choices=TIPO_CHOICES, default='peso')
    idade_dias = models.PositiveSmallIntegerField('Idade (dias)')
    valor_minimo = models.DecimalField('Valor mínimo', max_digits=6, decimal_places=2)
    valor_ideal = models.DecimalField('Valor ideal', max_digits=6, decimal_places=2)
    valor_maximo = models.DecimalField('Valor máximo', max_digits=6, decimal_places=2,
                                        null=True, blank=True)
    observacoes = models.CharField('Observações', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Ponto de meta'
        verbose_name_plural = 'Pontos de meta'
        ordering = ['meta', 'tipo', 'idade_dias']
        unique_together = ('meta', 'tipo', 'idade_dias')

    def __str__(self):
        return f'{self.meta} — {self.get_tipo_display()} aos {self.idade_dias}d: {self.valor_ideal}'


class MetaReprodutiva(models.Model):
    """Define os critérios de peso e desenvolvimento para entrada no programa reprodutivo."""

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='metas_reprodutivas',
    )
    nome = models.CharField('Nome', max_length=200)
    raca = models.CharField('Raça', max_length=30, choices=RACA_CHOICES)
    peso_adulto_medio_kg = models.DecimalField(
        'Peso adulto médio do rebanho (kg)', max_digits=6, decimal_places=1,
        null=True, blank=True,
    )
    percentual_peso_adulto = models.DecimalField(
        'Percentual do peso adulto (%)', max_digits=4, decimal_places=1,
        default=55.0, help_text='Embrapa recomenda 50–55%',
    )
    peso_minimo_kg = models.DecimalField(
        'Peso mínimo para IA (kg)', max_digits=6, decimal_places=1,
        null=True, blank=True,
        help_text='Referência: Holandês 330–340kg, Jersey 230–240kg',
    )
    ecc_minimo = models.DecimalField('ECC mínimo', max_digits=3, decimal_places=1,
                                      null=True, blank=True)
    idade_minima_meses = models.PositiveSmallIntegerField('Idade mínima (meses)', null=True, blank=True)
    idade_alvo_meses = models.PositiveSmallIntegerField(
        'Idade alvo para primeira IA (meses)', default=13,
    )
    gmd_minimo_recria = models.DecimalField(
        'GMD mínimo na recria (kg/dia)', max_digits=4, decimal_places=3,
        null=True, blank=True,
    )
    vigencia_inicio = models.DateField('Vigência inicial')
    vigencia_fim = models.DateField('Vigência final', null=True, blank=True)
    ativa = models.BooleanField('Ativa', default=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Meta reprodutiva'
        verbose_name_plural = 'Metas reprodutivas'

    def __str__(self):
        return f'{self.nome} ({self.get_raca_display()})'

    @property
    def peso_alvo_calculado(self):
        if self.peso_adulto_medio_kg and self.percentual_peso_adulto:
            return round(float(self.peso_adulto_medio_kg) * float(self.percentual_peso_adulto) / 100, 1)
        return self.peso_minimo_kg


class ReferencialTecnico(models.Model):
    """Recomendação da literatura científica para um indicador."""

    INDICADOR_CHOICES = [
        ('dias_secos', 'Dias secos'),
        ('dias_pre_parto', 'Dias no pré-parto'),
        ('tempo_colostragem', 'Tempo até primeira colostragem (h)'),
        ('volume_colostro', 'Volume de colostro (ml/kg PV)'),
        ('brix_colostro', 'Brix do colostro (%)'),
        ('gmd_aleitamento', 'GMD no aleitamento (kg/dia)'),
        ('gmd_recria', 'GMD na recria (kg/dia)'),
        ('peso_60d', 'Peso aos 60 dias (kg)'),
        ('peso_180d', 'Peso aos 180 dias (kg)'),
        ('idade_desaleitamento', 'Idade ao desaleitamento (dias)'),
        ('mortalidade_60d', 'Mortalidade até 60 dias (%)'),
        ('incidencia_diarreia', 'Incidência de diarreia (%)'),
        ('incidencia_pneumonia', 'Incidência de pneumonia (%)'),
        ('outro', 'Outro'),
    ]

    indicador = models.CharField('Indicador', max_length=50, choices=INDICADOR_CHOICES)
    descricao = models.CharField('Descrição do indicador', max_length=200)
    valor_minimo = models.DecimalField('Valor mínimo', max_digits=8, decimal_places=3, null=True, blank=True)
    valor_ideal = models.DecimalField('Valor ideal/recomendado', max_digits=8, decimal_places=3, null=True, blank=True)
    valor_maximo = models.DecimalField('Valor máximo', max_digits=8, decimal_places=3, null=True, blank=True)
    unidade = models.CharField('Unidade', max_length=50)
    populacao = models.CharField('População à qual se aplica', max_length=200)
    fonte = models.CharField('Fonte', max_length=200)
    autor = models.CharField('Autor(es)', max_length=300, blank=True)
    ano = models.PositiveSmallIntegerField('Ano', null=True, blank=True)
    observacoes = models.TextField('Observações e limitações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Referencial técnico'
        verbose_name_plural = 'Referenciais técnicos'
        ordering = ['indicador', '-ano']

    def __str__(self):
        return f'{self.get_indicador_display()} — {self.fonte} ({self.ano})'


# ---------------------------------------------------------------------------
# CRITÉRIOS DE CONFORMIDADE
# ---------------------------------------------------------------------------

CODIGO_CRITERIO_CHOICES = [
    # Colostragem
    ('colostragem_tempo',            'Colostragem — tempo até 1ª mamada (horas)'),
    ('colostragem_volume_relativo',  'Colostragem — volume relativo ao peso (% PV)'),
    ('colostragem_brix',             'Colostragem — qualidade Brix (%)'),
    # Umbigo
    ('umbigo_tempo',                 'Umbigo — tempo até 1ª cura (horas)'),
    # Pré-parto / secagem
    ('dias_secos_minimo',            'Dias secos — mínimo'),
    ('dias_secos_maximo',            'Dias secos — máximo'),
    ('dias_pre_parto_minimo',        'Pré-parto — dias mínimos no lote'),
    # Crescimento (delega para MetaDesenvolvimento — usado como fallback)
    ('peso_por_idade',               'Crescimento — peso mínimo por idade'),
    # Desaleitamento
    ('desaleitamento_idade_minima',  'Desaleitamento — idade mínima (dias)'),
    ('desaleitamento_idade_maxima',  'Desaleitamento — idade máxima (dias)'),
    ('desaleitamento_peso_minimo',   'Desaleitamento — peso mínimo (kg)'),
    # IA
    ('ia_peso_minimo',               'IA — peso mínimo na cobertura (kg)'),
]


class CriterioConformidade(models.Model):
    """
    Regra mensurável e executável definida pela propriedade.
    Diferente de Protocolo (documento descritivo) e MetaDesenvolvimento (curva de crescimento).
    Tem código padronizado para que o sistema saiba qual avaliador chamar.
    """

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='criterios_conformidade', verbose_name='Propriedade',
    )
    codigo = models.CharField(
        'Código do critério', max_length=50, choices=CODIGO_CRITERIO_CHOICES,
    )
    descricao_custom = models.CharField(
        'Descrição personalizada', max_length=200, blank=True,
        help_text='Deixe em branco para usar a descrição padrão',
    )
    valor_limite = models.DecimalField(
        'Valor limite', max_digits=8, decimal_places=3,
        help_text='Valor numérico do critério (ex: 2 para "até 2 horas")',
    )
    unidade = models.CharField('Unidade', max_length=30)
    escopo_raca = models.CharField(
        'Escopo — raça', max_length=30, choices=RACA_CHOICES,
        default='todas', help_text='Aplicar apenas a esta raça, ou Todas',
    )
    vigencia_inicio = models.DateField('Vigência inicial')
    vigencia_fim = models.DateField(
        'Vigência final', null=True, blank=True,
        help_text='Deixe em branco para critério vigente',
    )
    referencial_base = models.ForeignKey(
        ReferencialTecnico, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Referencial técnico base',
        help_text='Referência bibliográfica que embasou este critério (opcional)',
    )
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Critério de conformidade'
        verbose_name_plural = 'Critérios de conformidade'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.get_codigo_display()} — {self.valor_limite} {self.unidade}'

    @property
    def descricao(self):
        return self.descricao_custom or self.get_codigo_display()

    @property
    def vigente(self):
        return self.vigencia_fim is None
