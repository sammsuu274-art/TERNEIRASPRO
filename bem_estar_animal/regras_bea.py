"""
Camada centralizada de regras de negócio e classificações de Bem-Estar Animal.

Baseado na Cartilha Bem-Estar em Ação — Jornada Bem-estar Animal em Ação.
Piracanjuba ProCampo — Apoio ao Produtor.

IMPORTANTE:
- Todas as classificações são calculadas a partir dos dados, não digitadas manualmente.
- Valores de referência vêm da cartilha oficial.
- Quando dados necessários estão ausentes, retorna None ou 'dados_insuficientes'.
- Não inventar resultados quando faltam informações.
"""

from typing import Optional, Tuple, Dict, Any
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════
# ENUMERAÇÕES DE CLASSIFICAÇÃO
# ═══════════════════════════════════════════════════════════════

class Classificacao:
    """Classificações padronizadas para indicadores BEA."""
    EXCELENTE = 'excelente'
    ADEQUADO = 'adequado'
    MEDIO = 'medio'
    ATENCAO = 'atencao'
    CRITICO = 'critico'
    DADOS_INSUFICIENTES = 'dados_insuficientes'
    NAO_INFORMADO = 'nao_informado'
    NAO_APLICAVEL = 'nao_aplicavel'


# ═══════════════════════════════════════════════════════════════
# DOMÍNIO 1 — SAÚDE
# ═══════════════════════════════════════════════════════════════

def classificar_brix_serico(brix: Optional[float]) -> Dict[str, Any]:
    """
    Classifica Brix sérico / Transferência de Imunidade Passiva (TIP).
    
    Referências da cartilha:
    - ≥ 9,4% → Excelente
    - 8,1% a < 9,4% → Adequado/Médio
    - < 8,1% → Falha/Insuficiente (Crítico)
    
    Args:
        brix: Valor do Brix sérico em % (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if brix is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 9,4% (Excelente), 8,1-9,4% (Adequado), < 8,1% (Falha)',
            'justificativa': 'Brix sérico não medido.',
        }
    
    if brix >= 9.4:
        return {
            'classificacao': Classificacao.EXCELENTE,
            'valor': f'{brix:.1f}%',
            'referencia': '≥ 9,4%',
            'justificativa': 'Transferência de imunidade passiva excelente.',
        }
    elif brix >= 8.1:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{brix:.1f}%',
            'referencia': '8,1% a 9,4%',
            'justificativa': 'Transferência de imunidade passiva adequada.',
        }
    else:
        return {
            'classificacao': Classificacao.CRITICO,
            'valor': f'{brix:.1f}%',
            'referencia': '< 8,1%',
            'justificativa': 'Falha na transferência de imunidade passiva (FTIP).',
        }


def avaliar_temperatura_retal(temperatura: Optional[float]) -> Dict[str, Any]:
    """
    Avalia temperatura retal como indicador de doença respiratória.
    
    Referência da cartilha:
    - ≥ 39,4°C → sinal compatível com doença respiratória
    
    IMPORTANTE: temperatura alta NÃO é diagnóstico definitivo isolado.
    É um indicador de alerta que deve ser avaliado junto com outros sinais.
    
    Args:
        temperatura: Temperatura retal em °C (pode ser None)
    
    Returns:
        Dict com 'alerta', 'valor', 'referencia', 'justificativa'
    """
    if temperatura is None:
        return {
            'alerta': False,
            'valor': None,
            'referencia': '≥ 39,4°C (alerta para doença respiratória)',
            'justificativa': 'Temperatura retal não medida.',
        }
    
    if temperatura >= 39.4:
        return {
            'alerta': True,
            'valor': f'{temperatura:.1f}°C',
            'referencia': '≥ 39,4°C',
            'justificativa': 'Temperatura elevada — sinal compatível com doença respiratória. Avaliar junto com escore respiratório.',
        }
    else:
        return {
            'alerta': False,
            'valor': f'{temperatura:.1f}°C',
            'referencia': '< 39,4°C',
            'justificativa': 'Temperatura dentro da faixa esperada.',
        }


def classificar_escore_fezes(escore: Optional[int]) -> Dict[str, Any]:
    """
    Classifica escore de fezes / diarreia.
    
    Referência da cartilha:
    - 0/1 → Normal
    - 2/3 → Diarreia
    
    Args:
        escore: Escore de fezes (0 a 3), pode ser None
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if escore is None:
        return {
            'classificacao': Classificacao.NAO_INFORMADO,
            'valor': None,
            'referencia': '0-1 (Normal), 2-3 (Diarreia)',
            'justificativa': 'Escore de fezes não informado.',
        }
    
    if escore in (0, 1):
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': escore,
            'referencia': '0-1',
            'justificativa': 'Fezes normais/firmes.',
        }
    elif escore in (2, 3):
        return {
            'classificacao': Classificacao.ATENCAO if escore == 2 else Classificacao.CRITICO,
            'valor': escore,
            'referencia': '2-3',
            'justificativa': f'Diarreia {"moderada" if escore == 2 else "severa"}.',
        }
    else:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': escore,
            'referencia': '0-3',
            'justificativa': f'Escore inválido ({escore}).',
        }


