"""
Comando: python manage.py seed_criterios --propriedade <pk>

Cria os critérios de conformidade padrão para uma propriedade,
baseados nos referenciais técnicos Embrapa já carregados no banco.
Não sobrescreve critérios já existentes.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date


CRITERIOS_PADRAO = [
    # Colostragem — tempo até 1ª mamada
    {
        'codigo': 'colostragem_tempo',
        'valor_limite': 2.0,
        'unidade': 'horas',
        'escopo_raca': 'todas',
        'descricao_custom': 'Primeira colostragem em até 2 horas após o nascimento',
        'indicador_ref': 'tempo_colostragem',
    },
    # Colostragem — volume relativo ao peso vivo
    {
        'codigo': 'colostragem_volume_relativo',
        'valor_limite': 10.0,
        'unidade': '% do peso vivo',
        'escopo_raca': 'todas',
        'descricao_custom': 'Volume mínimo: 10% do peso ao nascer (ex: 40 kg → 4 litros)',
        'indicador_ref': 'volume_colostro',
    },
    # Colostragem — qualidade Brix
    {
        'codigo': 'colostragem_brix',
        'valor_limite': 22.0,
        'unidade': '%',
        'escopo_raca': 'todas',
        'descricao_custom': 'Brix mínimo para colostro de qualidade adequada',
        'indicador_ref': 'brix_colostro',
    },
    # Umbigo — tempo até 1ª cura
    {
        'codigo': 'umbigo_tempo',
        'valor_limite': 6.0,
        'unidade': 'horas',
        'escopo_raca': 'todas',
        'descricao_custom': 'Cura do umbigo em até 6 horas após o nascimento',
        'indicador_ref': None,
    },
    # Dias secos — mínimo
    {
        'codigo': 'dias_secos_minimo',
        'valor_limite': 45.0,
        'unidade': 'dias',
        'escopo_raca': 'todas',
        'descricao_custom': 'Período seco mínimo de 45 dias',
        'indicador_ref': 'dias_secos',
    },
    # Dias secos — máximo
    {
        'codigo': 'dias_secos_maximo',
        'valor_limite': 75.0,
        'unidade': 'dias',
        'escopo_raca': 'todas',
        'descricao_custom': 'Período seco máximo de 75 dias',
        'indicador_ref': 'dias_secos',
    },
    # Pré-parto — mínimo de dias no lote
    {
        'codigo': 'dias_pre_parto_minimo',
        'valor_limite': 21.0,
        'unidade': 'dias',
        'escopo_raca': 'todas',
        'descricao_custom': 'Mínimo de 21 dias no lote pré-parto',
        'indicador_ref': 'dias_pre_parto',
    },
    # Desaleitamento — idade mínima
    {
        'codigo': 'desaleitamento_idade_minima',
        'valor_limite': 56.0,
        'unidade': 'dias',
        'escopo_raca': 'todas',
        'descricao_custom': 'Idade mínima para desaleitamento: 56 dias',
        'indicador_ref': None,
    },
    # Desaleitamento — idade máxima
    {
        'codigo': 'desaleitamento_idade_maxima',
        'valor_limite': 90.0,
        'unidade': 'dias',
        'escopo_raca': 'todas',
        'descricao_custom': 'Idade máxima para desaleitamento: 90 dias',
        'indicador_ref': None,
    },
]


class Command(BaseCommand):
    help = 'Cria critérios de conformidade padrão para uma propriedade'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade', type=int, required=True,
            help='ID da propriedade que receberá os critérios padrão',
        )
        parser.add_argument(
            '--substituir', action='store_true',
            help='Desativa critérios existentes antes de criar os novos',
        )

    def handle(self, *args, **options):
        from core.models import Propriedade
        from config_tecnica.models import CriterioConformidade, ReferencialTecnico

        prop_id = options['propriedade']
        substituir = options['substituir']

        try:
            propriedade = Propriedade.objects.get(pk=prop_id)
        except Propriedade.DoesNotExist:
            raise CommandError(f'Propriedade com ID {prop_id} não encontrada.')

        hoje = date(2020, 1, 1)  # Vigência retroativa para cobrir dados históricos
        criados = 0
        ignorados = 0

        if substituir:
            desativados = CriterioConformidade.objects.filter(
                propriedade=propriedade, ativo=True,
            ).update(ativo=False)
            self.stdout.write(f'{desativados} critérios existentes desativados.')

        for dados in CRITERIOS_PADRAO:
            # Verifica se já existe critério ativo para este código
            if not substituir and CriterioConformidade.objects.filter(
                propriedade=propriedade,
                codigo=dados['codigo'],
                ativo=True,
                vigencia_fim__isnull=True,
            ).exists():
                ignorados += 1
                continue

            # Busca referencial técnico base (opcional)
            referencial = None
            if dados.get('indicador_ref'):
                referencial = ReferencialTecnico.objects.filter(
                    indicador=dados['indicador_ref'],
                    ativo=True,
                ).first()

            CriterioConformidade.objects.create(
                propriedade=propriedade,
                codigo=dados['codigo'],
                descricao_custom=dados['descricao_custom'],
                valor_limite=dados['valor_limite'],
                unidade=dados['unidade'],
                escopo_raca=dados['escopo_raca'],
                vigencia_inicio=hoje,
                vigencia_fim=None,
                referencial_base=referencial,
                ativo=True,
            )
            criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'{criados} critérios criados para "{propriedade.nome}" '
            f'({ignorados} já existiam e foram mantidos).'
        ))

        if ignorados > 0:
            self.stdout.write(
                'Use --substituir para desativar os existentes e recriar todos os padrões.'
            )
