#!/usr/bin/env python
"""
Script para gerar snapshot das conformidades C1-C7 antes da Fase 2.
Este arquivo será usado como referência para validar que futuras alterações
não alterem os valores das conformidades existentes.
"""

import os
import sys
import django
import json
from datetime import datetime
from decimal import Decimal

# Setup Django
sys.path.append('/home/victor/Documentos/victor/Documentos/TERNEIRAS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

from core.models import Propriedade
from indicadores.models import ResultadoConformidade
from indicadores.services import consolidar_dashboard


def decimal_default(obj):
    """Converter Decimal, datetime e date para formatos serializáveis no JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, 'isoformat'):  # datetime ou date
        return obj.isoformat()
    raise TypeError


def capturar_conformidades_c1_c7(propriedade_id):
    """Captura todos os resultados C1-C7 da propriedade"""
    
    codigos_c1_c7 = [
        'colostragem_tempo',      # C1
        'colostragem_volume_relativo', # C2
        'colostragem_brix',       # C3
        'umbigo_tempo',           # C4
        'dias_secos_minimo',      # C5a
        'dias_secos_maximo',      # C5b
        'dias_pre_parto_minimo',  # C6
    ]
    
    resultados = {}
    
    # Conformidades por critério específico
    # CORREÇÃO: Removido filtro criterio__ativo=True para incluir conformidades de critérios substituídos
    for codigo in codigos_c1_c7:
        conformidades = list(ResultadoConformidade.objects.filter(
            criterio__codigo=codigo,
            criterio__propriedade_id=propriedade_id,
            # criterio__ativo=True  # REMOVIDO - conformidades históricas são válidas
        ).values(
            'id', 'animal_id', 'criterio_id', 'data_evento',
            'evento_tipo', 'evento_id', 'valor_observado',
            'valor_referencia', 'desvio', 'resultado',
            'motivo_ausencia', 'observacoes'
        ))
        
        resultados[codigo] = {
            'total_avaliacoes': len(conformidades),
            'conforme': len([r for r in conformidades if r['resultado'] == 'conforme']),
            'nao_conforme': len([r for r in conformidades if r['resultado'] == 'nao_conforme']),
            'dado_ausente': len([r for r in conformidades if r['resultado'] == 'dado_ausente']),
            'avaliacoes': conformidades
        }
    
    # Conformidades por meta desenvolvimento (C7)
    # CORREÇÃO: Removido filtro meta_desenvolvimento__ativa=True
    conformidades_c7 = list(ResultadoConformidade.objects.filter(
        meta_desenvolvimento__propriedade_id=propriedade_id,
        # meta_desenvolvimento__ativa=True  # REMOVIDO - conformidades históricas são válidas
    ).values(
        'id', 'animal_id', 'meta_desenvolvimento_id', 'data_evento',
        'evento_tipo', 'evento_id', 'valor_observado',
        'valor_referencia', 'desvio', 'resultado',
        'motivo_ausencia', 'observacoes'
    ))
    
    resultados['meta_desenvolvimento_c7'] = {
        'total_avaliacoes': len(conformidades_c7),
        'conforme': len([r for r in conformidades_c7 if r['resultado'] == 'conforme']),
        'nao_conforme': len([r for r in conformidades_c7 if r['resultado'] == 'nao_conforme']),
        'dado_ausente': len([r for r in conformidades_c7 if r['resultado'] == 'dado_ausente']),
        'avaliacoes': conformidades_c7
    }
    
    return resultados


def main():
    """Função principal - gera o snapshot"""
    
    print("🔍 Gerando snapshot das conformidades pré-Fase 2...")
    
    # Buscar propriedade ativa (assumindo Fazenda Rodrigues ID=1)
    try:
        propriedade = Propriedade.objects.get(id=1, ativa=True)
        print(f"✅ Propriedade: {propriedade.nome} (ID: {propriedade.id})")
    except Propriedade.DoesNotExist:
        print("❌ Erro: Propriedade ID=1 não encontrada ou inativa")
        return
    
    # Capturar dashboard geral
    print("📊 Consolidando dashboard geral...")
    dashboard = consolidar_dashboard(propriedade.id, periodo_dias=180)  # 6 meses
    
    # Capturar conformidades C1-C7
    print("📋 Capturando conformidades C1-C7...")
    conformidades = capturar_conformidades_c1_c7(propriedade.id)
    
    # Montar snapshot completo
    snapshot = {
        'metadata': {
            'data_geracao': datetime.now().isoformat(),
            'propriedade_id': propriedade.id,
            'propriedade_nome': propriedade.nome,
            'objetivo': 'Snapshot pré-Fase 2 para validar que alterações futuras não quebram conformidades existentes',
            'fase_projeto': 'Pre-Fase-2-BEA'
        },
        'dashboard_geral': dashboard,
        'conformidades_c1_c7': conformidades,
        'resumo_conformidades': {}
    }
    
    # Calcular resumo
    resumo = {}
    for codigo, dados in conformidades.items():
        total = dados['total_avaliacoes']
        if total > 0:
            resumo[codigo] = {
                'total': total,
                'taxa_conformidade': round((dados['conforme'] / total) * 100, 2),
                'taxa_nao_conformidade': round((dados['nao_conforme'] / total) * 100, 2),
                'taxa_dado_ausente': round((dados['dado_ausente'] / total) * 100, 2)
            }
        else:
            resumo[codigo] = {'total': 0, 'taxa_conformidade': 0, 'taxa_nao_conformidade': 0, 'taxa_dado_ausente': 0}
    
    snapshot['resumo_conformidades'] = resumo
    
    # Salvar arquivo
    arquivo_snapshot = 'snapshot_pre_fase2.json'
    with open(arquivo_snapshot, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2, default=decimal_default)
    
    print(f"✅ Snapshot salvo em: {arquivo_snapshot}")
    
    # Relatório resumido
    print("\n📈 RESUMO DAS CONFORMIDADES:")
    print("-" * 50)
    for codigo, dados in resumo.items():
        if dados['total'] > 0:
            print(f"{codigo:25} | {dados['total']:3d} avaliações | {dados['taxa_conformidade']:5.1f}% conforme")
        else:
            print(f"{codigo:25} | {dados['total']:3d} avaliações | (sem dados)")
    
    print(f"\n📊 Dashboard Geral:")
    print(f"  - Terneiras ativas: {dashboard['terneiras_ativas']}")
    print(f"  - Nascimentos (180d): {dashboard['nascimentos_periodo']}")
    
    # Valores podem ser dicionários ou números - tratar apropriadamente
    mortalidade = dashboard['mortalidade']
    if isinstance(mortalidade, dict) and 'taxa' in mortalidade:
        print(f"  - Mortalidade: {mortalidade['taxa']:.1f}%")
    else:
        print(f"  - Mortalidade: {mortalidade}")
    
    colostragem = dashboard['taxa_colostragem_2h']
    if isinstance(colostragem, dict) and 'taxa' in colostragem:
        print(f"  - Colostragem 2h: {colostragem['taxa']:.1f}%")
    else:
        print(f"  - Colostragem 2h: {colostragem}")
    
    print(f"\n🎯 Snapshot concluído! Use este arquivo para validar que mudanças futuras")
    print(f"   não alterem os valores C1-C7 existentes.")


if __name__ == '__main__':
    main()