def classificar_infeccao_umbilical(escore: Optional[int]) -> Dict[str, Any]:
    """
    Classifica escore de infecção umbilical.
    
    Referência da cartilha:
    - 0 → Normal (sem infecção)
    - 1 → Infecção leve (atenção)
    - 2 → Infecção moderada/grave (crítico)
    
    Args:
        escore: Escore de infecção (0, 1 ou 2), pode ser None
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if escore is None:
        return {
            'classificacao': Classificacao.NAO_INFORMADO,
            'valor': None,
            'referencia': '0 (Normal), 1 (Leve), 2 (Moderada/Grave)',
            'justificativa': 'Escore de infecção umbilical não informado.',
        }
    
    if escore == 0:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': escore,
            'referencia': '0',
            'justificativa': 'Umbigo normal, sem sinais de infecção.',
        }
    elif escore == 1:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': escore,
            'referencia': '1',
            'justificativa': 'Infecção umbilical leve — monitorar.',
        }
    elif escore == 2:
        return {
            'classificacao': Classificacao.CRITICO,
            'valor': escore,
            'referencia': '2',
            'justificativa': 'Infecção umbilical moderada/grave — requer tratamento.',
        }
    else:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': escore,
            'referencia': '0-2',
            'justificativa': f'Escore inválido ({escore}).',
        }


# ═══════════════════════════════════════════════════════════════
# DOMÍNIO 2 — AMBIENTE
# ═══════════════════════════════════════════════════════════════

def avaliar_area_individual(area_m2: Optional[float]) -> Dict[str, Any]:
    """
    Avalia área de baia para alojamento individual.
    
    Referência da cartilha:
    - ≥ 3 m²/animal → Adequado
    
    Args:
        area_m2: Área da baia em m² (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if area_m2 is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 3 m²',
            'justificativa': 'Dimensão da baia não informada.',
        }
    
    if area_m2 >= 3.0:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{area_m2:.1f} m²',
            'referencia': '≥ 3 m²',
            'justificativa': 'Área adequada para alojamento individual.',
        }
    else:
        return {
            'classificacao': Classificacao.CRITICO,
            'valor': f'{area_m2:.1f} m²',
            'referencia': '< 3 m²',
            'justificativa': 'Área insuficiente — aumentar espaço.',
        }


def avaliar_area_coletiva(area_m2: Optional[float], numero_animais: Optional[int]) -> Dict[str, Any]:
    """
    Avalia área de baia para alojamento coletivo.
    
    Referência da cartilha:
    - ≥ 4 m²/animal → Adequado
    
    Args:
        area_m2: Área total da baia em m² (pode ser None)
        numero_animais: Número de animais na baia (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if area_m2 is None or numero_animais is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 4 m²/animal',
            'justificativa': 'Dados insuficientes (área ou número de animais não informados).',
        }
    
    if numero_animais == 0:
        return {
            'classificacao': Classificacao.NAO_APLICAVEL,
            'valor': None,
            'referencia': '≥ 4 m²/animal',
            'justificativa': 'Baia sem animais.',
        }
    
    area_por_animal = float(area_m2) / numero_animais
    
    if area_por_animal >= 4.0:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{area_por_animal:.1f} m²/animal ({area_m2:.1f} m² ÷ {numero_animais} animais)',
            'referencia': '≥ 4 m²/animal',
            'justificativa': 'Área adequada para alojamento coletivo.',
        }
    else:
        return {
            'classificacao': Classificacao.CRITICO,
            'valor': f'{area_por_animal:.1f} m²/animal ({area_m2:.1f} m² ÷ {numero_animais} animais)',
            'referencia': '< 4 m²/animal',
            'justificativa': 'Área insuficiente — reduzir número de animais ou aumentar espaço.',
        }


def avaliar_profundidade_cama(profundidade_cm: Optional[int]) -> Dict[str, Any]:
    """
    Avalia profundidade da cama.
    
    Referência da cartilha:
    - ≥ 30 cm → Adequado
    
    Args:
        profundidade_cm: Profundidade da cama em cm (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if profundidade_cm is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 30 cm',
            'justificativa': 'Profundidade da cama não informada.',
        }
    
    if profundidade_cm >= 30:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{profundidade_cm} cm',
            'referencia': '≥ 30 cm',
            'justificativa': 'Profundidade adequada para conforto.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{profundidade_cm} cm',
            'referencia': '< 30 cm',
            'justificativa': 'Cama rasa — aumentar profundidade.',
        }


