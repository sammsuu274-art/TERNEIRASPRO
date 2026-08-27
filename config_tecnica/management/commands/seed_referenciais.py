"""
Comando: python manage.py seed_referenciais
Carrega os referenciais técnicos iniciais baseados em Embrapa e literatura.
"""

from django.core.management.base import BaseCommand
from config_tecnica.models import ReferencialTecnico


REFERENCIAIS = [
    dict(
        indicador='tempo_colostragem',
        descricao='Tempo máximo para primeira colostragem',
        valor_ideal=2.0, valor_maximo=6.0, unidade='horas',
        populacao='Terneiras leiteiras em geral',
        fonte='Godden, 2008 — Vet Clinics North America',
        autor='Godden, S.M.', ano=2008,
        observacoes='Absorção de imunoglobulinas diminui progressivamente. Eficiência máxima nas primeiras 2 horas.',
    ),
    dict(
        indicador='volume_colostro',
        descricao='Volume de colostro na primeira mamada (% do peso vivo)',
        valor_ideal=10.0, unidade='% do peso vivo (ml/kg)',
        populacao='Terneiras leiteiras',
        fonte='Embrapa Gado de Leite', autor='Embrapa', ano=2020,
        observacoes='Meta: 10% do peso ao nascer em volume. Ex: 40 kg → 4 litros.',
    ),
    dict(
        indicador='brix_colostro',
        descricao='Qualidade mínima do colostro (Brix)',
        valor_minimo=22.0, valor_ideal=25.0, unidade='%',
        populacao='Colostro bovino',
        fonte='Buczinski & Vandeweerd, 2016', autor='Buczinski, S.; Vandeweerd, J.M.', ano=2016,
        observacoes='Brix ≥ 22% indica boa qualidade (IgG ≥ 50 g/L). Abaixo de 20% é fraco.',
    ),
    dict(
        indicador='dias_secos',
        descricao='Período seco recomendado',
        valor_minimo=45.0, valor_ideal=60.0, valor_maximo=75.0, unidade='dias',
        populacao='Vacas leiteiras',
        fonte='Embrapa Gado de Leite', autor='Embrapa', ano=2020,
        observacoes='Período < 45 dias compromete produção na próxima lactação.',
    ),
    dict(
        indicador='dias_pre_parto',
        descricao='Período mínimo no lote pré-parto',
        valor_minimo=21.0, valor_ideal=21.0, unidade='dias',
        populacao='Vacas gestantes — transição',
        fonte='Embrapa / NRC 2001', autor='Embrapa / NRC', ano=2020,
        observacoes='Mínimo 21 dias para adaptação ruminal à dieta de transição.',
    ),
    dict(
        indicador='gmd_aleitamento',
        descricao='GMD desejado no aleitamento — Holandês',
        valor_minimo=0.7, valor_ideal=0.8, unidade='kg/dia',
        populacao='Terneiras Holandesas em aleitamento',
        fonte='Embrapa Gado de Leite', autor='Embrapa', ano=2020,
        observacoes='Aleitamento intensivo pode atingir 0,9–1,0 kg/dia.',
    ),
    dict(
        indicador='mortalidade_60d',
        descricao='Mortalidade aceitável até 60 dias',
        valor_ideal=2.0, valor_maximo=5.0, unidade='%',
        populacao='Terneiras leiteiras até 60 dias',
        fonte='USDA NAHMS Dairy Study', autor='USDA', ano=2014,
        observacoes='Mortalidade > 5% indica problema de manejo, colostragem ou sanidade.',
    ),
    dict(
        indicador='incidencia_diarreia',
        descricao='Incidência de diarreia aceitável',
        valor_ideal=15.0, valor_maximo=25.0, unidade='%',
        populacao='Terneiras leiteiras — fase neonatal',
        fonte='Embrapa Gado de Leite', autor='Embrapa', ano=2020,
        observacoes='> 25% indica necessidade de revisão dos protocolos.',
    ),
    dict(
        indicador='incidencia_pneumonia',
        descricao='Incidência de pneumonia aceitável',
        valor_ideal=10.0, valor_maximo=15.0, unidade='%',
        populacao='Terneiras leiteiras',
        fonte='Embrapa Gado de Leite', autor='Embrapa', ano=2020,
        observacoes='Principal causa de mortalidade após 30 dias. > 15% exige revisão.',
    ),
]


class Command(BaseCommand):
    help = 'Carrega referenciais técnicos iniciais (Embrapa e literatura)'

    def handle(self, *args, **options):
        criados = 0
        for dados in REFERENCIAIS:
            obj, created = ReferencialTecnico.objects.get_or_create(
                indicador=dados['indicador'],
                fonte=dados['fonte'],
                defaults=dados,
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'{criados} referenciais criados ({len(REFERENCIAIS) - criados} já existiam).'
        ))
