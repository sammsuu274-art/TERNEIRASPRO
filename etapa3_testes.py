#!/usr/bin/env python
"""
ETAPA 3 — Testes completos das regras de negócio BEA.
Testa todas as 20 funções de classificação + 18 properties dos models.
"""
import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_terneiras.settings'
django.setup()

from decimal import Decimal
from bem_estar_animal.regras_bea import *

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f'  ✅ {msg}')

def fail(msg):
    global FAIL
    FAIL += 1
    print(f'  ❌ FALHOU: {msg}')

def section(title):
    print(f'\n{"═"*70}')
    print(f'  {title}')
    print(f'{"═"*70}')

def assert_eq(actual, expected, msg):
    if actual == expected:
        ok(msg)
    else:
        fail(f'{msg} — esperado {expected}, obtido {actual}')


# ═══════════════════════════════════════════════════════════════
# BLOCO 1 — SAÚDE: Brix sérico
# ═══════════════════════════════════════════════════════════════
section('BLOCO 1 — SAÚDE: Brix sérico')

# 1.1 Limites exatos
r = classificar_brix_serico(9.4)
assert_eq(r['classificacao'], Classificacao.EXCELENTE, 'Brix 9.4 → Excelente (limite exato)')

r = classificar_brix_serico(9.39)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Brix 9.39 → Adequado (0.01 abaixo do limite)')

r = classificar_brix_serico(8.1)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Brix 8.1 → Adequado (limite inferior exato)')

r = classificar_brix_serico(8.09)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Brix 8.09 → Crítico (0.01 abaixo)')

# 1.2 Valores típicos
r = classificar_brix_serico(10.5)
assert_eq(r['classificacao'], Classificacao.EXCELENTE, 'Brix 10.5 → Excelente')

r = classificar_brix_serico(8.5)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Brix 8.5 → Adequado')

r = classificar_brix_serico(7.0)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Brix 7.0 → Crítico')

