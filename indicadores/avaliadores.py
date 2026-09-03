"""
Avaliadores de conformidade.

Cada avaliador:
1. Recebe um evento (instância de model)
2. Busca os critérios vigentes para a propriedade na data do evento
3. Calcula o resultado
4. Persiste ResultadoConformidade

Regras:
- Dado ausente gera resultado 'dado_ausente', não erro.
- Nunca lança exceção — loga silenciosamente.
- Idempotente: se já existe resultado para o mesmo evento + critério, não recria.
"""

import logging
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from .models import ResultadoConformidade

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# UTILITÁRIOS INTERNOS
# ---------------------------------------------------------------------------

def _buscar_criterios(propriedade_id, codigo, data_evento, raca=None):
    """Critérios ativos e vigentes para a propriedade na data do evento."""
    from config_tecnica.models import CriterioConformidade

    qs = CriterioConformidade.objects.filter(
        propriedade_id=propriedade_id,
        codigo=codigo,
        ativo=True,
        vigencia_inicio__lte=data_evento,
    ).filter(
        Q(vigencia_fim__isnull=True) | Q(vigencia_fim__gte=data_evento)
    )
    if raca:
        qs = qs.filter(Q(escopo_raca='todas') | Q(escopo_raca=raca))
    return qs


def _ja_avaliado(animal_id, criterio_id, evento_tipo, evento_id):
    """
    Verifica se já existe avaliação para este animal+evento.
    
    MELHORIA: Também verifica por código do critério para evitar duplicatas
    quando critério é substituído (novo ID, mesmo código).
    """
    # Verificação original por critério específico
    if ResultadoConformidade.objects.filter(
        animal_id=animal_id,
        criterio_id=criterio_id,
        evento_tipo=evento_tipo,
        evento_id=evento_id,
    ).exists():
        return True
    
    # Verificação adicional por código do critério (evita duplicatas em substituições)
    try:
        from config_tecnica.models import CriterioConformidade
        criterio = CriterioConformidade.objects.get(id=criterio_id)
        
        return ResultadoConformidade.objects.filter(
            animal_id=animal_id,
            evento_tipo=evento_tipo,
            evento_id=evento_id,
            criterio__codigo=criterio.codigo,  # Mesmo código, qualquer ID
        ).exists()
    except:
        # Fallback para comportamento original se algo der errado
        return False


def _ja_avaliado_meta(animal_id, meta_id, evento_tipo, evento_id):
    return ResultadoConformidade.objects.filter(
        animal_id=animal_id,
        meta_desenvolvimento_id=meta_id,
        evento_tipo=evento_tipo,
        evento_id=evento_id,
    ).exists()


def _salvar(animal, criterio, meta_dev, data_evento, evento_tipo, evento_id,
            valor_obs, valor_ref, resultado, motivo_ausencia='', observacoes=''):
    desvio = None
    if valor_obs is not None and valor_ref is not None:
        desvio = round(float(valor_obs) - float(valor_ref), 3)

    ResultadoConformidade.objects.create(
        animal=animal,
        criterio=criterio,
        meta_desenvolvimento=meta_dev,
        data_evento=data_evento,
        evento_tipo=evento_tipo,
        evento_id=evento_id,
        valor_observado=Decimal(str(valor_obs)) if valor_obs is not None else None,
        valor_referencia=Decimal(str(valor_ref)) if valor_ref is not None else None,
        desvio=Decimal(str(desvio)) if desvio is not None else None,
        resultado=resultado,
        motivo_ausencia=motivo_ausencia,
        observacoes=observacoes,
    )


def _interpolar(pontos, idade_alvo, col=1):
    """Interpolação linear. pontos = [(idade_dias, val_min, val_ideal), ...]"""
    for p in pontos:
        if p[0] == idade_alvo:
            return float(p[col])
    for i in range(len(pontos) - 1):
        i0, i1 = pontos[i][0], pontos[i + 1][0]
        if i0 <= idade_alvo <= i1:
            frac = (idade_alvo - i0) / (i1 - i0)
            return round(float(pontos[i][col]) + frac * (float(pontos[i + 1][col]) - float(pontos[i][col])), 3)
    return None


