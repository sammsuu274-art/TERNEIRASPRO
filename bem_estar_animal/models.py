from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Importar regras BEA centralizadas
from .regras_bea import (
    avaliar_area_individual,
    avaliar_area_coletiva,
    avaliar_profundidade_cama,
    avaliar_estimulo_tatil_6h,
    avaliar_idade_mocacao,
    avaliar_protocolo_dor_mocacao,
    avaliar_volume_diario_aleitamento,
)


TIPO_EVIDENCIA_CHOICES = [
    ('foto', 'Foto'),
    ('video', 'Vídeo'),
]


class AmbienteBEA(models.Model):
    """
    Avaliação do ambiente conforme requisitos Be.animal - Domínio Ambiente
    Model 100% novo - ZERO conflito com sistema atual
    """
    
    # Vinculação
    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='ambiente_bea', verbose_name='Terneira',
        limit_choices_to={'sexo': 'F', 'categoria': 'terneira'}
    )
    data_avaliacao = models.DateField('Data da avaliação', default=timezone.now)
    
    # Parição e alojamento
    local_paricao = models.CharField(
        'Local de parição', max_length=20, blank=True,
        choices=[
            ('bercario', 'Berçário'),
            ('pre_desmame', 'Pré-desmame'),
            ('maternidade', 'Maternidade'),
            ('pasto', 'Pasto'),
        ]
    )
    tipo_alojamento = models.CharField(
        'Tipo de alojamento', max_length=20, blank=True,
        choices=[
            ('individual', 'Individual'),
            ('coletivo', 'Coletivo'),
            ('suspenso', 'Suspenso'),
            ('chao', 'Chão'),
        ]
    )
    
    # Dimensões da baia
    dimensao_baia_m2 = models.DecimalField(
        'Dimensão da baia (m²)', max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text='≥3m² para individual, ≥4m²/animal para coletivo'
    )
    numero_animais_baia = models.PositiveIntegerField(
        'Número de animais na baia', null=True, blank=True,
        help_text='Para alojamento coletivo'
    )
    
    # Cama
    tipo_cama = models.CharField(
        'Tipo de cama', max_length=50, blank=True,
        help_text='Ex: palha, maravalha, areia'
    )
    profundidade_cama_cm = models.PositiveIntegerField(
        'Profundidade da cama (cm)', null=True, blank=True,
        help_text='Meta: ≥30cm'
    )
    score_sujidade = models.CharField(
        'Score de sujidade da cama', max_length=20, blank=True,
        choices=[
            ('muito_limpo', 'Muito limpo'),
            ('limpo', 'Limpo'),
            ('suja', 'Suja'),
            ('muito_suja', 'Muito suja'),
        ]
    )
    
    # Microclima
    tem_aquecimento = models.BooleanField(
        'Tem aquecimento?', null=True, blank=True
    )
    cortinas_adequadas = models.BooleanField(
        'Cortinas >45cm altura?', null=True, blank=True
    )
    tem_sombra = models.BooleanField(
        'Tem sombra?', null=True, blank=True
    )
    tem_ventilacao = models.BooleanField(
        'Tem ventilação/ventiladores?', null=True, blank=True
    )
    
    # Higiene de utensílios
    freq_lavagem_mamadeiras = models.CharField(
        'Frequência lavagem mamadeiras', max_length=20, blank=True,
        choices=[
            ('apos_uso', 'Após cada uso'),
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('eventual', 'Eventual'),
        ]
    )
    freq_lavagem_sondas = models.CharField(
        'Frequência lavagem sondas', max_length=20, blank=True,
        choices=[
            ('apos_uso', 'Após cada uso'),
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('eventual', 'Eventual'),
        ]
    )
    freq_lavagem_bebedouros = models.CharField(
        'Frequência lavagem bebedouros', max_length=20, blank=True,
        choices=[
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('quinzenal', 'Quinzenal'),
            ('eventual', 'Eventual'),
        ]
    )
    
    # CAMPOS PROCAMPO - DOMÍNIO 2 e 3 (AMBIENTE e LIMPEZA) - EXPANDIDOS
    freq_lavagem_baldes = models.CharField(
        'Frequência lavagem baldes', max_length=20, blank=True,
        choices=[
            ('apos_uso', 'Após cada uso'),
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('eventual', 'Eventual'),
        ]
    )
    freq_lavagem_cochos = models.CharField(
        'Frequência lavagem cochos', max_length=20, blank=True,
        choices=[
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('quinzenal', 'Quinzenal'),
            ('eventual', 'Eventual'),
        ]
    )
    freq_desinfeccao_baias = models.CharField(
        'Frequência desinfecção baias', max_length=20, blank=True,
        choices=[
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('quinzenal', 'Quinzenal'),
            ('mensal', 'Mensal'),
            ('eventual', 'Eventual'),
        ]
    )
    fase_alojamento = models.CharField(
        'Fase de alojamento', max_length=20, blank=True,
        choices=[
            ('bercario', 'Berçário (0-2 meses)'),
            ('pre_desmame', 'Pré-desmame (2-6 meses)'),
        ],
        help_text='Separar avaliação por fase de desenvolvimento'
    )
    
    produto_higiene = models.CharField(
        'Produto usado na higiene', max_length=100, blank=True,
        help_text='Nome do produto de limpeza/desinfetante'
    )
    tem_pop_elaborado = models.BooleanField(
        'POP de higiene elaborado?', null=True, blank=True,
        help_text='Procedimento Operacional Padrão'
    )
    limpeza_acida_semanal = models.BooleanField(
        'Limpeza ácida semanal?', null=True, blank=True
    )

    # CAMPO PROCAMPO — DOMÍNIO 3 (LIMPEZA E DESINFECÇÃO)
    treinamento_equipe = models.BooleanField(
        'Equipe recebeu treinamento de higiene?', null=True, blank=True,
        help_text='Confirma se a equipe foi treinada nos protocolos de limpeza e desinfecção'
    )
    
    # Metadados
    responsavel_avaliacao = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável pela avaliação'
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avaliação de Ambiente BEA'
        verbose_name_plural = 'Avaliações de Ambiente BEA'
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f'Ambiente BEA - {self.terneira} em {self.data_avaliacao}'

    def clean(self):
        super().clean()
        # Dimensão da baia não pode ser negativa ou zero
        if self.dimensao_baia_m2 is not None:
            if self.dimensao_baia_m2 <= 0:
                raise ValidationError({
                    'dimensao_baia_m2': 'Dimensão da baia deve ser maior que zero.'
                })
            if self.dimensao_baia_m2 > 500:
                raise ValidationError({
                    'dimensao_baia_m2': 'Dimensão da baia não pode ser superior a 500 m².'
                })
        # Número de animais deve ser positivo
        if self.numero_animais_baia is not None and self.numero_animais_baia < 1:
            raise ValidationError({
                'numero_animais_baia': 'Número de animais deve ser pelo menos 1.'
            })
        # Profundidade da cama: limite razoável
        if self.profundidade_cama_cm is not None:
            if self.profundidade_cama_cm > 200:
                raise ValidationError({
                    'profundidade_cama_cm': 'Profundidade da cama não pode superar 200 cm.'
                })

    @property
    def adequacao_dimensao_individual(self):
        """B2 - Dimensão adequada para alojamento individual (≥3m²)"""
        if self.tipo_alojamento != 'individual':
            return None  # Não aplicável
        if self.dimensao_baia_m2 is None:
            return None  # Dado ausente
        return self.dimensao_baia_m2 >= 3.0

    @property
    def adequacao_dimensao_coletiva(self):
        """B3 - Dimensão adequada para alojamento coletivo (≥4m²/animal)"""
        if self.tipo_alojamento != 'coletivo':
            return None  # Não aplicável
        if self.dimensao_baia_m2 is None or self.numero_animais_baia is None:
            return None  # Dado ausente
        m2_por_animal = float(self.dimensao_baia_m2) / self.numero_animais_baia
        return m2_por_animal >= 4.0

    @property
    def adequacao_profundidade_cama(self):
        """B4 - Profundidade da cama adequada (≥30cm)"""
        if self.profundidade_cama_cm is None:
            return None  # Dado ausente
        return self.profundidade_cama_cm >= 30

    @property
    def classificacao_area(self):
        """Classificação automática da área conforme tipo de alojamento."""
        if self.tipo_alojamento == 'individual':
            return avaliar_area_individual(
                float(self.dimensao_baia_m2) if self.dimensao_baia_m2 else None
            )
        elif self.tipo_alojamento == 'coletivo':
            return avaliar_area_coletiva(
                float(self.dimensao_baia_m2) if self.dimensao_baia_m2 else None,
                self.numero_animais_baia
            )
        else:
            from .regras_bea import Classificacao
            return {
                'classificacao': Classificacao.NAO_APLICAVEL,
                'valor': None,
                'referencia': 'Individual: ≥3m², Coletivo: ≥4m²/animal',
                'justificativa': 'Tipo de alojamento não especificado.',
            }

    @property
    def classificacao_cama(self):
        """Classificação automática da profundidade da cama."""
        return avaliar_profundidade_cama(self.profundidade_cama_cm)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ComportamentoBEA(models.Model):
    """
    Avaliação do comportamento conforme requisitos Be.animal - Domínio Comportamento
    Model 100% novo - ZERO conflito com sistema atual
    """
    
    # Vinculação
    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='comportamento_bea', verbose_name='Terneira',
        limit_choices_to={'sexo': 'F', 'categoria': 'terneira'}
    )
    data_avaliacao = models.DateField('Data da avaliação', default=timezone.now)
    
    # Estímulo tátil
    estimulo_6h = models.BooleanField(
        'Estímulo tátil nas primeiras 6h?', null=True, blank=True,
        help_text='Estímulo tátil aplicado nas primeiras 6 horas de vida'
    )
    continuidade_diaria = models.BooleanField(
        'Continuidade diária do estímulo?', null=True, blank=True,
        help_text='Estímulo tátil mantido diariamente após as primeiras 6h'
    )
    
    # Agrupamento
    idade_agrupamento_dias = models.PositiveIntegerField(
        'Idade do agrupamento (dias)', null=True, blank=True,
        help_text='Idade em que a terneira foi colocada com outras'
    )
    tipo_agrupamento = models.CharField(
        'Tipo de agrupamento', max_length=20, blank=True,
        choices=[
            ('pares', 'Em pares'),
            ('grupos', 'Em grupos'),
            ('individual', 'Mantida individual'),
        ]
    )
    tem_enriquecimento = models.BooleanField(
        'Tem enriquecimento ambiental?', null=True, blank=True
    )
    tipo_enriquecimento = models.CharField(
        'Tipo de enriquecimento', max_length=200, blank=True,
        help_text='Descreva os itens de enriquecimento ambiental'
    )
    
    # Mochação
    mocacao_realizada = models.BooleanField(
        'Mochação realizada?', null=True, blank=True
    )
    mocacao_idade_semanas = models.PositiveIntegerField(
        'Idade na mochação (semanas)', null=True, blank=True,
        help_text='Meta: 3-4 semanas'
    )
    mocacao_metodo = models.CharField(
        'Método de mochação', max_length=30, blank=True,
        choices=[
            ('ferro_quente', 'Ferro quente'),
            ('pasta_caustica', 'Pasta cáustica'),
            ('outro', 'Outro método'),
        ]
    )
    
    # Protocolo de mitigação de dor (mochação)
    protocolo_dor_anestesia = models.BooleanField(
        'Anestesia aplicada?', null=True, blank=True
    )
    protocolo_dor_analgesia = models.BooleanField(
        'Analgesia aplicada?', null=True, blank=True
    )
    protocolo_dor_sedacao = models.BooleanField(
        'Sedação aplicada?', null=True, blank=True
    )
    
    # Remoção de tetas supranumerárias
    remocao_tetas_realizada = models.BooleanField(
        'Remoção de tetas supranumerárias realizada?', null=True, blank=True
    )
    protocolo_dor_tetas = models.BooleanField(
        'Protocolo de dor para remoção de tetas?', null=True, blank=True,
        help_text='Anestesia/analgesia para remoção de tetas supranumerárias'
    )
    
    # Metadados
    responsavel_avaliacao = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável pela avaliação'
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avaliação de Comportamento BEA'
        verbose_name_plural = 'Avaliações de Comportamento BEA'
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f'Comportamento BEA - {self.terneira} em {self.data_avaliacao}'

    @property
    def adequacao_estimulo_6h(self):
        """B10 - Estímulo tátil nas primeiras 6h"""
        if self.estimulo_6h is None:
            return None  # Dado ausente
        return self.estimulo_6h

    @property
    def adequacao_idade_mocacao(self):
        """B9 - Idade adequada para mochação (3-4 semanas)"""
        if self.mocacao_idade_semanas is None:
            return None  # Dado ausente
        return 3 <= self.mocacao_idade_semanas <= 4

    @property
    def classificacao_estimulo_6h(self):
        """Classificação automática do estímulo tátil nas primeiras 6h."""
        return avaliar_estimulo_tatil_6h(self.estimulo_6h)

    @property
    def classificacao_idade_mocacao(self):
        """Classificação automática da idade na mochação."""
        return avaliar_idade_mocacao(self.mocacao_idade_semanas)

    @property
    def classificacao_protocolo_dor(self):
        """Classificação automática do protocolo de controle da dor na mochação."""
        return avaliar_protocolo_dor_mocacao(
            self.protocolo_dor_anestesia,
            self.protocolo_dor_analgesia,
            self.protocolo_dor_sedacao
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ======== FASE 4: VISITAS, CONSENTIMENTO E EVIDÊNCIAS ========

class VisitaPresencialBEA(models.Model):
    """Visita presencial para acompanhamento BEA - expandida para Jornada ProCampo"""
    
    TIPO_VISITA_CHOICES = [
        ('baseline', 'Baseline/Diagnóstico Inicial'),
        ('acompanhamento', 'Acompanhamento'),
        ('reavaliacao', 'Reavaliação'),
        ('final', 'Visita Final'),
    ]
    
    # Vinculação básica
    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='visitas_bea', verbose_name='Propriedade'
    )
    jornada = models.ForeignKey(
        'JornadaProCampo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='visitas',
        verbose_name='Jornada ProCampo'
    )
    
    # Identificação
    data_visita = models.DateField('Data da visita')
    tipo_visita = models.CharField('Tipo de visita', max_length=20,
                                    choices=TIPO_VISITA_CHOICES, blank=True)
    numero_visita = models.PositiveSmallIntegerField('Número da visita',
                                                      null=True, blank=True,
                                                      help_text='1ª, 2ª, 3ª visita...')
    
    # Participantes
    responsavel_tecnico = models.ForeignKey(
        'accounts.Usuario', on_delete=models.CASCADE,
        related_name='visitas_realizadas_bea', verbose_name='Responsável técnico',
        limit_choices_to={'perfis__papel__in': ['tecnico', 'admin']}
    )
    produtor_visitado = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        related_name='visitas_recebidas_bea', verbose_name='Produtor visitado',
        limit_choices_to={'perfis__papel': 'produtor'},
        null=True, blank=True
    )
    
    # Conteúdo da visita
    observacoes_gerais = models.TextField('Observações gerais', blank=True)
    problemas_identificados = models.TextField('Problemas identificados', blank=True,
                                                help_text='Liste os principais problemas encontrados')
    acoes_recomendadas = models.TextField('Ações recomendadas', blank=True,
                                           help_text='O que foi recomendado ao produtor')
    
    # Metadados
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Visita Presencial BEA'
        verbose_name_plural = 'Visitas Presenciais BEA'
        ordering = ['-data_visita']

    def __str__(self):
        if self.jornada:
            return f'Visita {self.numero_visita or "?"} - {self.jornada.nome} em {self.data_visita}'
        return f'Visita {self.propriedade} em {self.data_visita}'

    def clean(self):
        super().clean()
        
        # Importar aqui para evitar import circular
        from accounts.models import UsuarioPerfil
        
        # Validar responsável técnico
        if self.responsavel_tecnico:
            try:
                perfil = self.responsavel_tecnico.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel not in ['tecnico', 'admin']:
                    raise ValidationError({
                        'responsavel_tecnico': 'Responsável técnico deve ter papel "técnico" ou "admin".'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'responsavel_tecnico': 'Responsável técnico deve estar vinculado à propriedade como técnico ou admin.'
                })
        
        # Validar produtor visitado
        if self.produtor_visitado:
            try:
                perfil = self.produtor_visitado.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel != 'produtor':
                    raise ValidationError({
                        'produtor_visitado': 'Produtor visitado deve ter papel "produtor".'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'produtor_visitado': 'Produtor visitado deve estar vinculado à propriedade como produtor.'
                })
        
        # Auto-numerar visita se vinculada a jornada
        if self.jornada and not self.numero_visita:
            self.numero_visita = self.jornada.visitas.count() + 1

    def save(self, *args, **kwargs):
        self.full_clean()  # Força execução do clean()
        super().save(*args, **kwargs)


