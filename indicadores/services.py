"""
Serviços de cálculo de indicadores zootécnicos.

Regras fundamentais:
- Dado ausente (None) nunca é tratado como zero.
- Todo indicador informa o denominador utilizado.
- Cálculos com menos de 5 animais são sinalizados como baixa confiabilidade.
"""

from datetime import timedelta, date
from decimal import Decimal
from typing import Optional


# ---------------------------------------------------------------------------
# CRESCIMENTO
# ---------------------------------------------------------------------------

def calcular_gmd(
    peso_inicial: Optional[float],
    peso_final: Optional[float],
    data_inicial: Optional[date],
    data_final: Optional[date],
) -> Optional[float]:
    """
    Retorna o Ganho Médio Diário em kg/dia.
    Retorna None se qualquer dado estiver ausente ou intervalo <= 0.
    """
    if any(v is None for v in [peso_inicial, peso_final, data_inicial, data_final]):
        return None
    dias = (data_final - data_inicial).days
    if dias <= 0:
        return None
    return round((float(peso_final) - float(peso_inicial)) / dias, 3)


def classificar_peso_vs_meta(
    peso_atual: Optional[float],
    peso_meta: Optional[float],
) -> dict:
    """
    Classifica o peso do animal em relação à meta.
    Retorna dict com status e percentual.
    """
    if peso_atual is None or peso_meta is None or float(peso_meta) == 0:
        return {'status': 'sem_meta', 'percentual': None, 'desvio_kg': None}

    percentual = round(float(peso_atual) / float(peso_meta) * 100, 1)
    desvio = round(float(peso_atual) - float(peso_meta), 2)

    if percentual >= 100:
        status = 'adequado'
    elif percentual >= 90:
        status = 'atencao'
    else:
        status = 'critico'

    return {'status': status, 'percentual': percentual, 'desvio_kg': desvio}


def interpolar_peso_na_idade(pesagens, idade_alvo_dias: int) -> Optional[float]:
    """
    Interpola o peso estimado em uma idade específica a partir das pesagens disponíveis.
    pesagens: lista de dicts {'data': date, 'peso_kg': float, 'data_nascimento': date}
    """
    if not pesagens:
        return None

    pontos = []
    for p in pesagens:
        if p.get('data_nascimento') and p.get('data') and p.get('peso_kg') is not None:
            idade = (p['data'] - p['data_nascimento']).days
            pontos.append((idade, float(p['peso_kg'])))

    pontos.sort(key=lambda x: x[0])

    if not pontos:
        return None

    # Exato
    for idade, peso in pontos:
        if idade == idade_alvo_dias:
            return round(peso, 2)

    # Interpolação linear
    for i in range(len(pontos) - 1):
        i0, p0 = pontos[i]
        i1, p1 = pontos[i + 1]
        if i0 <= idade_alvo_dias <= i1:
            frac = (idade_alvo_dias - i0) / (i1 - i0)
            return round(p0 + frac * (p1 - p0), 2)

    return None


def calcular_gmd_periodo(pesagens, dias_janela: int = 30) -> Optional[float]:
    """
    Calcula o GMD dos últimos N dias a partir da lista de pesagens.
    pesagens: lista de objetos Pesagem ordenados por data.
    """
    if not pesagens or len(pesagens) < 2:
        return None

    hoje = date.today()
    limite = hoje - timedelta(days=dias_janela)
    recentes = [p for p in pesagens if p.data >= limite]

    if len(recentes) < 2:
        # Usa as duas últimas pesagens se não há suficientes no período
        ultimas = sorted(pesagens, key=lambda p: p.data)[-2:]
        return calcular_gmd(
            float(ultimas[0].peso_kg), float(ultimas[-1].peso_kg),
            ultimas[0].data, ultimas[-1].data,
        )

    recentes = sorted(recentes, key=lambda p: p.data)
    return calcular_gmd(
        float(recentes[0].peso_kg), float(recentes[-1].peso_kg),
        recentes[0].data, recentes[-1].data,
    )


# ---------------------------------------------------------------------------
# COLOSTRAGEM
# ---------------------------------------------------------------------------

def calcular_tempo_colostragem_horas(hora_nascimento, hora_primeira_colostragem) -> Optional[float]:
    """Retorna o tempo em horas entre nascimento e primeira colostragem."""
    if hora_nascimento is None or hora_primeira_colostragem is None:
        return None
    delta = hora_primeira_colostragem - hora_nascimento
    horas = delta.total_seconds() / 3600
    return round(horas, 2)