# ---------------------------------------------------------------------------
# C5 — DIAS SECOS
# ---------------------------------------------------------------------------

def avaliar_dias_secos(parto):
    try:
        ciclo = parto.ciclo
        vaca = ciclo.vaca
        dias_secos = ciclo.dias_secos

        for codigo in ('dias_secos_minimo', 'dias_secos_maximo'):
            for criterio in _buscar_criterios(vaca.propriedade_id, codigo, parto.data_parto, vaca.raca):
                if _ja_avaliado(vaca.id, criterio.id, 'Parto', parto.id):
                    continue
                if dias_secos is None:
                    _salvar(
                        animal=vaca, criterio=criterio, meta_dev=None,
                        data_evento=parto.data_parto, evento_tipo='Parto', evento_id=parto.id,
                        valor_obs=None, valor_ref=float(criterio.valor_limite),
                        resultado='dado_ausente',
                        motivo_ausencia='Data de secagem não registrada no ciclo',
                    )
                    continue
                limite = float(criterio.valor_limite)
                conforme = dias_secos >= limite if codigo == 'dias_secos_minimo' else dias_secos <= limite
                _salvar(
                    animal=vaca, criterio=criterio, meta_dev=None,
                    data_evento=parto.data_parto, evento_tipo='Parto', evento_id=parto.id,
                    valor_obs=dias_secos, valor_ref=limite,
                    resultado='conforme' if conforme else 'nao_conforme',
                )
    except Exception as e:
        logger.error(f'avaliar_dias_secos parto {parto.pk}: {e}')


# ---------------------------------------------------------------------------
# C6 — DIAS NO PRÉ-PARTO
# ---------------------------------------------------------------------------

def avaliar_dias_pre_parto(parto):
    try:
        ciclo = parto.ciclo
        vaca = ciclo.vaca
        dias_pre = ciclo.dias_pre_parto

        for criterio in _buscar_criterios(vaca.propriedade_id, 'dias_pre_parto_minimo', parto.data_parto, vaca.raca):
            if _ja_avaliado(vaca.id, criterio.id, 'Parto', parto.id):
                continue
            if dias_pre is None:
                _salvar(
                    animal=vaca, criterio=criterio, meta_dev=None,
                    data_evento=parto.data_parto, evento_tipo='Parto', evento_id=parto.id,
                    valor_obs=None, valor_ref=float(criterio.valor_limite),
                    resultado='dado_ausente',
                    motivo_ausencia='Data de entrada no pré-parto não registrada',
                )
                continue
            conforme = dias_pre >= float(criterio.valor_limite)
            _salvar(
                animal=vaca, criterio=criterio, meta_dev=None,
                data_evento=parto.data_parto, evento_tipo='Parto', evento_id=parto.id,
                valor_obs=dias_pre, valor_ref=float(criterio.valor_limite),
                resultado='conforme' if conforme else 'nao_conforme',
            )
    except Exception as e:
        logger.error(f'avaliar_dias_pre_parto parto {parto.pk}: {e}')


# ---------------------------------------------------------------------------
# C1 — TEMPO ATÉ PRIMEIRA COLOSTRAGEM
# ---------------------------------------------------------------------------

def avaliar_tempo_colostragem(colostragem):
    try:
        from eventos.models import Colostragem as Col

        terneira = colostragem.terneira
        data_evento = colostragem.data_hora.date()

        primeira = Col.objects.filter(terneira=terneira).order_by('data_hora').first()
        if not primeira or primeira.pk != colostragem.pk:
            return

        for criterio in _buscar_criterios(terneira.propriedade_id, 'colostragem_tempo', data_evento, terneira.raca):
            if _ja_avaliado(terneira.id, criterio.id, 'Colostragem', colostragem.id):
                continue
            tempo = colostragem.tempo_apos_nascimento_horas
            if tempo is None:
                _salvar(
                    animal=terneira, criterio=criterio, meta_dev=None,
                    data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                    valor_obs=None, valor_ref=float(criterio.valor_limite),
                    resultado='dado_ausente',
                    motivo_ausencia='Hora do parto não registrada',
                )
                continue
            conforme = tempo <= float(criterio.valor_limite)
            _salvar(
                animal=terneira, criterio=criterio, meta_dev=None,
                data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                valor_obs=tempo, valor_ref=float(criterio.valor_limite),
                resultado='conforme' if conforme else 'nao_conforme',
            )
    except Exception as e:
        logger.error(f'avaliar_tempo_colostragem {colostragem.pk}: {e}')


