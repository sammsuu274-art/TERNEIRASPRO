from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Importar regras BEA centralizadas
from bem_estar_animal.regras_bea import (
    classificar_brix_colostro,
    avaliar_volume_primeira_alimentacao,
    avaliar_volume_segunda_alimentacao,
    avaliar_desaleitamento_gradual,
    avaliar_consumo_concentrado_desmame,
    classificar_brix_serico,
    avaliar_temperatura_retal,
    classificar_escore_fezes,
    classificar_infeccao_umbilical,
    avaliar_volume_diario_aleitamento,
)


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

# ======== CHOICES PARA EXTENSÕES BEA - FASE 3 ========
METODO_DESCONGELAMENTO_CHOICES = [
    ('banho_maria', 'Banho-maria'),
    ('ambiente', 'Temperatura ambiente'),
]

RESULTADO_TIP_CHOICES = [
    ('excelente', 'Excelente'),
    ('adequado', 'Adequado'),
    ('falha', 'Falha'),
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
    
    # CAMPOS PROCAMPO - DOMÍNIO 4 (NUTRIÇÃO)
    metodo_descongelamento = models.CharField(
        'Método de descongelamento', max_length=20,
        choices=METODO_DESCONGELAMENTO_CHOICES, blank=True,
        help_text='Como o colostro congelado foi descongelado'
    )
    volume_segunda_mamada_ml = models.PositiveIntegerField(
        'Volume segunda mamada (ml)', null=True, blank=True,
        help_text='Volume fornecido na segunda mamada (meta: +5% peso até 12h)'
    )
    leite_transicao = models.BooleanField(
        'Leite de transição oferecido?', null=True, blank=True,
        help_text='Se houve fornecimento de leite de transição após colostro'
    )
    
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

    def clean(self):
        super().clean()
        if self.volume_ml is not None:
            if self.volume_ml < 50:
                raise ValidationError({
                    'volume_ml': 'Volume mínimo de colostragem é 50 ml.'
                })
            if self.volume_ml > 10000:
                raise ValidationError({
                    'volume_ml': 'Volume máximo de colostragem é 10.000 ml (10 litros).'
                })
        if self.brix is not None:
            if self.brix < 0:
                raise ValidationError({
                    'brix': 'Brix não pode ser negativo.'
                })
            if self.brix > 32:
                raise ValidationError({
                    'brix': 'Brix máximo é 32% (limite físico do refratômetro padrão).'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    @property
    def classificacao_brix(self):
        """Classificação automática do Brix do colostro."""
        return classificar_brix_colostro(float(self.brix) if self.brix else None)

    @property
    def classificacao_volume_primeira_mamada(self):
        """Classificação do volume se for a primeira mamada."""
        # Buscar peso: nascimento ou primeira pesagem
        peso = None
        if hasattr(self.terneira, 'parto_origem') and self.terneira.parto_origem:
            peso = self.terneira.parto_origem.peso_nascimento
        if not peso:
            primeira_pesagem = self.terneira.pesagens.order_by('data').first()
            if primeira_pesagem:
                peso = primeira_pesagem.peso_kg
        
        return avaliar_volume_primeira_alimentacao(
            self.volume_ml,
            float(peso) if peso else None
        )

    @property
    def classificacao_volume_segunda_mamada(self):
        """Classificação do volume da segunda mamada (se informado)."""
        peso = None
        if hasattr(self.terneira, 'parto_origem') and self.terneira.parto_origem:
            peso = self.terneira.parto_origem.peso_nascimento
        if not peso:
            primeira_pesagem = self.terneira.pesagens.order_by('data').first()
            if primeira_pesagem:
                peso = primeira_pesagem.peso_kg
        
        return avaliar_volume_segunda_alimentacao(
            self.volume_segunda_mamada_ml,
            float(peso) if peso else None
        )


class CuraUmbigo(models.Model):
    """Registro de aplicação de produto no umbigo."""
    
    ESCORE_INFECCAO_CHOICES = [
        (0, '0 — Normal/sem infecção'),
        (1, '1 — Infecção leve'),
        (2, '2 — Infecção moderada/grave'),
    ]
    
    DIAS_QUEDA_CHOICES = [
        ('3-4', '3-4 dias'),
        ('5-7', '5-7 dias'),
        ('>8', 'Mais de 8 dias'),
    ]

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
    
    # CAMPOS PROCAMPO - DOMÍNIO 1 (SAÚDE)
    escore_infeccao = models.IntegerField(
        'Escore de infecção umbilical', choices=ESCORE_INFECCAO_CHOICES,
        null=True, blank=True,
        help_text='0=Normal, 1=Infecção leve, 2=Moderada/Grave'
    )
    dias_queda_cordao = models.CharField(
        'Dias para queda do cordão', max_length=10,
        choices=DIAS_QUEDA_CHOICES, blank=True, null=True,
        help_text='Tempo desde nascimento até queda completa do cordão'
    )
    antibiotico_usado = models.BooleanField(
        'Antibiótico sistêmico usado?', null=True, blank=True,
        help_text='Se houve necessidade de antibiótico sistêmico por onfalite'
    )
    uso_preventivo = models.BooleanField(
        'Uso preventivo de injetáveis?', null=True, blank=True,
        help_text='Se houve aplicação preventiva de medicação injetável'
    )
    
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável',
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    # ======== CAMPOS BEA OPCIONAIS - FASE 2 - MANTER POR COMPATIBILIDADE ========
    numero_infeccoes = models.PositiveSmallIntegerField(
        'Número de infecções umbilicais', null=True, blank=True, default=0,
        help_text='Contador de episódios de onfalite neste animal'
    )
    
    # ======== CAMPOS EXTRAS (NÃO ESTAVAM NA ESPECIFICAÇÃO APROVADA) ========
    cor_umbigo = models.CharField(
        'Cor do umbigo - EXTRA', max_length=20, null=True, blank=True,
        help_text='CAMPO EXTRA: Ex: rosa, vermelho, roxo, preto'
    )
    espessura_mm = models.PositiveSmallIntegerField(
        'Espessura do cordão (mm) - EXTRA', null=True, blank=True,
        help_text='CAMPO EXTRA: Medida na base do cordão umbilical'
    )
    comprimento_mm = models.PositiveSmallIntegerField(
        'Comprimento do coto (mm) - EXTRA', null=True, blank=True,
        help_text='CAMPO EXTRA: Medida do coto que ainda não caiu'
    )

    class Meta:
        verbose_name = 'Cura de umbigo'
        verbose_name_plural = 'Curas de umbigo'
        ordering = ['terneira', 'data_hora']

    def __str__(self):
        return f'Umbigo {self.terneira} em {self.data_hora}'

    def clean(self):
        super().clean()

        # Escore de infecção deve estar dentro do range (0, 1 ou 2)
        if self.escore_infeccao is not None and self.escore_infeccao not in (0, 1, 2):
            raise ValidationError({
                'escore_infeccao': 'Escore de infecção deve ser 0, 1 ou 2.'
            })

        # Verificar intervalo mínimo de 6h entre aplicações no mesmo dia/terneira
        # A cartilha determina 2 aplicações no 1º dia com intervalo mínimo de 6h
        if self.terneira_id and self.data_hora:
            # Buscar curas anteriores da mesma terneira (exceto o próprio registro em edição)
            qs = CuraUmbigo.objects.filter(terneira_id=self.terneira_id)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            for cura_anterior in qs:
                if cura_anterior.data_hora:
                    delta = abs((self.data_hora - cura_anterior.data_hora).total_seconds())
                    intervalo_horas = delta / 3600
                    # Apenas avisa se o intervalo for menor que 6h (não bloqueia — pode ser
                    # uma terceira aplicação em dia diferente, ou correção legítima)
                    if intervalo_horas < 6:
                        raise ValidationError(
                            f'Intervalo mínimo entre aplicações de cura de umbigo é de 6 horas. '
                            f'Aplicação anterior registrada em {cura_anterior.data_hora.strftime("%d/%m/%Y %H:%M")} '
                            f'({intervalo_horas:.1f}h de diferença).'
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def intervalo_desde_ultima_cura_horas(self):
        """Retorna horas desde a cura imediatamente anterior da mesma terneira."""
        if not self.pk or not self.data_hora:
            return None
        anterior = (
            CuraUmbigo.objects
            .filter(terneira_id=self.terneira_id, data_hora__lt=self.data_hora)
            .exclude(pk=self.pk)
            .order_by('-data_hora')
            .first()
        )
        if anterior and anterior.data_hora:
            delta = (self.data_hora - anterior.data_hora).total_seconds()
            return round(delta / 3600, 2)
        return None

    @property
    def intervalo_valido(self):
        """True se o intervalo desde a última cura for >= 6h (ou se for a primeira cura)."""
        horas = self.intervalo_desde_ultima_cura_horas
        if horas is None:
            return None  # Primeira cura ou dado ausente — não classificável
        return horas >= 6

    @property
    def classificacao_infeccao(self):
        """Classificação automática do escore de infecção umbilical."""
        return classificar_infeccao_umbilical(self.escore_infeccao)


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

    def clean(self):
        super().clean()
        if self.peso_kg is not None:
            if self.peso_kg < 5:
                raise ValidationError({
                    'peso_kg': 'Peso mínimo é 5 kg.'
                })
            if self.peso_kg > 550:
                raise ValidationError({
                    'peso_kg': 'Peso máximo é 550 kg (escopo: terneira/novilha até primeira cobertura — Pardo Suíço ~455 kg + margem).'
                })
        if self.ecc is not None:
            if self.ecc < 1:
                raise ValidationError({
                    'ecc': 'ECC mínimo é 1,0 (escala 1,0 a 5,0).'
                })
            if self.ecc > 5:
                raise ValidationError({
                    'ecc': 'ECC máximo é 5,0 (escala 1,0 a 5,0).'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def idade_na_pesagem(self):
        if self.animal.data_nascimento:
            return (self.data - self.animal.data_nascimento).days
        return None


class OcorrenciaSanitaria(models.Model):
    """Problema de saúde com início, tratamento e desfecho."""
    
    ESCORE_FEZES_CHOICES = [
        (0, '0 — Normais/firmes'),
        (1, '1 — Ligeiramente amolecidas'),
        (2, '2 — Amolecidas/pastosas'),
        (3, '3 — Líquidas/aquosas'),
    ]
    
    ESCORE_RESPIRATORIO_CHOICES = [
        (0, '0 — Normal'),
        (1, '1 — Alteração leve'),
        (2, '2 — Alteração moderada'),
        (3, '3 — Alteração grave'),
    ]
    
    FAIXA_ETARIA_CHOICES = [
        ('0-30d', '0-30 dias'),
        ('31-60d', '31-60 dias'),
        ('>60d', 'Acima de 60 dias'),
    ]

    animal = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='ocorrencias_sanitarias', verbose_name='Animal',
    )
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_OCORRENCIA_CHOICES)
    data_inicio = models.DateField('Data de início')
    
    # CAMPOS PROCAMPO - DOMÍNIO 1 (SAÚDE)
    brix_serico_tip = models.DecimalField(
        'Brix sérico/TIP (%)', max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text='Medição do Brix no sangue (≥9,4%=excelente, <8,1%=falha)'
    )
    escore_fezes = models.IntegerField(
        'Escore de fezes', choices=ESCORE_FEZES_CHOICES,
        null=True, blank=True,
        help_text='0-1=Normal, 2-3=Diarreia'
    )
    temperatura_retal = models.DecimalField(
        'Temperatura retal (°C)', max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text='Referência doença respiratória: ≥39,4°C'
    )
    escore_respiratorio = models.IntegerField(
        'Escore respiratório', choices=ESCORE_RESPIRATORIO_CHOICES,
        null=True, blank=True,
        help_text='0=Normal, 1-3=Alterado'
    )
    faixa_etaria_auto = models.CharField(
        'Faixa etária (automática)', max_length=10,
        choices=FAIXA_ETARIA_CHOICES, blank=True,
        help_text='Calculada automaticamente pela idade no registro'
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

    # ======== CAMPOS BEA OPCIONAIS - FASE 2 - MANTER POR COMPATIBILIDADE ========
    ultrassom_7dias = models.BooleanField(
        'Ultrassom realizado nos primeiros 7 dias?', null=True, blank=True,
        help_text='Para avaliação de transferência de imunidade passiva'
    )
    
    # ======== CAMPOS EXTRAS - MANTER POR COMPATIBILIDADE ========
    desidratacao_grau = models.IntegerField(
        'Grau de desidratação (%) - EXTRA', null=True, blank=True,
        help_text='CAMPO EXTRA: 0-15%: 0=Sem desidratação, 5-8%=Leve, 8-12%=Moderada, >12%=Severa'
    )
    apetite_score = models.IntegerField(
        'Score de apetite (0-2) - EXTRA', null=True, blank=True,
        help_text='CAMPO EXTRA: 0=Normal/Voraz, 1=Reduzido, 2=Ausente'
    )

    class Meta:
        verbose_name = 'Ocorrência sanitária'
        verbose_name_plural = 'Ocorrências sanitárias'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.animal} — {self.get_tipo_display()} em {self.data_inicio}'
    
    def clean(self):
        super().clean()

        # Auto-preencher faixa etária baseada na idade do animal
        if self.animal and self.animal.data_nascimento and self.data_inicio:
            idade_dias = (self.data_inicio - self.animal.data_nascimento).days
            if idade_dias <= 30:
                self.faixa_etaria_auto = '0-30d'
            elif idade_dias <= 60:
                self.faixa_etaria_auto = '31-60d'
            else:
                self.faixa_etaria_auto = '>60d'

        # Temperatura retal: intervalo fisiológico bovino
        if self.temperatura_retal is not None:
            if self.temperatura_retal < 35.0:
                raise ValidationError({
                    'temperatura_retal': 'Temperatura retal não pode ser inferior a 35,0°C.'
                })
            if self.temperatura_retal > 43.0:
                raise ValidationError({
                    'temperatura_retal': 'Temperatura retal não pode ser superior a 43,0°C.'
                })

        # Brix sérico: intervalo fisicamente possível
        if self.brix_serico_tip is not None:
            if self.brix_serico_tip < 0:
                raise ValidationError({
                    'brix_serico_tip': 'Brix sérico não pode ser negativo.'
                })
            if self.brix_serico_tip > 30:
                raise ValidationError({
                    'brix_serico_tip': 'Brix sérico não pode ser superior a 30%.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Executa clean() antes de salvar
        super().save(*args, **kwargs)

    @property
    def duracao_dias(self):
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days
        return None

    @property
    def ativa(self):
        return self.data_fim is None

    @property
    def classificacao_brix_serico(self):
        """Classificação automática do Brix sérico (TIP)."""
        return classificar_brix_serico(float(self.brix_serico_tip) if self.brix_serico_tip else None)

    @property
    def avaliacao_temperatura(self):
        """Avaliação da temperatura retal como indicador respiratório."""
        return avaliar_temperatura_retal(float(self.temperatura_retal) if self.temperatura_retal else None)

    @property
    def classificacao_fezes(self):
        """Classificação do escore de fezes / diarreia."""
        return classificar_escore_fezes(self.escore_fezes)


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
    """Regime alimentar vigente para a terneira em determinado período - EXPANDIDO PROCAMPO."""

    TIPO_ALIMENTO_CHOICES = [
        ('leite_integral', 'Leite integral'),
        ('sucedaneo', 'Sucedâneo'),
        ('misto', 'Misto (leite + sucedâneo)'),
        ('solido', 'Sólido exclusivo (pós-desaleitamento)'),
    ]
    
    FREQUENCIA_CHOICES = [
        ('1x', '1x ao dia'),
        ('2x', '2x ao dia'),
        ('3x', '3x ao dia'),
        ('a_vontade', 'À vontade'),
    ]
    
    CORRECAO_SOLIDOS_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('nao_aplicavel', 'Não aplicável'),
    ]

    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='protocolos_alimentares', verbose_name='Terneira',
    )
    data_inicio = models.DateField('Data de início')
    data_fim = models.DateField('Data de fim', null=True, blank=True)
    tipo_alimento = models.CharField('Tipo de alimento', max_length=30, choices=TIPO_ALIMENTO_CHOICES)
    
    # CAMPOS PROCAMPO - DOMÍNIO 4 (NUTRIÇÃO) - EXPANDIDOS
    # Volume e frequência por faixa etária
    volume_dia_0_30_litros = models.DecimalField(
        'Volume diário 0-30 dias (L)', max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text='Meta grande porte: ≥7L/dia'
    )
    volume_dia_31_60_litros = models.DecimalField(
        'Volume diário 31-60 dias (L)', max_digits=4, decimal_places=1,
        null=True, blank=True
    )
    volume_dia_acima_60_litros = models.DecimalField(
        'Volume diário acima 60 dias (L)', max_digits=4, decimal_places=1,
        null=True, blank=True
    )
    
    frequencia_mamadas = models.CharField(
        'Frequência de mamadas', max_length=20,
        choices=FREQUENCIA_CHOICES, blank=True
    )
    
    tipo_leite_detalhado = models.CharField(
        'Tipo de leite detalhado', max_length=100, blank=True,
        help_text='Ex: Leite integral pasteurizado, sucedâneo 22% PB'
    )
    
    correcao_solidos = models.CharField(
        'Correção de sólidos', max_length=20,
        choices=CORRECAO_SOLIDOS_CHOICES, blank=True,
        help_text='Se há adição de solúveis para elevar sólidos totais'
    )
    
    # Concentrado
    concentrado = models.CharField('Concentrado', max_length=200, blank=True)
    concentrado_proteina = models.DecimalField(
        'PB do concentrado (%)', max_digits=4, decimal_places=1,
        null=True, blank=True,
    )
    consumo_concentrado_estimado_kg = models.DecimalField(
        'Consumo estimado concentrado (kg/dia)', max_digits=5, decimal_places=3,
        null=True, blank=True
    )
    
    # Volumoso e água
    feno = models.BooleanField('Oferece feno?', default=False)
    tipo_volumoso = models.CharField('Tipo de volumoso', max_length=100, blank=True,
                                      help_text='Ex: Feno coast-cross, silagem milho')
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

    @property
    def classificacao_volume_0_30d(self):
        """Classificação do volume diário para terneiras 0-30 dias."""
        raca = self.terneira.raca if hasattr(self, 'terneira') else None
        return avaliar_volume_diario_aleitamento(
            float(self.volume_dia_0_30_litros) if self.volume_dia_0_30_litros else None,
            raca
        )


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
    
    # CAMPOS PROCAMPO - DOMÍNIO 4 (NUTRIÇÃO)
    consumo_concentrado_kg = models.DecimalField(
        'Consumo concentrado exato (kg/dia)', max_digits=5, decimal_places=3,
        null=True, blank=True,
        help_text='Meta ao desmame: 1,2-1,5 kg/dia'
    )
    duracao_gradual_dias = models.PositiveSmallIntegerField(
        'Duração desaleitamento gradual (dias)', null=True, blank=True,
        help_text='Meta: ≥10 dias para desaleitamento gradual'
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

    def clean(self):
        super().clean()
        # Consumo concentrado: limites fisiológicos
        if self.consumo_concentrado_kg is not None:
            if self.consumo_concentrado_kg < 0:
                raise ValidationError({
                    'consumo_concentrado_kg': 'Consumo de concentrado não pode ser negativo.'
                })
            if self.consumo_concentrado_kg > 10:
                raise ValidationError({
                    'consumo_concentrado_kg': 'Consumo de concentrado não pode ultrapassar 10 kg/dia para terneiras.'
                })
        # Duração gradual: limite razoável
        if self.duracao_gradual_dias is not None:
            if self.duracao_gradual_dias > 90:
                raise ValidationError({
                    'duracao_gradual_dias': 'Duração do desaleitamento gradual não pode ultrapassar 90 dias.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def idade_desaleitamento_dias(self):
        if self.terneira.data_nascimento:
            return (self.data - self.terneira.data_nascimento).days
        return None

    @property
    def classificacao_duracao_gradual(self):
        """Classificação da duração do desaleitamento gradual."""
        return avaliar_desaleitamento_gradual(self.duracao_gradual_dias, self.metodo)

    @property
    def classificacao_consumo_concentrado(self):
        """Classificação do consumo de concentrado no desmame."""
        return avaliar_consumo_concentrado_desmame(
            float(self.consumo_concentrado_kg) if self.consumo_concentrado_kg else None
        )


# ======== EXTENSÕES BEA - FASE 3 ========

class ColostragemBEA(models.Model):
    """Extensão BEA para dados de bem-estar animal da colostragem."""
    
    colostragem_origem = models.OneToOneField(
        Colostragem, on_delete=models.CASCADE,
        related_name='extensao_bea', verbose_name='Colostragem'
    )
    horario_primeira_mamada = models.DateTimeField(
        'Horário da primeira mamada', null=True, blank=True,
        help_text='Registro do primeiro fornecimento de colostro'
    )
    horario_segunda_mamada = models.DateTimeField(
        'Horário da segunda mamada', null=True, blank=True,
        help_text='Registro do segundo fornecimento de colostro'
    )
    metodo_descongelamento = models.CharField(
        'Método de descongelamento', max_length=20, 
        choices=METODO_DESCONGELAMENTO_CHOICES, blank=True,
        help_text='Como o colostro foi descongelado (se aplicável)'
    )
    leite_transicao = models.BooleanField(
        'Leite de transição oferecido?', null=True, blank=True,
        help_text='Se houve fornecimento de leite de transição'
    )
    
    class Meta:
        verbose_name = 'Extensão BEA - Colostragem'
        verbose_name_plural = 'Extensões BEA - Colostragem'
    
    def __str__(self):
        return f'BEA - {self.colostragem_origem}'


class PesagemBEA(models.Model):
    """Extensão BEA para dados de bem-estar animal da pesagem."""
    
    pesagem_origem = models.OneToOneField(
        Pesagem, on_delete=models.CASCADE,
        related_name='extensao_bea', verbose_name='Pesagem'
    )
    brix_serico = models.DecimalField(
        'Brix sérico (%)', max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text='Medição do Brix no sangue para avaliação de imunidade'
    )
    data_coleta_sangue = models.DateField(
        'Data da coleta de sangue', null=True, blank=True,
        help_text='Data em que foi coletado o sangue para análise de Brix'
    )
    resultado_tip = models.CharField(
        'Resultado TIP', max_length=20,
        choices=RESULTADO_TIP_CHOICES, blank=True,
        help_text='Resultado da avaliação de transferência de imunidade passiva'
    )
    
    class Meta:
        verbose_name = 'Extensão BEA - Pesagem'
        verbose_name_plural = 'Extensões BEA - Pesagem'
    
    def __str__(self):
        return f'BEA - {self.pesagem_origem}'
