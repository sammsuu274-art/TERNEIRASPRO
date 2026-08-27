from django.db import models
from django.utils import timezone


STATUS_TRAJETORIA_CHOICES = [
    ('favoravel', 'Favorável'),
    ('atencao', 'Atenção'),
    ('desfavoravel', 'Desfavorável'),
    ('insuficiente', 'Dados insuficientes'),
]

STATUS_CHECKPOINT_CHOICES = [
    ('adequado', 'Adequado'),
    ('atencao', 'Atenção'),
    ('critico', 'Crítico'),
    ('pendente', 'Pendente de avaliação'),
]


class ProgramaAcompanhamento(models.Model):
    """Janela formal de monitoramento do animal — padrão 180 dias."""

    STATUS_CHOICES = [
        ('em_andamento', 'Em andamento'),
        ('encerrado', 'Encerrado'),
        ('cancelado', 'Cancelado'),
    ]

    terneira = models.OneToOneField(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='programa_acompanhamento', verbose_name='Terneira',
    )
    data_inicio = models.DateField('Data de início', help_text='Geralmente a data de nascimento')
    duracao_dias = models.PositiveSmallIntegerField('Duração (dias)', default=180)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Programa de acompanhamento'
        verbose_name_plural = 'Programas de acompanhamento'

    def __str__(self):
        return f'Programa {self.terneira} — {self.status}'

    @property
    def data_encerramento_prevista(self):
        from datetime import timedelta
        return self.data_inicio + timedelta(days=self.duracao_dias)

    @property
    def dias_decorridos(self):
        hoje = timezone.now().date()
        return (hoje - self.data_inicio).days

    @property
    def percentual_concluido(self):
        return min(round(self.dias_decorridos / self.duracao_dias * 100), 100)

    @property
    def checkpoint_pendente(self):
        """Checkpoint está no prazo se o animal tem entre 165 e 195 dias."""
        d = self.dias_decorridos
        return 165 <= d <= 195 and not hasattr(self, 'checkpoint')