# ---------------------------------------------------------------------------
# C2 — VOLUME DA PRIMEIRA COLOSTRAGEM
# ---------------------------------------------------------------------------

def avaliar_volume_colostragem(colostragem):
    try:
        from eventos.models import Colostragem as Col

        terneira = colostragem.terneira
        data_evento = colostragem.data_hora.date()

        primeira = Col.objects.filter(terneira=terneira).order_by('data_hora').first()
        if not primeira or primeira.pk != colostragem.pk:
            return

        for criterio in _buscar_criterios(terneira.propriedade_id, 'colostragem_volume_relativo', data_evento, terneira.raca):
            if _ja_avaliado(terneira.id, criterio.id, 'Colostragem', colostragem.id):
                continue
            try:
                peso_nasc_kg = float(terneira.parto_origem.peso_nascimento)
            except (AttributeError, TypeError):
                _salvar(
                    animal=terneira, criterio=criterio, meta_dev=None,
                    data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                    valor_obs=None, valor_ref=None,
                    resultado='dado_ausente',
                    motivo_ausencia='Peso ao nascer não registrado',
                )
                continue
            percentual = float(criterio.valor_limite)
            meta_ml = peso_nasc_kg * 1000 * (percentual / 100)
            fornecido_ml = float(colostragem.volume_ml)
            conforme = fornecido_ml >= meta_ml
            _salvar(
                animal=terneira, criterio=criterio, meta_dev=None,
                data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                valor_obs=fornecido_ml, valor_ref=round(meta_ml, 1),
                resultado='conforme' if conforme else 'nao_conforme',
                observacoes=f'Peso ao nascer: {peso_nasc_kg}kg | Meta {percentual}%PV = {round(meta_ml)}ml',
            )
    except Exception as e:
        logger.error(f'avaliar_volume_colostragem {colostragem.pk}: {e}')


# ---------------------------------------------------------------------------
# C3 — BRIX DO COLOSTRO
# ---------------------------------------------------------------------------

def avaliar_brix_colostragem(colostragem):
    try:
        terneira = colostragem.terneira
        data_evento = colostragem.data_hora.date()

        for criterio in _buscar_criterios(terneira.propriedade_id, 'colostragem_brix', data_evento, terneira.raca):
            if _ja_avaliado(terneira.id, criterio.id, 'Colostragem', colostragem.id):
                continue
            if colostragem.brix is None:
                _salvar(
                    animal=terneira, criterio=criterio, meta_dev=None,
                    data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                    valor_obs=None, valor_ref=float(criterio.valor_limite),
                    resultado='dado_ausente',
                    motivo_ausencia='Brix não medido nesta colostragem',
                )
                continue
            brix = float(colostragem.brix)
            limite = float(criterio.valor_limite)
            _salvar(
                animal=terneira, criterio=criterio, meta_dev=None,
                data_evento=data_evento, evento_tipo='Colostragem', evento_id=colostragem.id,
                valor_obs=brix, valor_ref=limite,
                resultado='conforme' if brix >= limite else 'nao_conforme',
            )
    except Exception as e:
        logger.error(f'avaliar_brix_colostragem {colostragem.pk}: {e}')


# ---------------------------------------------------------------------------
# C4 — TEMPO ATÉ PRIMEIRA CURA DE UMBIGO
# ---------------------------------------------------------------------------

