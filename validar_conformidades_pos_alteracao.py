#!/usr/bin/env python
"""
Script para validar que alterações no sistema não afetaram conformidades C1-C7.
Compara snapshot atual com snapshot_pre_fase2.json.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/home/victor/Documentos/victor/Documentos/TERNEIRAS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

from gerar_snapshot_pre_fase2 import capturar_conformidades_c1_c7, decimal_default
from core.models import Propriedade


def comparar_conformidades(antes, depois):
    """Compara dois snapshots de conformidades e retorna diferenças"""
    diferencas = []
    
    for codigo in antes.keys():
        if codigo not in depois:
            diferencas.append(f"❌ CRITÉRIO REMOVIDO: {codigo}")
            continue
            
        a = antes[codigo]
        d = depois[codigo]
        
        # Verificar totais
        if a['total_avaliacoes'] != d['total_avaliacoes']:
            diferencas.append(f"⚠️  {codigo}: Total mudou de {a['total_avaliacoes']} para {d['total_avaliacoes']}")
        
        # Verificar conformes
        if a['conforme'] != d['conforme']:
            diferencas.append(f"❌ {codigo}: Conformes mudaram de {a['conforme']} para {d['conforme']}")
        
        # Verificar não-conformes
        if a['nao_conforme'] != d['nao_conforme']:
            diferencas.append(f"❌ {codigo}: Não-conformes mudaram de {a['nao_conforme']} para {d['nao_conforme']}")
        
        # Verificar dados ausentes
        if a['dado_ausente'] != d['dado_ausente']:
            diferencas.append(f"❌ {codigo}: Dados ausentes mudaram de {a['dado_ausente']} para {d['dado_ausente']}")
    
    # Verificar critérios novos
    for codigo in depois.keys():
        if codigo not in antes:
            diferencas.append(f"➕ CRITÉRIO NOVO: {codigo} ({depois[codigo]['total_avaliacoes']} avaliações)")
    
    return diferencas


def main():
    """Função principal - valida conformidades"""
    
    print("🔍 Validando conformidades pós-alteração...")
    
    # Carregar snapshot de referência
    try:
        with open('snapshot_pre_fase2.json', 'r', encoding='utf-8') as f:
            snapshot_referencia = json.load(f)
        print("✅ Snapshot de referência carregado")
    except FileNotFoundError:
        print("❌ Erro: snapshot_pre_fase2.json não encontrado!")
        print("   Execute gerar_snapshot_pre_fase2.py primeiro")
        return False
    
    # Buscar propriedade
    try:
        propriedade_id = snapshot_referencia['metadata']['propriedade_id']
        propriedade = Propriedade.objects.get(id=propriedade_id, ativa=True)
        print(f"✅ Propriedade: {propriedade.nome} (ID: {propriedade.id})")
    except Propriedade.DoesNotExist:
        print(f"❌ Erro: Propriedade ID={propriedade_id} não encontrada")
        return False
    
    # Capturar conformidades atuais
    print("📋 Capturando conformidades atuais...")
    conformidades_atuais = capturar_conformidades_c1_c7(propriedade.id)
    
    # Comparar com referência
    print("🔍 Comparando com snapshot de referência...")
    conformidades_ref = snapshot_referencia['conformidades_c1_c7']
    
    # Extrair apenas resumos para comparação
    resumo_ref = {}
    for codigo, dados in conformidades_ref.items():
        resumo_ref[codigo] = {
            'total_avaliacoes': dados['total_avaliacoes'],
            'conforme': dados['conforme'],
            'nao_conforme': dados['nao_conforme'],
            'dado_ausente': dados['dado_ausente']
        }
    
    resumo_atual = {}
    for codigo, dados in conformidades_atuais.items():
        resumo_atual[codigo] = {
            'total_avaliacoes': dados['total_avaliacoes'],
            'conforme': dados['conforme'],
            'nao_conforme': dados['nao_conforme'],
            'dado_ausente': dados['dado_ausente']
        }
    
    diferencas = comparar_conformidades(resumo_ref, resumo_atual)
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE VALIDAÇÃO")
    print("="*60)
    
    if not diferencas:
        print("✅ SUCESSO: Nenhuma diferença encontrada nas conformidades C1-C7!")
        print("   As alterações não afetaram os indicadores existentes.")
        resultado = True
    else:
        print(f"❌ FALHAS: {len(diferencas)} diferença(s) encontrada(s):")
        print()
        for diferenca in diferencas:
            print(f"   {diferenca}")
        print()
        print("⚠️  AÇÃO NECESSÁRIA: Investigue as diferenças antes de prosseguir.")
        resultado = False
    
    print(f"\n📅 Validação executada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Referência: snapshot_pre_fase2.json ({snapshot_referencia['metadata']['data_geracao']})")
    
    return resultado


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)