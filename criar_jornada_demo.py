#!/usr/bin/env python
"""Criar jornada ProCampo DEMO com dados de teste"""
import os
import django
from datetime import datetime, date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

from django.utils import timezone
from animais.models import Animal
from core.models import Propriedade
from accounts.models import Usuario, UsuarioPerfil
from bem_estar_animal.models import (
    JornadaProCampo, VisitaPresencialBEA, PlanoAcaoBEA,
    ConsentimentoBEA, AmbienteBEA, ComportamentoBEA, DietaSolidaBEA
)

print('=== CRIAÇÃO DE JORNADA PROCAMPO DEMO ===\n')

# Buscar dados existentes
try:
    propriedade = Propriedade.objects.get(id=4)  # Rodrigues
    print(f'✓ Propriedade: {propriedade.nome}')
except Propriedade.DoesNotExist:
    print('✗ Propriedade não encontrada!')
    exit(1)

try:
    admin = Usuario.objects.get(id=1)  # admin
    print(f'✓ Supervisor (admin): {admin.username}')
except Usuario.DoesNotExist:
    print('✗ Admin não encontrado!')
    exit(1)

# Criar ou pegar um produtor
try:
    produtor = Usuario.objects.get(username='produtor_silva')
    print(f'✓ Produtor encontrado: {produtor.username}')
except Usuario.DoesNotExist:
    print('  Criando produtor...')
    produtor = Usuario.objects.create_user(
        username='produtor_silva',
        email='silva@rodrigues.com',
        password='senha123'
    )
    print(f'✓ Produtor criado: {produtor.username}')

# Verificar/criar perfis
perfil_admin, created = UsuarioPerfil.objects.get_or_create(
    usuario=admin,
    propriedade=propriedade,
    defaults={'papel': 'admin', 'ativo': True}
)
if created:
    print(f'✓ Perfil admin criado')
else:
    print(f'✓ Perfil admin já existe')

perfil_produtor, created = UsuarioPerfil.objects.get_or_create(
    usuario=produtor,
    propriedade=propriedade,
    defaults={'papel': 'produtor', 'ativo': True}
)
if created:
    print(f'✓ Perfil produtor criado')
else:
    print(f'✓ Perfil produtor já existe')

# Criar consentimento
consentimento, created = ConsentimentoBEA.objects.get_or_create(
    propriedade=propriedade,
    produtor=produtor,
    defaults={
        'consentimento_dados': True,
        'consentimento_imagem': True,
        'data_consentimento': timezone.now(),
        'responsavel_coleta': admin,
        'observacoes': 'Consentimento coletado para programa ProCampo 2026'
    }
)
if created:
    print(f'✓ Consentimento criado')
else:
    print(f'✓ Consentimento já existe')

# Criar jornada
jornada, created = JornadaProCampo.objects.get_or_create(
    propriedade=propriedade,
    data_inicio=date(2026, 9, 1),
    defaults={
        'nome': 'ProCampo 2026 - Fazenda Rodrigues',
        'supervisor': admin,
        'produtor': produtor,
        'data_selecao_produtor': date(2026, 8, 15),
        'data_prevista_conclusao': date(2027, 3, 1),  # 6 meses
        'status': 'em_andamento',
        'minimo_visitas': 3,
        'baseline_realizado': True,
        'consentimento': consentimento,
        'objetivo_principal': 'Melhorar os indicadores de bem-estar animal com foco em colostragem, instalações e manejo de doenças.'
    }
)

if created:
    print(f'\n✓ JORNADA CRIADA: {jornada.nome}')
else:
    print(f'\n✓ Jornada já existe: {jornada.nome}')