def avaliar_tempo_umbigo(cura_umbigo):
    try:
        from eventos.models import CuraUmbigo as CU

        terneira = cura_umbigo.terneira
        data_evento = cura_umbigo.data_hora.date()

        primeira = CU.objects.filter(terneira=terneira).order_by('data_hora').first()
        if not primeira or primeira.pk != cura_umbigo.pk:
            return

        for criterio in _buscar_criterios(terneira.propriedade_id, 'umbigo_tempo', data_evento, terneira.raca):
            if _ja_avaliado(terneira.id, criterio.id, 'CuraUmbigo', cura_umbigo.id):
                continue
            try:
                hora_nasc = terneira.parto_origem.hora_nascimento_completa
                if hora_nasc is None:
                    raise ValueError('hora_parto ausente')
                hora_nasc_aware = timezone.make_aware(hora_nasc) if hora_nasc.tzinfo is None else hora_nasc
                tempo_horas = round((cura_umbigo.data_hora - hora_nasc_aware).total_seconds() / 3600, 2)
            except (AttributeError, ValueError):
                _salvar(
                    animal=terneira, criterio=criterio, meta_dev=None,
                    data_evento=data_evento, evento_tipo='CuraUmbigo', evento_id=cura_umbigo.id,
                    valor_obs=None, valor_ref=float(criterio.valor_limite),
                    resultado='dado_ausente',
                    motivo_ausencia='Hora do parto não registrada',
                )
                continue
            conforme = tempo_horas <= float(criterio.valor_limite)
            _salvar(
                animal=terneira, criterio=criterio, meta_dev=None,
                data_evento=data_evento, evento_tipo='CuraUmbigo', evento_id=cura_umbigo.id,
                valor_obs=tempo_horas, valor_ref=float(criterio.valor_limite),
                resultado='conforme' if conforme else 'nao_conforme',
            )
    except Exception as e:
        logger.error(f'avaliar_tempo_umbigo {cura_umbigo.pk}: {e}')


# ---------------------------------------------------------------------------
# C7 — PESO POR IDADE (vs. MetaDesenvolvimento)
# ---------------------------------------------------------------------------

def avaliar_peso_por_idade(pesagem):
    try:
        from config_tecnica.models import MetaDesenvolvimento, PontoMetaDesenvolvimento

        animal = pesagem.animal
        if not animal.data_nascimento:
            return

        data_evento = pesagem.data
        idade_dias = (data_evento - animal.data_nascimento).days
        if idade_dias <= 0:
            return

        metas = MetaDesenvolvimento.objects.filter(
            propriedade_id=animal.propriedade_id,
            ativa=True,
            vigencia_inicio__lte=data_evento,
        ).filter(
            Q(vigencia_fim__isnull=True) | Q(vigencia_fim__gte=data_evento)
        ).filter(
            Q(raca=animal.raca) | Q(raca='todas')
        )

        for meta in metas:
            if _ja_avaliado_meta(animal.id, meta.id, 'Pesagem', pesagem.id):
                continue

            pontos = list(
                PontoMetaDesenvolvimento.objects.filter(
                    meta=meta, tipo='peso'
                ).order_by('idade_dias').values_list('idade_dias', 'valor_minimo', 'valor_ideal')
            )
            if len(pontos) < 2:
                continue

            peso_min = _interpolar(pontos, idade_dias, col=1)
            peso_ideal = _interpolar(pontos, idade_dias, col=2)
            if peso_min is None:
                continue

            peso_atual = float(pesagem.peso_kg)
            obs = f'Idade: {idade_dias}d | Mín: {round(peso_min,1)}kg'
            if peso_ideal:
                obs += f' | Ideal: {round(peso_ideal,1)}kg'

            _salvar(
                animal=animal, criterio=None, meta_dev=meta,
                data_evento=data_evento, evento_tipo='Pesagem', evento_id=pesagem.id,
                valor_obs=peso_atual, valor_ref=round(peso_min, 2),
                resultado='conforme' if peso_atual >= peso_min else 'nao_conforme',
                observacoes=obs,
            )
    except Exception as e:
        logger.error(f'avaliar_peso_por_idade pesagem {pesagem.pk}: {e}')


# ---------------------------------------------------------------------------
# DISPATCHERS
# ---------------------------------------------------------------------------

def avaliar_evento_parto(parto):
    avaliar_dias_secos(parto)
    avaliar_dias_pre_parto(parto)


def avaliar_evento_colostragem(colostragem):
    avaliar_tempo_colostragem(colostragem)
    avaliar_volume_colostragem(colostragem)
    avaliar_brix_colostragem(colostragem)


def avaliar_evento_cura_umbigo(cura_umbigo):
    avaliar_tempo_umbigo(cura_umbigo)


def avaliar_evento_pesagem(pesagem):
    avaliar_peso_por_idade(pesagem)
