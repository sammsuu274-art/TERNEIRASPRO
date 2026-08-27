from django.db import models
from django.utils import timezone


METODO_FORNECIMENTO_CHOICES = [
    ('mamada_direta', 'Mamada direta'),
    ('mamadeira', 'Mamadeira'),
    ('sonda', 'Sonda esofágica'),
    ('balde', 'Balde'),
]

ORIGEM_COLOSTRO_CHOICES = [
    ('mae', 'Mãe biológica'),
    ('banco', 'Banco de colostro'),
    ('sucedaneo', 'Sucedâneo de colostro'),
    ('outra_vaca', 'Outra vaca da propriedade'),
]

TIPO_OCORRENCIA_CHOICES = [
    ('diarreia', 'Diarreia'),
    ('pneumonia', 'Pneumonia'),
    ('onfalite', 'Onfalite'),
    ('febre', 'Febre'),
    ('desidratacao', 'Desidratação'),
    ('claudicacao', 'Claudicação'),
    ('lesao', 'Lesão'),
    ('outro', 'Outro'),
]

RESULTADO_CHOICES = [
    ('cura', 'Cura'),
    ('melhora', 'Melhora parcial'),
    ('sem_resposta', 'Sem resposta ao tratamento'),
    ('obito', 'Óbito'),
    ('cronico', 'Crônico'),
]

METODO_PESAGEM_CHOICES = [
    ('balanca_digital', 'Balança digital'),
    ('balanca_mecanica', 'Balança mecânica'),
    ('fita_toracica', 'Fita torácica (estimativa)'),
    ('estimativa_visual', 'Estimativa visual'),
]


class Parto(models.Model):
    FACILIDADE_CHOICES = [
        (0, '0 — Parto normal sem assistência'),
        (1, '1 — Pequena assistência'),
        (2, '2 — Tração ou intervenção moderada'),
        (3, '3 — Cesariana ou emergência'),
    ]
    VITALIDADE_CHOICES = [
        ('normal', 'Normal — ativo e em pé rapidamente'),
        ('lento', 'Lento — demorou a levantar'),
        ('fraco', 'Fraco — precisou de assistência para levantar'),
        ('sem_vida', 'Natimorto'),
    ]

    ciclo = models.OneToOneField(
        'animais.CicloReprodutivo', on_delete=models.CASCADE,
        related_name='parto', verbose_name='Ciclo reprodutivo',
    )
    terneira = models.OneToOneField(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='parto_origem', verbose_name='Animal nascido',
    )
    data_parto = models.DateField('Data do parto')
    hora_parto = models.TimeField('Hora do parto', null=True, blank=True)
    facilidade = models.IntegerField('Facilidade do parto', choices=FACILIDADE_CHOICES, default=0)
    assistencia = models.BooleanField('Houve assistência?', default=False)
    gemelar = models.BooleanField('Parto gemelar?', default=False)
    peso_nascimento = models.DecimalField(
        'Peso ao nascer (kg)', max_digits=5, decimal_places=2,
        null=True, blank=True, help_text='Deixe em branco se não foi pesado',
    )
    vitalidade = models.CharField('Vitalidade', max_length=20, choices=VITALIDADE_CHOICES, default='normal')
    tempo_levantar_min = models.PositiveIntegerField(
        'Tempo para levantar (min)', null=True, blank=True,
    )
    lesoes_anormalidades = models.TextField('Lesões ou anormalidades', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    registrado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Registrado por',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    evento_em = models.DateTimeField('Data/hora real do evento', null=True, blank=True)

    class Meta:
        verbose_name = 'Parto'
        verbose_name_plural = 'Partos'
        ordering = ['-data_parto']

    def __str__(self):
        return f'Parto de {self.ciclo.vaca} em {self.data_parto}'

    @property
    def hora_nascimento_completa(self):
        if self.data_parto and self.hora_parto:
            from datetime import datetime
            return datetime.combine(self.data_parto, self.hora_parto)
        return None


class BancoColostro(models.Model):
    """Estoque de colostro da propriedade — disponível para uso nas terneiras."""
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('utilizado', 'Utilizado'),
        ('descartado', 'Descartado'),
    ]

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='banco_colostro', verbose_name='Propriedade',
    )
    data_coleta = models.DateField('Data de coleta')
    vaca_origem = models.ForeignKey(
        'animais.Animal', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Vaca de origem',
    )
    brix = models.DecimalField('Brix (%)', max_digits=4, decimal_places=1, null=True, blank=True)
    volume_ml = models.PositiveIntegerField('Volume (ml)')
    congelado = models.BooleanField('Congelado?', default=False)
    data_congelamento = models.DateField('Data de congelamento', null=True, blank=True)
    lote = models.CharField('Lote/Identificação', max_length=50, blank=True)
    validade = models.DateField('Validade', null=True, blank=True)
    local_armazenamento = models.CharField('Local de armazenamento', max_length=100, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='disponivel')
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Banco de colostro'
        verbose_name_plural = 'Banco de colostro'
        ordering = ['-data_coleta']

    def __str__(self):
        return f'Colostro {self.lote or self.pk} — {self.volume_ml}ml — {self.get_status_display()}'