def calcular_volume_meta_colostro(peso_nascimento_kg: Optional[float]) -> Optional[float]:
    """Meta de volume de colostro = 10% do peso ao nascer em litros."""
    if peso_nascimento_kg is None:
        return None
    return round(float(peso_nascimento_kg) * 0.10, 2)


# ---------------------------------------------------------------------------
# INDICADORES POPULACIONAIS (por lote ou propriedade)
# ---------------------------------------------------------------------------

def calcular_taxa_colostragem_2h(terneiras_com_dados) -> dict:
    """
    Calcula percentual de terneiras que receberam colostro em até 2h.
    Retorna: total, com_dados, dentro_meta, percentual, confiavel
    """
    total = len(terneiras_com_dados)
    dentro_meta = sum(1 for t in terneiras_com_dados if t.get('tempo_horas') is not None and t['tempo_horas'] <= 2.0)
    com_dados = sum(1 for t in terneiras_com_dados if t.get('tempo_horas') is not None)

    if com_dados == 0:
        return {'total': total, 'com_dados': 0, 'dentro_meta': 0, 'percentual': None, 'confiavel': False}

    percentual = round(dentro_meta / com_dados * 100, 1)
    return {
        'total': total,
        'com_dados': com_dados,
        'dentro_meta': dentro_meta,
        'percentual': percentual,
        'confiavel': com_dados >= 5,
    }


def calcular_incidencia(total_animais: int, animais_afetados: int) -> dict:
    """
    Calcula incidência de uma condição sanitária.
    Retorna percentual e flag de confiabilidade.
    """
    if total_animais == 0:
        return {'percentual': None, 'confiavel': False}
    percentual = round(animais_afetados / total_animais * 100, 1)
    return {'percentual': percentual, 'confiavel': total_animais >= 10}


def calcular_mortalidade(nascidos: int, mortes: int) -> dict:
    if nascidos == 0:
        return {'percentual': None, 'confiavel': False}
    percentual = round(mortes / nascidos * 100, 1)
    return {'percentual': percentual, 'confiavel': nascidos >= 10}


# ---------------------------------------------------------------------------
# PROJEÇÃO REPRODUTIVA
# ---------------------------------------------------------------------------

def projetar_data_reprodutiva(
    data_referencia: date,
    peso_atual: float,
    peso_alvo: float,
    gmd_projetado: float,
) -> Optional[date]:
    """
    Projeta a data em que o animal atingirá o peso alvo.
    Retorna None se gmd_projetado <= 0.
    """
    if gmd_projetado <= 0:
        return None
    if peso_atual >= peso_alvo:
        return data_referencia
    dias = (peso_alvo - peso_atual) / gmd_projetado
    return data_referencia + timedelta(days=round(dias))


def classificar_trajetoria(
    peso_atual: Optional[float],
    peso_alvo: Optional[float],
    gmd_recente: Optional[float],
    gmd_minimo_necessario: Optional[float],
    data_referencia: Optional[date],
    data_alvo: Optional[date],
) -> dict:
    """
    Classifica a trajetória de desenvolvimento.
    Retorna status e lista de motivos.
    """
    motivos = []

    if any(v is None for v in [peso_atual, peso_alvo, gmd_recente, data_referencia, data_alvo]):
        return {'status': 'insuficiente', 'motivos': ['Dados insuficientes para avaliação']}

    dias_restantes = (data_alvo - data_referencia).days
    if dias_restantes <= 0:
        return {'status': 'insuficiente', 'motivos': ['Data alvo no passado']}

    peso_projetado = peso_atual + (gmd_recente * dias_restantes)
    desvio = peso_projetado - peso_alvo
    percentual_desvio = desvio / peso_alvo * 100

    if desvio >= 0:
        status = 'favoravel'
        motivos.append(f'Peso projetado ({peso_projetado:.1f} kg) ≥ peso alvo ({peso_alvo:.1f} kg)')
    elif percentual_desvio >= -10:
        status = 'atencao'
        motivos.append(f'Peso projetado ({peso_projetado:.1f} kg) está {abs(desvio):.1f} kg abaixo do alvo')
        motivos.append('Ajuste no manejo nutricional pode reverter o quadro')
    else:
        status = 'desfavoravel'
        motivos.append(f'Peso projetado ({peso_projetado:.1f} kg) está {abs(desvio):.1f} kg abaixo do alvo')
        motivos.append(f'Desvio de {abs(percentual_desvio):.1f}% — avaliação técnica recomendada')

    if gmd_minimo_necessario and gmd_recente < gmd_minimo_necessario:
        motivos.append(
            f'GMD atual ({gmd_recente:.3f} kg/dia) abaixo do mínimo necessário ({gmd_minimo_necessario:.3f} kg/dia)'
        )

    return {'status': status, 'motivos': motivos}