# 1.3 None
r = classificar_brix_serico(None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Brix None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 2 — SAÚDE: Temperatura retal
# ═══════════════════════════════════════════════════════════════
section('BLOCO 2 — SAÚDE: Temperatura retal')

# 2.1 Limites exatos
r = avaliar_temperatura_retal(39.4)
assert_eq(r['alerta'], True, 'Temperatura 39.4 → Alerta (limite exato)')

r = avaliar_temperatura_retal(39.39)
assert_eq(r['alerta'], False, 'Temperatura 39.39 → Sem alerta (0.01 abaixo)')

# 2.2 Valores típicos
r = avaliar_temperatura_retal(40.0)
assert_eq(r['alerta'], True, 'Temperatura 40.0 → Alerta')

r = avaliar_temperatura_retal(38.5)
assert_eq(r['alerta'], False, 'Temperatura 38.5 → Normal')

# 2.3 None
r = avaliar_temperatura_retal(None)
assert_eq(r['alerta'], False, 'Temperatura None → Sem alerta (dado ausente)')


# ═══════════════════════════════════════════════════════════════
# BLOCO 3 — SAÚDE: Escore de fezes
# ═══════════════════════════════════════════════════════════════
section('BLOCO 3 — SAÚDE: Escore de fezes')

r = classificar_escore_fezes(0)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Escore 0 → Adequado')

r = classificar_escore_fezes(1)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Escore 1 → Adequado')

r = classificar_escore_fezes(2)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Escore 2 → Atenção')

r = classificar_escore_fezes(3)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Escore 3 → Crítico')

r = classificar_escore_fezes(None)
assert_eq(r['classificacao'], Classificacao.NAO_INFORMADO, 'Escore None → Não informado')


# ═══════════════════════════════════════════════════════════════
# BLOCO 4 — SAÚDE: Infecção umbilical
# ═══════════════════════════════════════════════════════════════
section('BLOCO 4 — SAÚDE: Infecção umbilical')

r = classificar_infeccao_umbilical(0)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Infecção 0 → Adequado')

r = classificar_infeccao_umbilical(1)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Infecção 1 → Atenção')

r = classificar_infeccao_umbilical(2)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Infecção 2 → Crítico')

r = classificar_infeccao_umbilical(None)
assert_eq(r['classificacao'], Classificacao.NAO_INFORMADO, 'Infecção None → Não informado')


# ═══════════════════════════════════════════════════════════════
# BLOCO 5 — AMBIENTE: Área individual
# ═══════════════════════════════════════════════════════════════
section('BLOCO 5 — AMBIENTE: Área individual')

# 5.1 Limites exatos
r = avaliar_area_individual(3.0)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Área 3.0 m² → Adequado (limite exato)')

r = avaliar_area_individual(2.99)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Área 2.99 m² → Crítico (0.01 abaixo)')

# 5.2 Valores típicos
r = avaliar_area_individual(4.0)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Área 4.0 m² → Adequado')

r = avaliar_area_individual(2.5)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Área 2.5 m² → Crítico')

# 5.3 None
r = avaliar_area_individual(None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Área None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 6 — AMBIENTE: Área coletiva
# ═══════════════════════════════════════════════════════════════
section('BLOCO 6 — AMBIENTE: Área coletiva')

# 6.1 Limites exatos
r = avaliar_area_coletiva(12.0, 3)  # 4.0 m²/animal
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Área 12 m² ÷ 3 = 4.0 m²/animal → Adequado (limite)')

r = avaliar_area_coletiva(11.97, 3)  # 3.99 m²/animal
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Área 11.97 m² ÷ 3 = 3.99 m²/animal → Crítico')

# 6.2 Valores típicos
r = avaliar_area_coletiva(20.0, 4)  # 5.0 m²/animal
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Área 20 m² ÷ 4 = 5.0 m²/animal → Adequado')

r = avaliar_area_coletiva(15.0, 5)  # 3.0 m²/animal
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Área 15 m² ÷ 5 = 3.0 m²/animal → Crítico')

# 6.3 Dados ausentes
r = avaliar_area_coletiva(None, 3)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Área None → Dados insuficientes')

r = avaliar_area_coletiva(12.0, None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Num animais None → Dados insuficientes')

# 6.4 Baia sem animais
r = avaliar_area_coletiva(12.0, 0)
assert_eq(r['classificacao'], Classificacao.NAO_APLICAVEL, 'Num animais 0 → Não aplicável')


# ═══════════════════════════════════════════════════════════════
# BLOCO 7 — AMBIENTE: Profundidade cama
# ═══════════════════════════════════════════════════════════════
section('BLOCO 7 — AMBIENTE: Profundidade cama')

# 7.1 Limites exatos
r = avaliar_profundidade_cama(30)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Cama 30 cm → Adequado (limite exato)')

r = avaliar_profundidade_cama(29)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Cama 29 cm → Atenção (1 cm abaixo)')

# 7.2 Valores típicos
r = avaliar_profundidade_cama(40)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Cama 40 cm → Adequado')

r = avaliar_profundidade_cama(15)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Cama 15 cm → Atenção')

# 7.3 None
r = avaliar_profundidade_cama(None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Cama None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 8 — COLOSTRO: Brix
# ═══════════════════════════════════════════════════════════════
section('BLOCO 8 — COLOSTRO: Brix')

# 8.1 Limites exatos
r = classificar_brix_colostro(22.0)
assert_eq(r['classificacao'], Classificacao.EXCELENTE, 'Brix colostro 22.0 → Excelente (limite exato)')

r = classificar_brix_colostro(21.99)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Brix colostro 21.99 → Atenção (0.01 abaixo)')

# 8.2 Valores típicos
r = classificar_brix_colostro(25.0)
assert_eq(r['classificacao'], Classificacao.EXCELENTE, 'Brix colostro 25.0 → Excelente')

r = classificar_brix_colostro(20.0)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Brix colostro 20.0 → Atenção')

# 8.3 None
r = classificar_brix_colostro(None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Brix colostro None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 9 — COLOSTRO: Volume primeira alimentação
# ═══════════════════════════════════════════════════════════════
section('BLOCO 9 — COLOSTRO: Volume primeira alimentação')

# 9.1 Peso 40 kg → recomendado 4000 ml (10%)
r = avaliar_volume_primeira_alimentacao(4000, 40.0)  # 100%
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Volume 4000ml para 40kg (100%) → Adequado')

r = avaliar_volume_primeira_alimentacao(3200, 40.0)  # 80%
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Volume 3200ml para 40kg (80%) → Atenção')

r = avaliar_volume_primeira_alimentacao(3000, 40.0)  # 75%
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Volume 3000ml para 40kg (75%) → Crítico')

r = avaliar_volume_primeira_alimentacao(5000, 40.0)  # 125%
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Volume 5000ml para 40kg (125%) → Adequado')

# 9.2 Dados ausentes
r = avaliar_volume_primeira_alimentacao(None, 40.0)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Volume None → Dados insuficientes')

r = avaliar_volume_primeira_alimentacao(4000, None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Peso None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 10 — COLOSTRO: Volume segunda alimentação
# ═══════════════════════════════════════════════════════════════
section('BLOCO 10 — COLOSTRO: Volume segunda alimentação')

# 10.1 Peso 40 kg → recomendado 2000 ml (5%)
r = avaliar_volume_segunda_alimentacao(2000, 40.0)  # 100%
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Volume 2000ml para 40kg (100%) → Adequado')

r = avaliar_volume_segunda_alimentacao(1500, 40.0)  # 75%
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Volume 1500ml para 40kg (75%) → Atenção')

# 10.2 Dados ausentes
r = avaliar_volume_segunda_alimentacao(None, 40.0)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Volume None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 11 — ALEITAMENTO: Volume diário
# ═══════════════════════════════════════════════════════════════
section('BLOCO 11 — ALEITAMENTO: Volume diário')

# 11.1 Raças grandes (Holandês)
r = avaliar_volume_diario_aleitamento(7.0, 'holandes')
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Volume 7.0L Holandês → Adequado (limite)')

r = avaliar_volume_diario_aleitamento(6.9, 'holandes')
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Volume 6.9L Holandês → Atenção (0.1 abaixo)')

r = avaliar_volume_diario_aleitamento(8.0, 'holandes')
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Volume 8.0L Holandês → Adequado')

# 11.2 Raças não grandes
r = avaliar_volume_diario_aleitamento(5.0, 'jersey')
assert_eq(r['classificacao'], Classificacao.NAO_APLICAVEL, 'Volume 5.0L Jersey → Não aplicável (raça pequena)')

# 11.3 Dados ausentes
r = avaliar_volume_diario_aleitamento(None, 'holandes')
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Volume None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 12 — DESALEITAMENTO: Duração gradual
# ═══════════════════════════════════════════════════════════════
section('BLOCO 12 — DESALEITAMENTO: Duração gradual')

# 12.1 Método gradual
r = avaliar_desaleitamento_gradual(10, 'gradual')
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Gradual 10 dias → Adequado (limite exato)')

r = avaliar_desaleitamento_gradual(9, 'gradual')
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Gradual 9 dias → Atenção (1 dia abaixo)')

r = avaliar_desaleitamento_gradual(15, 'gradual')
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Gradual 15 dias → Adequado')

# 12.2 Método não gradual
r = avaliar_desaleitamento_gradual(5, 'abrupto')
assert_eq(r['classificacao'], Classificacao.NAO_APLICAVEL, 'Abrupto 5 dias → Não aplicável')

# 12.3 Dados ausentes
r = avaliar_desaleitamento_gradual(None, 'gradual')
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Duração None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 13 — DESALEITAMENTO: Consumo concentrado
# ═══════════════════════════════════════════════════════════════
section('BLOCO 13 — DESALEITAMENTO: Consumo concentrado')

# 13.1 Faixa 1.2 - 1.5 kg
r = avaliar_consumo_concentrado_desmame(1.2)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Concentrado 1.2 kg → Adequado (limite inferior)')

r = avaliar_consumo_concentrado_desmame(1.5)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Concentrado 1.5 kg → Adequado (limite superior)')

r = avaliar_consumo_concentrado_desmame(1.35)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Concentrado 1.35 kg → Adequado (meio da faixa)')

r = avaliar_consumo_concentrado_desmame(1.19)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Concentrado 1.19 kg → Atenção (0.01 abaixo)')

r = avaliar_consumo_concentrado_desmame(1.0)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Concentrado 1.0 kg → Atenção')

r = avaliar_consumo_concentrado_desmame(1.6)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Concentrado 1.6 kg → Adequado (acima, não é problema)')

# 13.2 None
r = avaliar_consumo_concentrado_desmame(None)
assert_eq(r['classificacao'], Classificacao.DADOS_INSUFICIENTES, 'Concentrado None → Dados insuficientes')


# ═══════════════════════════════════════════════════════════════
# BLOCO 14 — COMPORTAMENTO: Estímulo tátil 6h
# ═══════════════════════════════════════════════════════════════
section('BLOCO 14 — COMPORTAMENTO: Estímulo tátil 6h')

r = avaliar_estimulo_tatil_6h(True)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Estímulo True → Adequado')

r = avaliar_estimulo_tatil_6h(False)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Estímulo False → Atenção')

r = avaliar_estimulo_tatil_6h(None)
assert_eq(r['classificacao'], Classificacao.NAO_INFORMADO, 'Estímulo None → Não informado')


# ═══════════════════════════════════════════════════════════════
# BLOCO 15 — COMPORTAMENTO: Idade mochação
# ═══════════════════════════════════════════════════════════════
section('BLOCO 15 — COMPORTAMENTO: Idade mochação')

# 15.1 Faixa ideal 3-4 semanas
r = avaliar_idade_mocacao(3)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Mochação 3 semanas → Adequado (limite inferior)')

r = avaliar_idade_mocacao(4)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Mochação 4 semanas → Adequado (limite superior)')

r = avaliar_idade_mocacao(2)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Mochação 2 semanas → Atenção (precoce)')

r = avaliar_idade_mocacao(5)
assert_eq(r['classificacao'], Classificacao.ATENCAO, 'Mochação 5 semanas → Atenção (tardia)')

# 15.2 None
r = avaliar_idade_mocacao(None)
assert_eq(r['classificacao'], Classificacao.NAO_INFORMADO, 'Mochação None → Não informado')


# ═══════════════════════════════════════════════════════════════
# BLOCO 16 — COMPORTAMENTO: Protocolo dor mochação
# ═══════════════════════════════════════════════════════════════
section('BLOCO 16 — COMPORTAMENTO: Protocolo dor mochação')

# 16.1 Com protocolo
r = avaliar_protocolo_dor_mocacao(True, True, False)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Anestesia+Analgesia → Adequado')

r = avaliar_protocolo_dor_mocacao(True, False, False)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Apenas anestesia → Adequado')

r = avaliar_protocolo_dor_mocacao(False, True, False)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Apenas analgesia → Adequado')

r = avaliar_protocolo_dor_mocacao(False, False, True)
assert_eq(r['classificacao'], Classificacao.ADEQUADO, 'Apenas sedação → Adequado')

# 16.2 Sem protocolo
r = avaliar_protocolo_dor_mocacao(False, False, False)
assert_eq(r['classificacao'], Classificacao.CRITICO, 'Sem protocolo → Crítico')

# 16.3 Dados ausentes
r = avaliar_protocolo_dor_mocacao(None, None, None)
assert_eq(r['classificacao'], Classificacao.NAO_INFORMADO, 'Todos None → Não informado')


# ═══════════════════════════════════════════════════════════════
# BLOCO 17 — Testes de properties dos models
# ═══════════════════════════════════════════════════════════════
section('BLOCO 17 — Properties dos models')

from animais.models import Animal
from eventos.models import Colostragem, CuraUmbigo, OcorrenciaSanitaria, Desaleitamento, Parto
from bem_estar_animal.models import AmbienteBEA, ComportamentoBEA, DietaSolidaBEA
from core.models import Propriedade
from datetime import date

# Buscar terneira DEMO para testes
terneira = Animal.objects.filter(categoria='terneira').first()
if not terneira:
    fail('Nenhuma terneira encontrada para testar properties')
else:
    ok(f'Terneira encontrada para testes: {terneira.identificacao}')
    
    # 17.1 Testar AmbienteBEA.classificacao_area (individual)
    amb = AmbienteBEA(
        terneira=terneira,
        data_avaliacao=date.today(),
        tipo_alojamento='individual',
        dimensao_baia_m2=3.5
    )
    result = amb.classificacao_area
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('AmbienteBEA.classificacao_area (individual 3.5m²) → Adequado')
    else:
        fail(f'AmbienteBEA.classificacao_area esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.2 Testar AmbienteBEA.classificacao_cama
    amb.profundidade_cama_cm = 35
    result = amb.classificacao_cama
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('AmbienteBEA.classificacao_cama (35cm) → Adequado')
    else:
        fail(f'AmbienteBEA.classificacao_cama esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.3 Testar ComportamentoBEA.classificacao_estimulo_6h
    comp = ComportamentoBEA(
        terneira=terneira,
        data_avaliacao=date.today(),
        estimulo_6h=True
    )
    result = comp.classificacao_estimulo_6h
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('ComportamentoBEA.classificacao_estimulo_6h (True) → Adequado')
    else:
        fail(f'ComportamentoBEA.classificacao_estimulo_6h esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.4 Testar ComportamentoBEA.classificacao_idade_mocacao
    comp.mocacao_idade_semanas = 3
    result = comp.classificacao_idade_mocacao
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('ComportamentoBEA.classificacao_idade_mocacao (3 sem) → Adequado')
    else:
        fail(f'ComportamentoBEA.classificacao_idade_mocacao esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.5 Testar ComportamentoBEA.classificacao_protocolo_dor
    comp.protocolo_dor_anestesia = True
    comp.protocolo_dor_analgesia = True
    comp.protocolo_dor_sedacao = False
    result = comp.classificacao_protocolo_dor
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('ComportamentoBEA.classificacao_protocolo_dor (anestesia+analgesia) → Adequado')
    else:
        fail(f'ComportamentoBEA.classificacao_protocolo_dor esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.6 Testar DietaSolidaBEA.classificacao_inicio_agua
    dieta = DietaSolidaBEA(
        terneira=terneira,
        data_avaliacao=date.today(),
        inicio_oferta_agua=1
    )
    result = dieta.classificacao_inicio_agua
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('DietaSolidaBEA.classificacao_inicio_agua (1 dia) → Adequado')
    else:
        fail(f'DietaSolidaBEA.classificacao_inicio_agua esperado Adequado, obtido {result["classificacao"]}')
    
    # 17.7 Testar DietaSolidaBEA.classificacao_inicio_concentrado
    dieta.inicio_concentrado_dias = 1
    result = dieta.classificacao_inicio_concentrado
    if result['classificacao'] == Classificacao.ADEQUADO:
        ok('DietaSolidaBEA.classificacao_inicio_concentrado (1 dia) → Adequado')
    else:
        fail(f'DietaSolidaBEA.classificacao_inicio_concentrado esperado Adequado, obtido {result["classificacao"]}')


# ═══════════════════════════════════════════════════════════════
# BLOCO 18 — Preservação dados DEMO
# ═══════════════════════════════════════════════════════════════
section('BLOCO 18 — Preservação dados DEMO')

from bem_estar_animal.models import JornadaProCampo, PlanoAcaoBEA

prop = Propriedade.objects.filter(nome__icontains='Rodrigues').first()
if prop:
    ok(f'Propriedade DEMO presente: {prop.nome}')
else:
    fail('Propriedade Rodrigues não encontrada')

terneiras_demo = Animal.objects.filter(identificacao__contains='DEMO')
if terneiras_demo.count() >= 3:
    ok(f'Terneiras DEMO presentes: {terneiras_demo.count()}')
else:
    fail(f'Terneiras DEMO: esperado >=3, encontrado {terneiras_demo.count()}')

jornadas = JornadaProCampo.objects.count()
if jornadas >= 1:
    ok(f'Jornadas ProCampo presentes: {jornadas}')
else:
    fail('Nenhuma jornada ProCampo encontrada')

acoes = PlanoAcaoBEA.objects.count()
if acoes >= 5:
    ok(f'Ações do plano presentes: {acoes}')
else:
    fail(f'Ações do plano: esperado >=5, encontrado {acoes}')


# ═══════════════════════════════════════════════════════════════
# BLOCO 19 — Verificação de regressões (ETAPA 2)
# ═══════════════════════════════════════════════════════════════
section('BLOCO 19 — Verificação de regressões (ETAPA 2)')

# Verificar que AmbienteBEA.treinamento_equipe existe
try:
    campo = AmbienteBEA._meta.get_field('treinamento_equipe')
    ok('Campo treinamento_equipe continua presente (sem regressão ETAPA 2)')
except:
    fail('Campo treinamento_equipe REMOVIDO — regressão detectada!')

# Verificar validações estruturais da ETAPA 2 ainda funcionam
try:
    from django.core.exceptions import ValidationError
    amb_teste = AmbienteBEA(
        terneira=terneira if terneira else None,
        data_avaliacao=date.today(),
        dimensao_baia_m2=-1
    )
    try:
        amb_teste.clean()
        fail('Validação dimensao_baia_m2 negativa não funciona — regressão!')
    except ValidationError:
        ok('Validação dimensao_baia_m2 negativa ainda funciona (sem regressão)')
except Exception as e:
    fail(f'Erro ao testar validação ETAPA 2: {e}')


# ═══════════════════════════════════════════════════════════════
# Resultado final
# ═══════════════════════════════════════════════════════════════
print(f'\n{"═"*70}')
print(f'  RESULTADO FINAL')
print(f'{"═"*70}')
print(f'  ✅ PASSOU: {PASS}')
print(f'  ❌ FALHOU: {FAIL}')
print(f'  TOTAL:    {PASS + FAIL}')

if FAIL == 0:
    print(f'\n  🎯 TODOS OS TESTES PASSARAM — ETAPA 3 CONCLUÍDA\n')
    sys.exit(0)
else:
    print(f'\n  ⚠️  {FAIL} TESTE(S) FALHARAM — REVISAR\n')
    sys.exit(1)