class CheckpointSesMeses(models.Model):
    """
    Avaliação consolidada ao final dos 6 meses.
    Armazena o resultado; os indicadores são calculados na geração.
    """

    programa = models.OneToOneField(
        ProgramaAcompanhamento, on_delete=models.CASCADE,
        related_name='checkpoint', verbose_name='Programa',
    )
    data_avaliacao = models.DateField('Data da avaliação')
    idade_dias = models.PositiveSmallIntegerField('Idade na avaliação (dias)')

    # Crescimento
    peso_kg = models.DecimalField('Peso (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    peso_meta_kg = models.DecimalField('Peso meta (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    percentual_meta = models.DecimalField('% da meta atingida', max_digits=5, decimal_places=1, null=True, blank=True)
    gmd_total = models.DecimalField('GMD total (kg/dia)', max_digits=5, decimal_places=3, null=True, blank=True)
    gmd_30_dias = models.DecimalField('GMD últimos 30d (kg/dia)', max_digits=5, decimal_places=3, null=True, blank=True)

    # Desenvolvimento corporal
    altura_cm = models.DecimalField('Altura (cm)', max_digits=5, decimal_places=1, null=True, blank=True)
    perimetro_toracico_cm = models.DecimalField('Perímetro torácico (cm)', max_digits=5, decimal_places=1, null=True, blank=True)
    ecc = models.DecimalField('ECC', max_digits=3, decimal_places=1, null=True, blank=True)

    # Sanitário (calculado no momento da geração — não desnormalizado)
    diarreia_ocorrencias = models.PositiveSmallIntegerField('Episódios de diarreia', default=0)
    pneumonia_ocorrencias = models.PositiveSmallIntegerField('Episódios de pneumonia', default=0)
    onfalite_ocorrencias = models.PositiveSmallIntegerField('Episódios de onfalite', default=0)
    total_tratamentos = models.PositiveSmallIntegerField('Total de tratamentos', default=0)
    doenca_ativa = models.BooleanField('Doença ativa?', default=False)

    # Alimentação
    desaleitada = models.BooleanField('Desaleitada?', default=False)
    consumo_concentrado_adequado = models.BooleanField('Consumo de concentrado adequado?', null=True, blank=True)

    # Classificação
    status_checkpoint = models.CharField(
        'Status', max_length=20, choices=STATUS_CHECKPOINT_CHOICES, default='pendente',
    )
    crescimento_estrutural = models.CharField(
        'Crescimento estrutural', max_length=20,
        choices=[('adequado', 'Adequado'), ('atencao', 'Atenção'), ('insuficiente', 'Insuficiente')],
        blank=True,
    )

    # Trajetória projetada
    status_trajetoria = models.CharField(
        'Trajetória', max_length=20, choices=STATUS_TRAJETORIA_CHOICES, default='insuficiente',
    )
    indicadores_trajetoria = models.TextField(
        'Indicadores que fundamentam a trajetória', blank=True,
    )

    # Observações do técnico
    observacoes = models.TextField('Observações técnicas', blank=True)
    recomendacoes = models.TextField('Recomendações de manejo', blank=True)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Checkpoint de 6 meses'
        verbose_name_plural = 'Checkpoints de 6 meses'

    def __str__(self):
        return f'Checkpoint {self.programa.terneira} em {self.data_avaliacao}'


class ProjecaoReprodutiva(models.Model):
    """
    Projeção de quando a terneira atingirá os critérios para a primeira IA.
    Recalculada a cada nova pesagem.
    """

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='projecoes_reprodutivas', verbose_name='Terneira',
    )
    meta_reprodutiva = models.ForeignKey(
        'config_tecnica.MetaReprodutiva', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Meta reprodutiva usada',
    )
    data_calculo = models.DateField('Data do cálculo')
    peso_atual_kg = models.DecimalField('Peso atual (kg)', max_digits=5, decimal_places=2)
    peso_alvo_kg = models.DecimalField('Peso alvo (kg)', max_digits=5, decimal_places=2)
    gmd_projetado = models.DecimalField('GMD projetado (kg/dia)', max_digits=5, decimal_places=3)
    dias_ate_peso_alvo = models.IntegerField('Dias até o peso alvo', null=True, blank=True)
    data_estimada = models.DateField('Data estimada para IA', null=True, blank=True)
    idade_estimada_meses = models.DecimalField(
        'Idade estimada (meses)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    status_trajetoria = models.CharField(
        'Trajetória', max_length=20, choices=STATUS_TRAJETORIA_CHOICES,
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Projeção reprodutiva'
        verbose_name_plural = 'Projeções reprodutivas'
        ordering = ['-data_calculo']

    def __str__(self):
        return f'Projeção {self.terneira} em {self.data_calculo} — {self.get_status_trajetoria_display()}'


class CoberturaIA(models.Model):
    """Registro da primeira inseminação/cobertura — encerra o escopo do sistema para o animal."""

    TIPO_CHOICES = [
        ('iatf', 'IATF'),
        ('ia_tempo_fixo', 'IA em tempo fixo'),
        ('ia_cio', 'IA no cio'),
        ('monta_natural', 'Monta natural'),
    ]

    RESULTADO_CHOICES = [
        ('prenhe', 'Prenhe'),
        ('vazia', 'Vazia'),
        ('aguardando', 'Aguardando diagnóstico'),
    ]

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='coberturas_ia', verbose_name='Animal',
    )
    data = models.DateField('Data')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    touro_semen = models.CharField('Touro/Sêmen', max_length=200, blank=True)
    peso_na_ia_kg = models.DecimalField('Peso na IA (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    ecc_na_ia = models.DecimalField('ECC na IA', max_digits=3, decimal_places=1, null=True, blank=True)
    numero_servico = models.PositiveSmallIntegerField('Número do serviço', default=1)
    resultado = models.CharField('Resultado', max_length=20, choices=RESULTADO_CHOICES, default='aguardando')
    data_diagnostico = models.DateField('Data do diagnóstico', null=True, blank=True)
    data_prevista_parto = models.DateField('Data prevista do parto', null=True, blank=True)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cobertura / IA'
        verbose_name_plural = 'Coberturas / IA'
        ordering = ['-data']

    def __str__(self):
        return f'IA {self.terneira} em {self.data} — {self.get_resultado_display()}'