class Colostragem(models.Model):
    """Cada fornecimento de colostro é um registro independente."""

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='colostragens', verbose_name='Terneira',
    )
    data_hora = models.DateTimeField('Data e hora do fornecimento')
    volume_ml = models.PositiveIntegerField('Volume fornecido (ml)')
    origem = models.CharField('Origem', max_length=20, choices=ORIGEM_COLOSTRO_CHOICES)
    banco_colostro = models.ForeignKey(
        BancoColostro, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Lote do banco',
    )
    metodo = models.CharField('Método', max_length=20, choices=METODO_FORNECIMENTO_CHOICES)
    brix = models.DecimalField('Brix (%)', max_digits=4, decimal_places=1, null=True, blank=True)
    temperatura_c = models.DecimalField(
        'Temperatura (°C)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    ingestao_confirmada = models.BooleanField('Ingestão confirmada?', default=True)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Colostragem'
        verbose_name_plural = 'Colostragens'
        ordering = ['terneira', 'data_hora']

    def __str__(self):
        return f'Colostragem {self.terneira} em {self.data_hora}'

    @property
    def tempo_apos_nascimento_horas(self):
        """Calcula horas entre o nascimento e este fornecimento."""
        try:
            hora_nasc = self.terneira.parto_origem.hora_nascimento_completa
            if hora_nasc:
                from django.utils import timezone
                delta = self.data_hora - timezone.make_aware(hora_nasc)
                return round(delta.total_seconds() / 3600, 2)
        except Exception:
            pass
        return None


class CuraUmbigo(models.Model):
    """Registro de aplicação de produto no umbigo."""

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='curas_umbigo', verbose_name='Terneira',
    )
    data_hora = models.DateTimeField('Data e hora')
    produto = models.CharField('Produto utilizado', max_length=100)
    concentracao = models.CharField('Concentração', max_length=50, blank=True)
    metodo_aplicacao = models.CharField(
        'Método', max_length=50, blank=True,
        help_text='Ex: imersão, aspersão, pincel',
    )
    # Avaliação do umbigo neste momento
    coto_seco = models.BooleanField('Coto seco?', null=True, blank=True)
    inchaço = models.BooleanField('Inchaço?', default=False)
    secrecao = models.BooleanField('Secreção?', default=False)
    odor = models.BooleanField('Odor?', default=False)
    sangramento = models.BooleanField('Sangramento?', default=False)
    dor_palpacao = models.BooleanField('Dor à palpação?', default=False)
    suspeita_onfalite = models.BooleanField('Suspeita de onfalite?', default=False)
    foto = models.ImageField('Foto', upload_to='umbigo/', null=True, blank=True)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cura de umbigo'
        verbose_name_plural = 'Curas de umbigo'
        ordering = ['terneira', 'data_hora']

    def __str__(self):
        return f'Umbigo {self.terneira} em {self.data_hora}'