# Criar visita baseline
visita1, created = VisitaPresencialBEA.objects.get_or_create(
    propriedade=propriedade,
    jornada=jornada,
    data_visita=date(2026, 9, 1),
    defaults={
        'tipo_visita': 'baseline',
        'numero_visita': 1,
        'responsavel_tecnico': admin,
        'produtor_visitado': produtor,
        'observacoes_gerais': 'Visita inicial para diagnóstico baseline. Propriedade com 3 terneiras em diferentes fases.',
        'problemas_identificados': '''
1. Dimensão das baias individuais abaixo de 3m²
2. Profundidade da cama insuficiente (20cm, meta: ≥30cm)
3. Frequência de lavagem de bebedouros inadequada
4. Falta de protocolo de dor na mochação
5. Início tardio de oferta de água (7 dias, meta: 1º dia)
        ''',
        'acoes_recomendadas': '''
1. Ampliar baias para 3,5m² 
2. Aumentar profundidade da cama para 30-35cm
3. Estabelecer lavagem diária de bebedouros
4. Implementar protocolo anestesia+analgesia para mochação
5. Oferecer água desde o 1º dia de vida
        '''
    }
)

if created:
    print(f'✓ Visita 1 (Baseline) criada em {visita1.data_visita}')
else:
    print(f'✓ Visita 1 já existe')

# Criar ações do plano baseadas nos problemas
acoes_dados = [
    {
        'dominio': 'Ambiente',
        'indicador': 'Dimensão baias individuais',
        'situacao': 'Baias com 2,5m² (meta: ≥3m²)',
        'acao': 'Ampliar baias para 3,5m² cada',
        'prazo': date(2026, 10, 15),
        'prioridade': 'alta'
    },
    {
        'dominio': 'Ambiente',
        'indicador': 'Profundidade cama',
        'situacao': 'Cama com 20cm (meta: ≥30cm)',
        'acao': 'Aumentar volume de maravalha para 30-35cm',
        'prazo': date(2026, 9, 20),
        'prioridade': 'media'
    },
    {
        'dominio': 'Limpeza',
        'indicador': 'Frequência lavagem bebedouros',
        'situacao': 'Lavagem semanal',
        'acao': 'Estabelecer rotina de lavagem diária',
        'prazo': date(2026, 9, 10),
        'prioridade': 'alta'
    },
    {
        'dominio': 'Comportamento',
        'indicador': 'Protocolo dor mochação',
        'situacao': 'Sem protocolo de mitigação de dor',
        'acao': 'Implementar anestesia local + analgésico sistêmico',
        'prazo': date(2026, 10, 1),
        'prioridade': 'critica'
    },
    {
        'dominio': 'Água e Dieta Sólida',
        'indicador': 'Início oferta água',
        'situacao': 'Água oferecida apenas após 7 dias',
        'acao': 'Oferecer água fresca desde o 1º dia de vida',
        'prazo': date(2026, 9, 15),
        'prioridade': 'alta'
    },
]

for acao_dados in acoes_dados:
    acao, created = PlanoAcaoBEA.objects.get_or_create(
        jornada=jornada,
        indicador=acao_dados['indicador'],
        defaults={
            'visita_origem': visita1,
            'dominio': acao_dados['dominio'],
            'situacao_encontrada': acao_dados['situacao'],
            'acao_recomendada': acao_dados['acao'],
            'responsavel': produtor,
            'prazo': acao_dados['prazo'],
            'prioridade': acao_dados['prioridade'],
            'status': 'em_andamento'
        }
    )
    if created:
        print(f'  ✓ Ação criada: {acao.indicador}')

# Buscar terneiras para criar avaliações
terneiras = Animal.objects.filter(identificacao__contains='T0', categoria='terneira', propriedade=propriedade)
print(f'\n✓ Terneiras encontradas para avaliação: {terneiras.count()}')