# ═══════════════════════════════════════════════════════════════
# DOMÍNIO 4 — COLOSTRAGEM
# ═══════════════════════════════════════════════════════════════

def classificar_brix_colostro(brix: Optional[float]) -> Dict[str, Any]:
    """
    Classifica Brix do colostro fresco.
    
    Referência da cartilha:
    - ≥ 22° Brix → Excelente
    
    Args:
        brix: Valor do Brix do colostro em % (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if brix is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 22° Brix',
            'justificativa': 'Brix do colostro não medido.',
        }
    
    if brix >= 22.0:
        return {
            'classificacao': Classificacao.EXCELENTE,
            'valor': f'{brix:.1f}° Brix',
            'referencia': '≥ 22° Brix',
            'justificativa': 'Colostro de excelente qualidade.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{brix:.1f}° Brix',
            'referencia': '< 22° Brix',
            'justificativa': 'Qualidade do colostro abaixo do ideal.',
        }


def avaliar_volume_primeira_alimentacao(volume_ml: Optional[int], peso_kg: Optional[float]) -> Dict[str, Any]:
    """
    Avalia volume da primeira alimentação de colostro.
    
    Referência da cartilha:
    - 10% do peso corporal até 2 horas após o nascimento
    
    Args:
        volume_ml: Volume fornecido em ml (pode ser None)
        peso_kg: Peso da terneira em kg (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if volume_ml is None or peso_kg is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '10% do peso corporal',
            'justificativa': 'Dados insuficientes (volume ou peso não informados).',
        }
    
    # 1 kg = 1 litro = 1000 ml (densidade aproximada do colostro)
    # 10% do peso em kg → converter para ml
    volume_recomendado_ml = float(peso_kg) * 100  # 10% do peso em ml
    percentual_fornecido = (float(volume_ml) / volume_recomendado_ml) * 100
    
    if percentual_fornecido >= 100:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{volume_ml} ml ({percentual_fornecido:.0f}% do recomendado)',
            'referencia': f'{volume_recomendado_ml:.0f} ml (10% de {peso_kg:.1f} kg)',
            'justificativa': 'Volume adequado para primeira alimentação.',
        }
    elif percentual_fornecido >= 80:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{volume_ml} ml ({percentual_fornecido:.0f}% do recomendado)',
            'referencia': f'{volume_recomendado_ml:.0f} ml (10% de {peso_kg:.1f} kg)',
            'justificativa': 'Volume ligeiramente abaixo do recomendado.',
        }
    else:
        return {
            'classificacao': Classificacao.CRITICO,
            'valor': f'{volume_ml} ml ({percentual_fornecido:.0f}% do recomendado)',
            'referencia': f'{volume_recomendado_ml:.0f} ml (10% de {peso_kg:.1f} kg)',
            'justificativa': 'Volume insuficiente — aumentar fornecimento.',
        }