class ConsentimentoBEA(models.Model):
    """Consentimento de dados e imagem para BEA"""
    
    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='consentimentos_bea', verbose_name='Propriedade'
    )
    produtor = models.ForeignKey(
        'accounts.Usuario', on_delete=models.CASCADE,
        related_name='consentimentos_bea', verbose_name='Produtor',
        limit_choices_to={'perfis__papel': 'produtor'}
    )
    consentimento_dados = models.BooleanField('Consentimento uso de dados', default=False)
    consentimento_imagem = models.BooleanField('Consentimento uso de imagem', default=False)
    data_consentimento = models.DateTimeField('Data do consentimento')
    responsavel_coleta = models.ForeignKey(
        'accounts.Usuario', on_delete=models.CASCADE,
        related_name='consentimentos_coletados_bea', verbose_name='Responsável pela coleta',
        limit_choices_to={'perfis__papel__in': ['tecnico', 'admin']}
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Consentimento BEA'
        verbose_name_plural = 'Consentimentos BEA'
        ordering = ['-data_consentimento']
        unique_together = ('propriedade', 'produtor')

    def __str__(self):
        return f'Consentimento {self.produtor} - {self.propriedade}'

    def clean(self):
        super().clean()
        
        # Importar aqui para evitar import circular
        from accounts.models import UsuarioPerfil
        
        # Validar responsável coleta
        if self.responsavel_coleta:
            try:
                perfil = self.responsavel_coleta.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel not in ['tecnico', 'admin']:
                    raise ValidationError({
                        'responsavel_coleta': 'Responsável pela coleta deve ter papel "técnico" ou "admin".'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'responsavel_coleta': 'Responsável pela coleta deve estar vinculado à propriedade como técnico ou admin.'
                })
        
        # Validar produtor
        if self.produtor:
            try:
                perfil = self.produtor.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel != 'produtor':
                    raise ValidationError({
                        'produtor': 'Usuário deve ter papel "produtor".'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'produtor': 'Produtor deve estar vinculado à propriedade como produtor.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Força execução do clean()
        super().save(*args, **kwargs)


class EvidenciasBEA(models.Model):
    """Evidências fotográficas/vídeo para avaliações BEA"""
    
    # GenericForeignKey para vincular a qualquer model BEA
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    tipo_evidencia = models.CharField(
        'Tipo de evidência', max_length=10, choices=TIPO_EVIDENCIA_CHOICES
    )
    arquivo = models.FileField(
        'Arquivo', upload_to='evidencias_bea/%Y/%m/',
        help_text='Fotos: máx 10MB | Vídeos: máx 50MB'
    )
    descricao = models.CharField('Descrição', max_length=200, blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    usuario_upload = models.ForeignKey(
        'accounts.Usuario', on_delete=models.CASCADE,
        related_name='evidencias_bea', verbose_name='Usuário que fez upload'
    )

    class Meta:
        verbose_name = 'Evidência BEA'
        verbose_name_plural = 'Evidências BEA'
        ordering = ['-data_upload']

    def __str__(self):
        return f'Evidência {self.get_tipo_evidencia_display()} - {self.objeto_vinculado_nome()}'

    def objeto_vinculado_nome(self):
        """Retorna nome do tipo do objeto vinculado"""
        if self.content_object:
            return self.content_object.__class__.__name__
        return 'Objeto não encontrado'

    def _resolver_propriedade_e_produtor(self):
        """
        Resolve a propriedade e produtores a partir do objeto vinculado.
        Retorna (propriedade, [lista de produtores])
        Levanta ValidationError se não conseguir resolver.
        """
        if not self.content_object:
            raise ValidationError(
                'Não é possível validar consentimento: objeto vinculado não existe ou foi removido.'
            )
        
        obj = self.content_object
        model_name = obj.__class__.__name__
        propriedade = None
        animal = None
        
        # Resolver propriedade e animal dependendo do tipo de objeto
        if model_name == 'AmbienteBEA':
            animal = obj.terneira
            propriedade = animal.propriedade if animal else None
        elif model_name == 'ComportamentoBEA':
            animal = obj.terneira
            propriedade = animal.propriedade if animal else None
        elif model_name == 'ColostragemBEA':
            if hasattr(obj, 'colostragem_origem') and obj.colostragem_origem:
                animal = obj.colostragem_origem.terneira
                propriedade = animal.propriedade if animal else None
        elif model_name == 'PesagemBEA':
            if hasattr(obj, 'pesagem_origem') and obj.pesagem_origem:
                animal = obj.pesagem_origem.animal
                propriedade = animal.propriedade if animal else None
        else:
            raise ValidationError(
                f'Tipo de objeto "{model_name}" não suportado para evidências BEA. '
                f'Tipos válidos: AmbienteBEA, ComportamentoBEA, ColostragemBEA, PesagemBEA.'
            )
        
        if not propriedade:
            raise ValidationError(
                f'Não foi possível determinar a propriedade a partir do {model_name}. '
                f'Verifique se o animal está corretamente vinculado.'
            )
        
        # Buscar produtores vinculados à propriedade
        from accounts.models import UsuarioPerfil
        produtores = UsuarioPerfil.objects.filter(
            propriedade=propriedade,
            papel='produtor',
            ativo=True
        ).values_list('usuario', flat=True)
        
        if not produtores:
            raise ValidationError(
                f'Não há produtores ativos vinculados à propriedade "{propriedade.nome}". '
                f'É necessário ter ao menos um produtor cadastrado para registrar evidências.'
            )
        
        return propriedade, list(produtores)

    def _verificar_consentimento_produtores(self, propriedade, produtores_ids):
        """
        Verifica se há pelo menos um produtor da propriedade com consentimento válido.
        Retorna True se houver consentimento válido, False caso contrário.
        """
        from accounts.models import Usuario
        
        for produtor_id in produtores_ids:
            try:
                produtor = Usuario.objects.get(id=produtor_id)
                if produtor.tem_consentimento_valido(propriedade):
                    return True
            except Usuario.DoesNotExist:
                continue
        
        return False

    def clean(self):
        super().clean()
        
        # Validar consentimento dos produtores da propriedade
        try:
            propriedade, produtores_ids = self._resolver_propriedade_e_produtor()
            
            if not self._verificar_consentimento_produtores(propriedade, produtores_ids):
                raise ValidationError(
                    f'Não é possível fazer upload de evidências para a propriedade "{propriedade.nome}" '
                    f'sem consentimento válido de dados e imagem de pelo menos um produtor. '
                    f'Registre o consentimento antes de prosseguir.'
                )
        except ValidationError:
            # Re-lançar ValidationErrors do resolver
            raise
        
        # Validar tamanho do arquivo
        if self.arquivo:
            file_size = self.arquivo.size
            if self.tipo_evidencia == 'foto' and file_size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError({'arquivo': 'Fotos devem ter no máximo 10MB.'})
            elif self.tipo_evidencia == 'video' and file_size > 50 * 1024 * 1024:  # 50MB
                raise ValidationError({'arquivo': 'Vídeos devem ter no máximo 50MB.'})
            
            # Validar extensões
            import os
            ext = os.path.splitext(self.arquivo.name)[1].lower()
            if self.tipo_evidencia == 'foto' and ext not in ['.jpg', '.jpeg', '.png']:
                raise ValidationError({'arquivo': 'Fotos devem ser JPG ou PNG.'})
            elif self.tipo_evidencia == 'video' and ext not in ['.mp4', '.mov']:
                raise ValidationError({'arquivo': 'Vídeos devem ser MP4 ou MOV.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Força execução do clean()
        super().save(*args, **kwargs)


# ======== PROGRAMA PROCAMPO: JORNADA BEM-ESTAR ANIMAL ========

class JornadaProCampo(models.Model):
    """
    Jornada completa de bem-estar animal conforme programa ProCampo Piracanjuba.
    Cada jornada acompanha 1 produtor em 1 propriedade por 6 meses com mínimo 3 visitas.
    """
    
    STATUS_JORNADA_CHOICES = [
        ('planejamento', 'Planejamento'),
        ('em_andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Identificação
    nome = models.CharField('Nome da jornada', max_length=200,
                            help_text='Ex: ProCampo 2026 - Fazenda São José')
    
    # Participantes
    supervisor = models.ForeignKey(
        'accounts.Usuario', on_delete=models.PROTECT,
        related_name='jornadas_supervisionadas', verbose_name='Supervisor responsável',
        limit_choices_to={'perfis__papel__in': ['tecnico', 'admin']}
    )
    produtor = models.ForeignKey(
        'accounts.Usuario', on_delete=models.PROTECT,
        related_name='jornadas_produtor', verbose_name='Produtor participante',
        limit_choices_to={'perfis__papel': 'produtor'}
    )
    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.PROTECT,
        related_name='jornadas_procampo', verbose_name='Propriedade'
    )
    
    # Cronograma
    data_selecao_produtor = models.DateField('Data de seleção do produtor',
                                              help_text='Limite: 30/08/2026')
    data_inicio = models.DateField('Data de início da jornada')
    data_prevista_conclusao = models.DateField('Data prevista para conclusão',
                                                help_text='Após 6 meses do início')
    data_conclusao = models.DateField('Data de conclusão', null=True, blank=True)
    
    # Controle
    status = models.CharField('Status', max_length=20, choices=STATUS_JORNADA_CHOICES,
                              default='planejamento')
    minimo_visitas = models.PositiveSmallIntegerField('Mínimo de visitas', default=3)
    baseline_realizado = models.BooleanField('Baseline realizado?', default=False)
    case_sucesso_gerado = models.BooleanField('Case de sucesso gerado?', default=False)
    
    # Consentimento
    consentimento = models.ForeignKey(
        ConsentimentoBEA, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='jornadas',
        verbose_name='Consentimento associado'
    )
    
    # Observações
    objetivo_principal = models.TextField('Objetivo principal da jornada', blank=True)
    observacoes = models.TextField('Observações gerais', blank=True)
    motivo_cancelamento = models.TextField('Motivo do cancelamento', blank=True)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Jornada ProCampo'
        verbose_name_plural = 'Jornadas ProCampo'
        ordering = ['-data_inicio']
        unique_together = ('propriedade', 'data_inicio')
    
    def __str__(self):
        return f'{self.nome} - {self.get_status_display()}'
    
    @property
    def duracao_dias(self):
        """Duração da jornada em dias"""
        if self.data_conclusao:
            return (self.data_conclusao - self.data_inicio).days
        return (timezone.now().date() - self.data_inicio).days
    
    @property
    def total_visitas(self):
        """Total de visitas presenciais realizadas"""
        return self.visitas.count()
    
    @property
    def visitas_restantes(self):
        """Visitas restantes para atingir o mínimo"""
        restantes = self.minimo_visitas - self.total_visitas
        return max(0, restantes)
    
    @property
    def total_acoes_plano(self):
        """Total de ações no plano"""
        return self.plano_acao.count()
    
    @property
    def acoes_pendentes(self):
        """Ações pendentes no plano"""
        return self.plano_acao.filter(status__in=['pendente', 'em_andamento']).count()
    
    @property
    def acoes_concluidas(self):
        """Ações concluídas no plano"""
        return self.plano_acao.filter(status='concluido').count()
    
    @property
    def pode_concluir(self):
        """Verifica se a jornada pode ser concluída"""
        return (
            self.baseline_realizado and
            self.total_visitas >= self.minimo_visitas and
            self.acoes_pendentes == 0
        )
    
    def clean(self):
        super().clean()
        
        # Validar datas
        if self.data_inicio and self.data_selecao_produtor:
            if self.data_inicio < self.data_selecao_produtor:
                raise ValidationError({
                    'data_inicio': 'Data de início não pode ser anterior à data de seleção.'
                })
        
        if self.data_inicio and self.data_prevista_conclusao:
            if self.data_prevista_conclusao <= self.data_inicio:
                raise ValidationError({
                    'data_prevista_conclusao': 'Data de conclusão deve ser posterior à data de início.'
                })
        
        # Validar participantes
        if self.supervisor and self.propriedade:
            from accounts.models import UsuarioPerfil
            try:
                perfil = self.supervisor.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel not in ['tecnico', 'admin']:
                    raise ValidationError({
                        'supervisor': 'Supervisor deve ter papel técnico ou admin na propriedade.'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'supervisor': 'Supervisor deve estar vinculado à propriedade.'
                })
        
        if self.produtor and self.propriedade:
            from accounts.models import UsuarioPerfil
            try:
                perfil = self.produtor.perfis.get(propriedade=self.propriedade, ativo=True)
                if perfil.papel != 'produtor':
                    raise ValidationError({
                        'produtor': 'Usuário deve ter papel produtor na propriedade.'
                    })
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'produtor': 'Produtor deve estar vinculado à propriedade.'
                })


class DietaSolidaBEA(models.Model):
    """
    Domínio 5 - Água e Dieta Sólida
    Registra início e manejo de água, concentrado e volumoso.
    """
    
    TIPO_BEBEDOURO_CHOICES = [
        ('balde', 'Balde'),
        ('bebedouro_automatico', 'Bebedouro automático'),
        ('cocho_agua', 'Cocho de água'),
        ('outro', 'Outro'),
    ]
    
    FREQ_ABASTECIMENTO_CHOICES = [
        ('continuo', 'Contínuo/À vontade'),
        ('3x_dia', '3x ao dia'),
        ('2x_dia', '2x ao dia'),
        ('1x_dia', '1x ao dia'),
        ('eventual', 'Eventual'),
    ]
    
    # Vinculação
    terneira = models.ForeignKey(
        'animais.Animal', on_delete=models.CASCADE,
        related_name='dieta_solida_bea', verbose_name='Terneira',
        limit_choices_to={'sexo': 'F', 'categoria__in': ['terneira', 'novilha']}
    )
    jornada = models.ForeignKey(
        JornadaProCampo, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dietas_solidas',
        verbose_name='Jornada ProCampo'
    )
    data_avaliacao = models.DateField('Data da avaliação', default=timezone.now)
    
    # ÁGUA
    inicio_oferta_agua = models.PositiveSmallIntegerField(
        'Início oferta água (dias de vida)', null=True, blank=True,
        help_text='Recomendado: 1º dia de vida'
    )
    fonte_agua = models.CharField('Fonte de água', max_length=100, blank=True,
                                   help_text='Ex: Poço, cidade, mina, etc.')
    tipo_bebedouro = models.CharField('Tipo de bebedouro', max_length=30,
                                      choices=TIPO_BEBEDOURO_CHOICES, blank=True)
    agua_fresca_disponivel = models.BooleanField('Água fresca disponível?',
                                                   null=True, blank=True)
    
    # CONCENTRADO
    inicio_concentrado_dias = models.PositiveSmallIntegerField(
        'Início concentrado (dias de vida)', null=True, blank=True,
        help_text='Recomendado: 1º dia de vida'
    )
    tipo_racao = models.CharField('Tipo de ração/concentrado', max_length=100, blank=True,
                                   help_text='Nome comercial ou composição')
    freq_abastecimento_concentrado = models.CharField(
        'Frequência abastecimento concentrado', max_length=20,
        choices=FREQ_ABASTECIMENTO_CHOICES, blank=True
    )
    consumo_concentrado_estimado_kg = models.DecimalField(
        'Consumo estimado concentrado (kg/dia)', max_digits=5, decimal_places=3,
        null=True, blank=True,
        help_text='Média por animal'
    )
    
    # VOLUMOSO
    inicio_volumoso_dias = models.PositiveSmallIntegerField(
        'Início volumoso (dias de vida)', null=True, blank=True,
        help_text='Feno ou silagem'
    )
    tipo_volumoso = models.CharField('Tipo de volumoso', max_length=100, blank=True,
                                      help_text='Ex: Feno coast-cross, silagem milho')
    freq_abastecimento_volumoso = models.CharField(
        'Frequência abastecimento volumoso', max_length=20,
        choices=FREQ_ABASTECIMENTO_CHOICES, blank=True
    )
    consumo_volumoso_estimado_kg = models.DecimalField(
        'Consumo estimado volumoso (kg/dia)', max_digits=5, decimal_places=3,
        null=True, blank=True,
        help_text='Média por animal'
    )
    
    # Metadados
    responsavel_avaliacao = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Responsável pela avaliação'
    )
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dieta Sólida BEA'
        verbose_name_plural = 'Dietas Sólidas BEA'
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f'Dieta Sólida - {self.terneira} em {self.data_avaliacao}'
    
    @property
    def agua_adequada(self):
        """Verifica se água foi oferecida no 1º dia (recomendação)"""
        if self.inicio_oferta_agua is None:
            return None
        return self.inicio_oferta_agua <= 1
    
    @property
    def concentrado_adequado(self):
        """Verifica se concentrado foi oferecido no 1º dia (recomendação)"""
        if self.inicio_concentrado_dias is None:
            return None
        return self.inicio_concentrado_dias <= 1

    @property
    def classificacao_inicio_agua(self):
        """Classificação do início da oferta de água."""
        from .regras_bea import Classificacao
        if self.inicio_oferta_agua is None:
            return {
                'classificacao': Classificacao.NAO_INFORMADO,
                'valor': None,
                'referencia': '1º dia de vida',
                'justificativa': 'Informação não registrada.',
            }
        if self.inicio_oferta_agua <= 1:
            return {
                'classificacao': Classificacao.ADEQUADO,
                'valor': f'{self.inicio_oferta_agua} dias',
                'referencia': '≤ 1 dia',
                'justificativa': 'Água oferecida desde o início conforme recomendação.',
            }
        else:
            return {
                'classificacao': Classificacao.ATENCAO,
                'valor': f'{self.inicio_oferta_agua} dias',
                'referencia': '> 1 dia',
                'justificativa': 'Oferta de água tardia.',
            }

    @property
    def classificacao_inicio_concentrado(self):
        """Classificação do início da oferta de concentrado."""
        from .regras_bea import Classificacao
        if self.inicio_concentrado_dias is None:
            return {
                'classificacao': Classificacao.NAO_INFORMADO,
                'valor': None,
                'referencia': '1º dia de vida',
                'justificativa': 'Informação não registrada.',
            }
        if self.inicio_concentrado_dias <= 1:
            return {
                'classificacao': Classificacao.ADEQUADO,
                'valor': f'{self.inicio_concentrado_dias} dias',
                'referencia': '≤ 1 dia',
                'justificativa': 'Concentrado oferecido desde o início conforme recomendação.',
            }
        else:
            return {
                'classificacao': Classificacao.ATENCAO,
                'valor': f'{self.inicio_concentrado_dias} dias',
                'referencia': '> 1 dia',
                'justificativa': 'Oferta de concentrado tardia.',
            }


class PlanoAcaoBEA(models.Model):
    """
    Plano de ação para correção/melhoria de indicadores BEA.
    Vinculado à jornada ProCampo.
    """
    
    STATUS_ACAO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    # Vinculação
    jornada = models.ForeignKey(
        JornadaProCampo, on_delete=models.CASCADE,
        related_name='plano_acao', verbose_name='Jornada'
    )
    visita_origem = models.ForeignKey(
        VisitaPresencialBEA, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='acoes_geradas',
        verbose_name='Visita que gerou a ação'
    )
    
    # Identificação do problema
    dominio = models.CharField('Domínio', max_length=50,
                                help_text='Ex: Saúde, Ambiente, Nutrição, Comportamento')
    indicador = models.CharField('Indicador/Problema', max_length=200,
                                  help_text='Ex: Brix sérico baixo, cama suja')
    situacao_encontrada = models.TextField('Situação encontrada',
                                            help_text='Descreva o problema identificado')
    
    # Ação
    acao_recomendada = models.TextField('Ação recomendada',
                                         help_text='O que deve ser feito para corrigir')
    responsavel = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='acoes_responsavel',
        verbose_name='Responsável pela ação'
    )
    prazo = models.DateField('Prazo para conclusão')
    prioridade = models.CharField('Prioridade', max_length=10,
                                   choices=PRIORIDADE_CHOICES, default='media')
    
    # Controle
    status = models.CharField('Status', max_length=20, choices=STATUS_ACAO_CHOICES,
                              default='pendente')
    data_conclusao = models.DateField('Data de conclusão', null=True, blank=True)
    resultado_obtido = models.TextField('Resultado obtido', blank=True,
                                         help_text='Descreva o que foi realizado e o resultado')
    
    # Evidências
    # (EvidenciasBEA já pode ser vinculada via GenericForeignKey)
    
    # Metadados
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ação do Plano BEA'
        verbose_name_plural = 'Ações do Plano BEA'
        ordering = ['prazo', '-prioridade']
    
    def __str__(self):
        return f'{self.indicador} - {self.get_status_display()}'
    
    @property
    def dias_ate_prazo(self):
        """Dias restantes até o prazo"""
        if self.status in ['concluido', 'cancelado']:
            return None
        return (self.prazo - timezone.now().date()).days
    
    @property
    def esta_atrasada(self):
        """Verifica se ação está atrasada"""
        if self.status in ['concluido', 'cancelado']:
            return False
        return timezone.now().date() > self.prazo
    
    @property
    def duracao_dias(self):
        """Duração da ação em dias (se concluída)"""
        if self.status == 'concluido' and self.data_conclusao:
            return (self.data_conclusao - self.criado_em.date()).days
        return None
    
    def clean(self):
        super().clean()
        
        # Validar data de conclusão
        if self.status == 'concluido' and not self.data_conclusao:
            raise ValidationError({
                'data_conclusao': 'Data de conclusão é obrigatória quando status é "concluído".'
            })
        
        if self.data_conclusao and self.data_conclusao > timezone.now().date():
            raise ValidationError({
                'data_conclusao': 'Data de conclusão não pode ser futura.'
            })
        
        # Validar responsável
        if self.responsavel and self.jornada:
            from accounts.models import UsuarioPerfil
            try:
                UsuarioPerfil.objects.get(
                    usuario=self.responsavel,
                    propriedade=self.jornada.propriedade,
                    ativo=True
                )
            except UsuarioPerfil.DoesNotExist:
                raise ValidationError({
                    'responsavel': 'Responsável deve estar vinculado à propriedade da jornada.'
                })