class Pesagem(models.Model):
    """Medição de peso e desenvolvimento corporal."""

    animal = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='pesagens', verbose_name='Animal',
    )
    data = models.DateField('Data da pesagem')
    peso_kg = models.DecimalField('Peso (kg)', max_digits=6, decimal_places=2)
    altura_garupa_cm = models.DecimalField(
        'Altura na garupa (cm)', max_digits=5, decimal_places=1,
        null=True, blank=True,
    )
    perimetro_toracico_cm = models.DecimalField(
        'Perímetro torácico (cm)', max_digits=5, decimal_places=1,
        null=True, blank=True,
    )
    ecc = models.DecimalField(
        'Escore de Condição Corporal', max_digits=3, decimal_places=1,
        null=True, blank=True, help_text='Escala 1,0 a 5,0',
    )
    metodo = models.CharField('Método', max_length=30, choices=METODO_PESAGEM_CHOICES, default='balanca_digital')
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    evento_em = models.DateTimeField('Data/hora real', null=True, blank=True)

    class Meta:
        verbose_name = 'Pesagem'
        verbose_name_plural = 'Pesagens'
        ordering = ['animal', 'data']

    def __str__(self):
        return f'{self.animal} — {self.peso_kg}kg em {self.data}'

    @property
    def idade_na_pesagem(self):
        if self.animal.data_nascimento:
            return (self.data - self.animal.data_nascimento).days
        return None


class OcorrenciaSanitaria(models.Model):
    """Problema de saúde com início, tratamento e desfecho."""

    animal = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='ocorrencias_sanitarias', verbose_name='Animal',
    )
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_OCORRENCIA_CHOICES)
    data_inicio = models.DateField('Data de início')
    temperatura_retal = models.DecimalField(
        'Temperatura retal (°C)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    sinais_clinicos = models.TextField('Sinais clínicos', blank=True)
    diagnostico = models.CharField('Diagnóstico', max_length=200, blank=True)
    conduta = models.TextField('Conduta adotada', blank=True)
    medicamento = models.CharField('Medicamento', max_length=200, blank=True)
    dose = models.CharField('Dose', max_length=100, blank=True)
    via_administracao = models.CharField('Via de administração', max_length=50, blank=True)
    duracao_tratamento_dias = models.PositiveSmallIntegerField(
        'Duração do tratamento (dias)', null=True, blank=True,
    )
    data_fim = models.DateField('Data de resolução', null=True, blank=True)
    resultado = models.CharField('Resultado', max_length=20, choices=RESULTADO_CHOICES, blank=True)
    recorrencia = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Recorrência de',
    )
    responsavel_tecnico = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável técnico',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ocorrência sanitária'
        verbose_name_plural = 'Ocorrências sanitárias'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.animal} — {self.get_tipo_display()} em {self.data_inicio}'

    @property
    def duracao_dias(self):
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days
        return None

    @property
    def ativa(self):
        return self.data_fim is None


class Vacinacao(models.Model):
    """Registro de vacinação."""

    animal = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='vacinacoes', verbose_name='Animal',
    )
    data = models.DateField('Data')
    vacina = models.CharField('Vacina', max_length=200)
    fabricante = models.CharField('Fabricante', max_length=100, blank=True)
    lote_produto = models.CharField('Lote do produto', max_length=50, blank=True)
    dose = models.CharField('Dose', max_length=50, blank=True)
    via = models.CharField('Via de aplicação', max_length=50, blank=True)
    protocolo = models.ForeignKey(
        'config_tecnica.Protocolo', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Protocolo',
    )
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vacinação'
        verbose_name_plural = 'Vacinações'
        ordering = ['-data']

    def __str__(self):
        return f'{self.animal} — {self.vacina} em {self.data}'


