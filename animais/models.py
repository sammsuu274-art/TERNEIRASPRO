from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


RACAS = [
    ('holandes', 'Holandês'),
    ('jersey', 'Jersey'),
    ('girolando', 'Girolando'),
    ('gir_leiteiro', 'Gir Leiteiro'),
    ('guzera', 'Guzerá'),
    ('pardo_suico', 'Pardo Suíço'),
    ('mestaca', 'Mestiça'),
    ('outra', 'Outra'),
]

SEXO_CHOICES = [
    ('F', 'Fêmea'),
    ('M', 'Macho'),
]

SITUACAO_CHOICES = [
    ('ativa', 'Ativa'),
    ('morta', 'Morta'),
    ('vendida', 'Vendida'),
    ('descartada', 'Descartada'),
    ('transferida', 'Transferida'),
]

CATEGORIA_CHOICES = [
    ('terneira', 'Terneira'),
    ('novilha', 'Novilha'),
    ('vaca', 'Vaca'),
    ('touro', 'Touro'),
    ('bezerro', 'Bezerro (macho)'),
]


class Animal(models.Model):
    """Representa qualquer bovino da propriedade — vaca, terneira, touro ou bezerro macho."""

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='animais', verbose_name='Propriedade',
    )
    identificacao = models.CharField('Identificação (brinco/chip/nome)', max_length=50)
    nome = models.CharField('Nome', max_length=100, blank=True)
    sexo = models.CharField('Sexo', max_length=1, choices=SEXO_CHOICES)
    raca = models.CharField('Raça', max_length=30, choices=RACAS)
    raca_descricao = models.CharField('Descrição da raça', max_length=100, blank=True,
                                      help_text='Detalhe quando raça = Mestiça ou Outra')
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True)
    mae = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='filhos', verbose_name='Mãe',
    )
    pai_identificacao = models.CharField('Identificação do pai', max_length=100, blank=True,
                                         help_text='Touro ou sêmen utilizado')
    situacao = models.CharField('Situação', max_length=20, choices=SITUACAO_CHOICES, default='ativa')
    data_saida = models.DateField('Data de saída', null=True, blank=True)
    motivo_saida = models.TextField('Motivo da saída', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['identificacao']
        unique_together = ('propriedade', 'identificacao')

    def __str__(self):
        return f'{self.identificacao} — {self.get_raca_display()} ({self.get_categoria_display()})'

    def clean(self):
        super().clean()
        if self.data_nascimento is not None:
            hoje = timezone.now().date()
            if self.data_nascimento > hoje:
                raise ValidationError({
                    'data_nascimento': 'A data de nascimento não pode ser futura.'
                })
            limite_passado = hoje.replace(year=hoje.year - 30)
            if self.data_nascimento < limite_passado:
                raise ValidationError({
                    'data_nascimento': 'Data de nascimento muito antiga (máximo 30 anos atrás).'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def idade_dias(self):
        if self.data_nascimento:
            return (timezone.now().date() - self.data_nascimento).days
        return None

    @property
    def idade_meses(self):
        dias = self.idade_dias
        if dias is not None:
            return round(dias / 30.44, 1)
        return None

    @property
    def e_femea(self):
        return self.sexo == 'F'

    @property
    def lote_atual(self):
        mov = self.movimentacoes.order_by('-data').first()
        return mov.lote if mov else None


class Lote(models.Model):
    """Grupo de manejo. Um animal pode mudar de lote ao longo do tempo."""

    TIPO_CHOICES = [
        ('pre_parto', 'Pré-parto'),
        ('maternidade', 'Maternidade'),
        ('aleitamento', 'Aleitamento'),
        ('pos_desaleitamento', 'Pós-desaleitamento'),
        ('recria', 'Recria'),
        ('vacas', 'Vacas em lactação'),
        ('secas', 'Vacas secas'),
        ('geral', 'Geral'),
    ]

    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='lotes', verbose_name='Propriedade',
    )
    nome = models.CharField('Nome do lote', max_length=100)
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['nome']
        unique_together = ('propriedade', 'nome')

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'

    @property
    def total_animais(self):
        return MovimentacaoLote.objects.filter(
            lote=self,
            animal__situacao='ativa',
        ).values('animal').distinct().count()


class MovimentacaoLote(models.Model):
    """Histórico de movimentação de animais entre lotes."""

    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE,
        related_name='movimentacoes', verbose_name='Animal',
    )
    lote = models.ForeignKey(
        Lote, on_delete=models.CASCADE,
        related_name='movimentacoes', verbose_name='Lote',
    )
    data = models.DateField('Data da movimentação')
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    registrado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Registrado por',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de lote'
        verbose_name_plural = 'Movimentações de lote'
        ordering = ['-data']

    def __str__(self):
        return f'{self.animal} → {self.lote} em {self.data}'


class CicloReprodutivo(models.Model):
    """
    Representa uma gestação específica da vaca mãe.
    Vincula o histórico da mãe ao nascimento da terneira.
    """

    SITUACAO_CHOICES = [
        ('gestando', 'Gestando'),
        ('encerrado_parto', 'Encerrado — Parto realizado'),
        ('encerrado_aborto', 'Encerrado — Aborto'),
        ('encerrado_outro', 'Encerrado — Outro motivo'),
    ]

    vaca = models.ForeignKey(
        Animal, on_delete=models.CASCADE,
        related_name='ciclos_reprodutivos', verbose_name='Vaca',
        limit_choices_to={'sexo': 'F'},
    )
    numero_lactacao = models.PositiveSmallIntegerField(
        'Número da lactação', null=True, blank=True,
        help_text='1 = primeira cria, 2 = segunda, etc.',
    )
    data_cobertura = models.DateField('Data da cobertura/IA', null=True, blank=True)
    touro_semen = models.CharField('Touro/Sêmen utilizado', max_length=200, blank=True)
    data_previsao_parto = models.DateField('Previsão do parto', null=True, blank=True)
    data_secagem = models.DateField('Data da secagem', null=True, blank=True)
    tratamento_secagem = models.CharField(
        'Tratamento de secagem', max_length=200, blank=True,
        help_text='Ex: secagem seletiva, vaca seca total, produto utilizado',
    )
    data_entrada_pre_parto = models.DateField('Entrada no pré-parto', null=True, blank=True)
    lote_pre_parto = models.ForeignKey(
        Lote, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Lote pré-parto',
    )
    ecc_entrada_pre_parto = models.DecimalField(
        'ECC na entrada do pré-parto', max_digits=3, decimal_places=1,
        null=True, blank=True,
        help_text='Escore de Condição Corporal (1,0 a 5,0)',
    )
    situacao = models.CharField(
        'Situação', max_length=30, choices=SITUACAO_CHOICES, default='gestando',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ciclo reprodutivo'
        verbose_name_plural = 'Ciclos reprodutivos'
        ordering = ['-data_previsao_parto']

    def __str__(self):
        return f'{self.vaca} — Lactação {self.numero_lactacao or "?"}'

    @property
    def dias_secos(self):
        """Calcula dias secos reais após o parto ser registrado."""
        if self.data_secagem and hasattr(self, 'parto') and self.parto.data_parto:
            return (self.parto.data_parto - self.data_secagem).days
        return None

    @property
    def dias_pre_parto(self):
        """Calcula dias efetivos no pré-parto."""
        if self.data_entrada_pre_parto and hasattr(self, 'parto') and self.parto.data_parto:
            return (self.parto.data_parto - self.data_entrada_pre_parto).days
        return None