for terneira in terneiras[:2]:  # Criar avaliação para 2 terneiras
    # Avaliação Ambiente
    amb, created = AmbienteBEA.objects.get_or_create(
        terneira=terneira,
        data_avaliacao=date(2026, 9, 1),
        defaults={
            'local_paricao': 'maternidade',
            'tipo_alojamento': 'individual',
            'fase_alojamento': 'bercario',
            'dimensao_baia_m2': Decimal('2.5'),
            'numero_animais_baia': 1,
            'tipo_cama': 'maravalha',
            'profundidade_cama_cm': 20,
            'score_sujidade': 'limpo',
            'tem_aquecimento': False,
            'cortinas_adequadas': True,
            'tem_sombra': True,
            'tem_ventilacao': False,
            'freq_lavagem_mamadeiras': 'apos_uso',
            'freq_lavagem_sondas': 'apos_uso',
            'freq_lavagem_bebedouros': 'semanal',
            'freq_lavagem_baldes': 'diaria',
            'freq_lavagem_cochos': 'diaria',
            'freq_desinfeccao_baias': 'semanal',
            'produto_higiene': 'Hipoclorito de sódio 2%',
            'tem_pop_elaborado': True,
            'limpeza_acida_semanal': True,
            'responsavel_avaliacao': admin,
            'observacoes': 'Baseline - Avaliação inicial'
        }
    )
    if created:
        print(f'  ✓ Avaliação Ambiente criada para {terneira.identificacao}')
    
    # Avaliação Comportamento
    comp, created = ComportamentoBEA.objects.get_or_create(
        terneira=terneira,
        data_avaliacao=date(2026, 9, 1),
        defaults={
            'estimulo_6h': True,
            'continuidade_diaria': True,
            'idade_agrupamento_dias': 45,
            'tipo_agrupamento': 'pares',
            'tem_enriquecimento': False,
            'tipo_enriquecimento': '',
            'mocacao_realizada': True,
            'mocacao_idade_semanas': 4,
            'mocacao_metodo': 'ferro_quente',
            'protocolo_dor_anestesia': False,
            'protocolo_dor_analgesia': False,
            'protocolo_dor_sedacao': False,
            'remocao_tetas_realizada': False,
            'responsavel_avaliacao': admin,
            'observacoes': 'Baseline - Mochação sem protocolo de dor (problema identificado)'
        }
    )
    if created:
        print(f'  ✓ Avaliação Comportamento criada para {terneira.identificacao}')
    
    # Avaliação Dieta Sólida
    dieta, created = DietaSolidaBEA.objects.get_or_create(
        terneira=terneira,
        jornada=jornada,
        data_avaliacao=date(2026, 9, 1),
        defaults={
            'inicio_oferta_agua': 7,
            'fonte_agua': 'Poço artesiano',
            'tipo_bebedouro': 'balde',
            'agua_fresca_disponivel': True,
            'inicio_concentrado_dias': 3,
            'tipo_racao': 'Iniciador 20% PB',
            'freq_abastecimento_concentrado': '2x_dia',
            'consumo_concentrado_estimado_kg': Decimal('0.8'),
            'inicio_volumoso_dias': 20,
            'tipo_volumoso': 'Feno coast-cross',
            'freq_abastecimento_volumoso': '1x_dia',
            'consumo_volumoso_estimado_kg': Decimal('0.3'),
            'responsavel_avaliacao': admin,
            'observacoes': 'Baseline - Água oferecida tardiamente (problema identificado)'
        }
    )
    if created:
        print(f'  ✓ Avaliação Dieta Sólida criada para {terneira.identificacao}')

print(f'\n=== JORNADA PROCAMPO DEMO CRIADA COM SUCESSO ===')
print(f'Jornada: {jornada.nome}')
print(f'Status: {jornada.get_status_display()}')
print(f'Visitas realizadas: {jornada.total_visitas}/{jornada.minimo_visitas}')
print(f'Ações no plano: {jornada.total_acoes_plano}')
print(f'Ações pendentes: {jornada.acoes_pendentes}')
print(f'Baseline realizado: {"Sim" if jornada.baseline_realizado else "Não"}')