class ProtocoloAlimentar(models.Model):
    """Regime alimentar vigente para a terneira em determinado período."""

    TIPO_ALIMENTO_CHOICES = [
        ('leite_integral', 'Leite integral'),
        ('sucedaneo', 'Sucedâneo'),
        ('misto', 'Misto (leite + sucedâneo)'),
        ('solido', 'Sólido exclusivo (pós-desaleitamento)'),
    ]

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='protocolos_alimentares', verbose_name='Terneira',
    )
    data_inicio = models.DateField('Data de início')
    data_fim = models.DateField('Data de fim', null=True, blank=True)
    tipo_alimento = models.CharField('Tipo de alimento', max_length=30, choices=TIPO_ALIMENTO_CHOICES)
    volume_dia_litros = models.DecimalField(
        'Volume diário (L)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    fornecimentos_dia = models.PositiveSmallIntegerField('Fornecimentos/dia', default=2)
    concentrado = models.CharField('Concentrado', max_length=200, blank=True)
    concentrado_proteina = models.DecimalField(
        'PB do concentrado (%)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    feno = models.BooleanField('Oferece feno?', default=False)
    agua_livre = models.BooleanField('Água à vontade?', default=True)
    protocolo = models.ForeignKey(
        'config_tecnica.Protocolo', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Protocolo base',
    )
    observacoes = models.TextField('Observações', blank=True)
    registrado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Registrado por',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Protocolo alimentar'
        verbose_name_plural = 'Protocolos alimentares'
        ordering = ['terneira', '-data_inicio']

    def __str__(self):
        return f'{self.terneira} — {self.get_tipo_alimento_display()} a partir de {self.data_inicio}'


class RegistroAlimentacaoDiario(models.Model):
    """Registro diário do que foi fornecido (opcional, para propriedades com controle detalhado)."""

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='registros_alimentacao', verbose_name='Terneira',
    )
    data = models.DateField('Data')
    volume_leite_ml = models.PositiveIntegerField('Volume de leite/sucedâneo (ml)', null=True, blank=True)
    concentrado_ofertado_g = models.PositiveIntegerField('Concentrado ofertado (g)', null=True, blank=True)
    concentrado_recusado_g = models.PositiveIntegerField('Concentrado recusado (g)', null=True, blank=True)
    recusa_liquido = models.BooleanField('Recusou dieta líquida?', default=False)
    diarreia_apos = models.BooleanField('Diarreia após alimentação?', default=False)
    observacoes = models.TextField('Observações', blank=True)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro diário de alimentação'
        verbose_name_plural = 'Registros diários de alimentação'
        ordering = ['-data']
        unique_together = ('terneira', 'data')

    @property
    def consumo_concentrado_g(self):
        if self.concentrado_ofertado_g is not None and self.concentrado_recusado_g is not None:
            return self.concentrado_ofertado_g - self.concentrado_recusado_g
        return None


class Desaleitamento(models.Model):
    """Evento de encerramento do aleitamento."""

    METODO_CHOICES = [
        ('abrupto', 'Abrupto'),
        ('gradual', 'Gradual (redução progressiva)'),
        ('step_down', 'Step-down (redução por etapas)'),
    ]

    terneira = models.OneToOneField(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='desaleitamento', verbose_name='Terneira',
    )
    data = models.DateField('Data do desaleitamento')
    metodo = models.CharField('Método', max_length=20, choices=METODO_CHOICES)
    peso_kg = models.DecimalField(
        'Peso no desaleitamento (kg)', max_digits=5, decimal_places=2,
        null=True, blank=True,
    )
    consumo_concentrado_adequado = models.BooleanField(
        'Consumo de concentrado adequado?', null=True, blank=True,
    )
    doenca_ativa = models.BooleanField('Doença ativa no momento?', default=False)
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Desaleitamento'
        verbose_name_plural = 'Desaleitamentos'

    def __str__(self):
        return f'Desaleitamento de {self.terneira} em {self.data}'

    @property
    def idade_desaleitamento_dias(self):
        if self.terneira.data_nascimento:
            return (self.data - self.terneira.data_nascimento).days
        return None