def avaliar_volume_segunda_alimentacao(volume_ml: Optional[int], peso_kg: Optional[float]) -> Dict[str, Any]:
    """
    Avalia volume da segunda alimentação de colostro.
    
    Referência da cartilha:
    - Adicional de 5% do peso até 12 horas
    
    Args:
        volume_ml: Volume fornecido em ml (pode ser None)
        peso_kg: Peso da terneira em kg (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if volume_ml is None or peso_kg is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '5% do peso corporal (adicional)',
            'justificativa': 'Dados insuficientes (volume ou peso não informados).',
        }
    
    # 5% do peso em ml
    volume_recomendado_ml = float(peso_kg) * 50
    percentual_fornecido = (float(volume_ml) / volume_recomendado_ml) * 100
    
    if percentual_fornecido >= 100:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{volume_ml} ml ({percentual_fornecido:.0f}% do recomendado)',
            'referencia': f'{volume_recomendado_ml:.0f} ml (5% de {peso_kg:.1f} kg)',
            'justificativa': 'Volume adequado para segunda alimentação.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{volume_ml} ml ({percentual_fornecido:.0f}% do recomendado)',
            'referencia': f'{volume_recomendado_ml:.0f} ml (5% de {peso_kg:.1f} kg)',
            'justificativa': 'Volume abaixo do recomendado.',
        }


# ═══════════════════════════════════════════════════════════════
# DOMÍNIO 5 — ALEITAMENTO E DIETA SÓLIDA
# ═══════════════════════════════════════════════════════════════

def avaliar_volume_diario_aleitamento(volume_litros: Optional[float], raca: Optional[str] = None) -> Dict[str, Any]:
    """
    Avalia volume diário de leite/sucedâneo para terneiras 0-30 dias.
    
    Referência da cartilha:
    - Grandes raças: ≥ 7 L/dia
    
    Args:
        volume_litros: Volume diário em litros (pode ser None)
        raca: Raça da terneira (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if volume_litros is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 7 L/dia (grandes raças)',
            'justificativa': 'Volume diário não informado.',
        }
    
    # Raças grandes: Holandês, Pardo Suíço, Girolando
    racas_grandes = ['holandes', 'pardo_suico', 'girolando']
    eh_raca_grande = raca and raca.lower() in racas_grandes
    
    if eh_raca_grande:
        if volume_litros >= 7.0:
            return {
                'classificacao': Classificacao.ADEQUADO,
                'valor': f'{volume_litros:.1f} L/dia',
                'referencia': '≥ 7 L/dia',
                'justificativa': 'Volume adequado para raca de grande porte.',
            }
        else:
            return {
                'classificacao': Classificacao.ATENCAO,
                'valor': f'{volume_litros:.1f} L/dia',
                'referencia': '< 7 L/dia',
                'justificativa': 'Volume abaixo do recomendado para raca de grande porte.',
            }
    else:
        # Para raças não identificadas ou pequenas, apenas informa o valor sem classificar
        return {
            'classificacao': Classificacao.NAO_APLICAVEL,
            'valor': f'{volume_litros:.1f} L/dia',
            'referencia': '≥ 7 L/dia (grandes raças)',
            'justificativa': 'Referência de 7 L/dia aplica-se a grandes raças. Raça não identificada ou porte diferente.',
        }


def avaliar_desaleitamento_gradual(duracao_dias: Optional[int], metodo: Optional[str] = None) -> Dict[str, Any]:
    """
    Avalia duração do desaleitamento gradual.
    
    Referência da cartilha:
    - ≥ 10 dias para desaleitamento gradual
    
    Args:
        duracao_dias: Duração em dias (pode ser None)
        metodo: Método de desaleitamento (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if metodo and metodo != 'gradual':
        return {
            'classificacao': Classificacao.NAO_APLICAVEL,
            'valor': metodo,
            'referencia': '≥ 10 dias (gradual)',
            'justificativa': f'Método {metodo} — referência de 10 dias aplica-se apenas ao gradual.',
        }
    
    if duracao_dias is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '≥ 10 dias',
            'justificativa': 'Duração do desaleitamento gradual não informada.',
        }
    
    if duracao_dias >= 10:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{duracao_dias} dias',
            'referencia': '≥ 10 dias',
            'justificativa': 'Desaleitamento gradual com duração adequada.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{duracao_dias} dias',
            'referencia': '< 10 dias',
            'justificativa': 'Desaleitamento gradual muito rápido — aumentar duração.',
        }


def avaliar_consumo_concentrado_desmame(consumo_kg: Optional[float]) -> Dict[str, Any]:
    """
    Avalia consumo de concentrado no momento do desmame.
    
    Referência da cartilha:
    - 1,2 a 1,5 kg/dia
    
    Args:
        consumo_kg: Consumo em kg/dia (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if consumo_kg is None:
        return {
            'classificacao': Classificacao.DADOS_INSUFICIENTES,
            'valor': None,
            'referencia': '1,2 a 1,5 kg/dia',
            'justificativa': 'Consumo de concentrado não informado.',
        }
    
    if 1.2 <= consumo_kg <= 1.5:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{consumo_kg:.2f} kg/dia',
            'referencia': '1,2 a 1,5 kg/dia',
            'justificativa': 'Consumo dentro da faixa recomendada.',
        }
    elif consumo_kg < 1.2:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{consumo_kg:.2f} kg/dia',
            'referencia': '< 1,2 kg/dia',
            'justificativa': 'Consumo abaixo do recomendado — terneira pode não estar pronta para desmamar.',
        }
    else:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{consumo_kg:.2f} kg/dia',
            'referencia': '> 1,5 kg/dia',
            'justificativa': 'Consumo acima da faixa típica (não é problema).',
        }