# ---------------------------------------------------------------------------
# DASHBOARD — indicadores consolidados por propriedade
# ---------------------------------------------------------------------------

def consolidar_dashboard(propriedade_id: int, periodo_dias: int = 90) -> dict:
    """
    Consolida os principais indicadores da propriedade para o dashboard.
    Retorna um dicionário com todos os KPIs.
    """
    from animais.models import Animal
    from eventos.models import Parto, Colostragem, OcorrenciaSanitaria
    from programas.models import ProgramaAcompanhamento, CheckpointSesMeses
    from django.utils import timezone

    hoje = timezone.now().date()
    inicio_periodo = hoje - timedelta(days=periodo_dias)

    # Terneiras ativas
    terneiras_ativas = Animal.objects.filter(
        propriedade_id=propriedade_id,
        categoria='terneira',
        situacao='ativa',
    )

    # Nascimentos no período
    nascimentos_periodo = Parto.objects.filter(
        ciclo__vaca__propriedade_id=propriedade_id,
        data_parto__gte=inicio_periodo,
    )

    n_nascimentos = nascimentos_periodo.count()
    n_terneiras_ativas = terneiras_ativas.count()

    # Mortalidade no período
    mortes = Animal.objects.filter(
        propriedade_id=propriedade_id,
        categoria='terneira',
        situacao='morta',
        data_saida__gte=inicio_periodo,
    ).count()

    mort = calcular_mortalidade(n_nascimentos, mortes)

    # Colostragem até 2h no período
    colostragens_dados = []
    for parto in nascimentos_periodo.select_related('terneira'):
        primeira = Colostragem.objects.filter(
            terneira=parto.terneira
        ).order_by('data_hora').first()
        if primeira and parto.hora_nascimento_completa:
            from django.utils import timezone as tz
            hora_nasc = tz.make_aware(parto.hora_nascimento_completa) if parto.hora_nascimento_completa.tzinfo is None else parto.hora_nascimento_completa
            tempo = calcular_tempo_colostragem_horas(hora_nasc, primeira.data_hora)
            colostragens_dados.append({'tempo_horas': tempo})
        else:
            colostragens_dados.append({'tempo_horas': None})

    taxa_colostro = calcular_taxa_colostragem_2h(colostragens_dados)

    # Diarreia e pneumonia no período
    terneiras_ids = terneiras_ativas.values_list('id', flat=True)
    diarreia = OcorrenciaSanitaria.objects.filter(
        animal__in=terneiras_ids,
        tipo='diarreia',
        data_inicio__gte=inicio_periodo,
    ).values('animal').distinct().count()
    pneumonia = OcorrenciaSanitaria.objects.filter(
        animal__in=terneiras_ids,
        tipo='pneumonia',
        data_inicio__gte=inicio_periodo,
    ).values('animal').distinct().count()

    inc_diarreia = calcular_incidencia(n_terneiras_ativas, diarreia)
    inc_pneumonia = calcular_incidencia(n_terneiras_ativas, pneumonia)

    # Checkpoints pendentes e status
    programas_ativos = ProgramaAcompanhamento.objects.filter(
        terneira__propriedade_id=propriedade_id,
        status='em_andamento',
    )
    checkpoints_pendentes = sum(1 for p in programas_ativos if p.checkpoint_pendente)

    checkpoints_realizados = CheckpointSesMeses.objects.filter(
        programa__terneira__propriedade_id=propriedade_id,
    )
    trajetoria_favoravel = checkpoints_realizados.filter(status_trajetoria='favoravel').count()
    trajetoria_atencao = checkpoints_realizados.filter(status_trajetoria='atencao').count()
    trajetoria_desfavoravel = checkpoints_realizados.filter(status_trajetoria='desfavoravel').count()

    return {
        'periodo_dias': periodo_dias,
        'terneiras_ativas': n_terneiras_ativas,
        'nascimentos_periodo': n_nascimentos,
        'mortalidade': mort,
        'taxa_colostragem_2h': taxa_colostro,
        'incidencia_diarreia': inc_diarreia,
        'incidencia_pneumonia': inc_pneumonia,
        'checkpoints_pendentes': checkpoints_pendentes,
        'trajetoria_favoravel': trajetoria_favoravel,
        'trajetoria_atencao': trajetoria_atencao,
        'trajetoria_desfavoravel': trajetoria_desfavoravel,
    }