# ═══════════════════════════════════════════════════════════════
# DOMÍNIO 6 — COMPORTAMENTO
# ═══════════════════════════════════════════════════════════════

def avaliar_estimulo_tatil_6h(realizado: Optional[bool]) -> Dict[str, Any]:
    """
    Avalia se estímulo tátil foi realizado nas primeiras 6 horas.
    
    Referência da cartilha:
    - Estímulo tátil dentro das primeiras 6 horas de vida
    
    Args:
        realizado: Se foi realizado (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if realizado is None:
        return {
            'classificacao': Classificacao.NAO_INFORMADO,
            'valor': None,
            'referencia': 'Sim (dentro das primeiras 6h)',
            'justificativa': 'Informação não registrada.',
        }
    
    if realizado:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': 'Sim',
            'referencia': 'Sim',
            'justificativa': 'Estímulo tátil realizado conforme recomendação.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': 'Não',
            'referencia': 'Sim',
            'justificativa': 'Estímulo tátil não realizado nas primeiras 6h.',
        }


def avaliar_idade_mocacao(idade_semanas: Optional[int]) -> Dict[str, Any]:
    """
    Avalia idade na mochação.
    
    Referência da cartilha:
    - Ideal: 3 a 4 semanas
    
    Args:
        idade_semanas: Idade em semanas (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'valor', 'referencia', 'justificativa'
    """
    if idade_semanas is None:
        return {
            'classificacao': Classificacao.NAO_INFORMADO,
            'valor': None,
            'referencia': '3 a 4 semanas',
            'justificativa': 'Idade na mochação não informada.',
        }
    
    if 3 <= idade_semanas <= 4:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'valor': f'{idade_semanas} semanas',
            'referencia': '3 a 4 semanas',
            'justificativa': 'Mochação realizada na idade ideal.',
        }
    elif idade_semanas < 3:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{idade_semanas} semanas',
            'referencia': '< 3 semanas',
            'justificativa': 'Mochação precoce.',
        }
    else:
        return {
            'classificacao': Classificacao.ATENCAO,
            'valor': f'{idade_semanas} semanas',
            'referencia': '> 4 semanas',
            'justificativa': 'Mochação tardia.',
        }


def avaliar_protocolo_dor_mocacao(
    anestesia: Optional[bool],
    analgesia: Optional[bool],
    sedacao: Optional[bool]
) -> Dict[str, Any]:
    """
    Avalia presença de protocolo de controle da dor na mochação.
    
    Referência da cartilha:
    - Registrar protocolo de controle da dor
    
    Args:
        anestesia: Se foi aplicada anestesia (pode ser None)
        analgesia: Se foi aplicada analgesia (pode ser None)
        sedacao: Se foi aplicada sedação (pode ser None)
    
    Returns:
        Dict com 'classificacao', 'componentes', 'referencia', 'justificativa'
    """
    if anestesia is None and analgesia is None and sedacao is None:
        return {
            'classificacao': Classificacao.NAO_INFORMADO,
            'componentes': None,
            'referencia': 'Anestesia e/ou analgesia',
            'justificativa': 'Protocolo de dor não informado.',
        }
    
    componentes = []
    if anestesia:
        componentes.append('anestesia')
    if analgesia:
        componentes.append('analgesia')
    if sedacao:
        componentes.append('sedação')
    
    if componentes:
        return {
            'classificacao': Classificacao.ADEQUADO,
            'componentes': ', '.join(componentes),
            'referencia': 'Anestesia e/ou analgesia',
            'justificativa': f'Protocolo de dor registrado ({", ".join(componentes)}).',
        }
    else:
        return {
            'classificacao': Classificacao.CRITICO,
            'componentes': 'Nenhum',
            'referencia': 'Anestesia e/ou analgesia',
            'justificativa': 'Mochação sem protocolo de controle da dor.',
        }
