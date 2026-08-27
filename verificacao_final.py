#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

from animais.models import Animal
from eventos.models import Parto, Colostragem, CuraUmbigo, Pesagem, OcorrenciaSanitaria, Vacinacao, Desaleitamento, BancoColostro
from programas.models import ProgramaAcompanhamento, CheckpointSesMeses
from config_tecnica.models import MetaReprodutiva
from indicadores.models import ResultadoConformidade

print("=" * 80)
print("VERIFICAÇÃO FINAL COMPLETA — TERNEIRASPRO")
print("=" * 80)

# 1. ANIMAIS
print("\n1. ANIMAIS CADASTRADOS:")
print("-" * 80)

terneiras = Animal.objects.filter(categoria='terneira')
vacas = Animal.objects.filter(categoria='vaca')

print(f"   Terneiras: {terneiras.count()}")
for t in terneiras:
    print(f"     • ID={t.id}: {t.identificacao} ({t.data_nascimento})")

print(f"\n   Vacas: {vacas.count()}")
for v in vacas:
    filhos = v.filhos.count()
    print(f"     • ID={v.id}: {v.identificacao} ({filhos} filha(s))")

# 2. PARTOS E PROGRAMAS
print("\n2. PARTOS E PROGRAMAS DE ACOMPANHAMENTO:")
print("-" * 80)

partos = Parto.objects.all()
print(f"   Partos: {partos.count()}")
for p in partos:
    prog = ProgramaAcompanhamento.objects.filter(terneira=p.terneira).first()
    print(f"     • Terneira {p.terneira.id}: {p.data_parto} | Programa: {prog.status if prog else 'NÃO'}")

# 3. EVENTOS
print("\n3. EVENTOS ZOOTÉCNICOS:")
print("-" * 80)

for t_id in [277, 292]:
    t = Animal.objects.get(id=t_id)
    print(f"\n   Terneira {t_id} ({t.identificacao}):")
    
    cols = Colostragem.objects.filter(terneira=t).count()
    curas = CuraUmbigo.objects.filter(terneira=t).count()
    pess = Pesagem.objects.filter(animal=t).count()
    ocors = OcorrenciaSanitaria.objects.filter(animal=t).count()
    vacs = Vacinacao.objects.filter(animal=t).count()
    desaleita = Desaleitamento.objects.filter(terneira=t).count()
    
    print(f"     - Colostragens: {cols}")
    print(f"     - Curas umbigo: {curas}")
    print(f"     - Pesagens: {pess}")
    print(f"     - Ocorrências: {ocors}")
    print(f"     - Vacinações: {vacs}")
    print(f"     - Desaleitamentos: {desaleita}")

# 4. BANCO DE COLOSTRO
print("\n4. BANCO DE COLOSTRO:")
print("-" * 80)

banco = BancoColostro.objects.all()
print(f"   Total de lotes: {banco.count()}")
total_vol = sum(b.volume_ml for b in banco)
print(f"   Volume total: {total_vol} ml")

# 5. CHECKPOINTS
print("\n5. CHECKPOINTS 6 MESES:")
print("-" * 80)

checkpoints = CheckpointSesMeses.objects.all()
print(f"   Total: {checkpoints.count()}")
for c in checkpoints:
    print(f"     • Terneira {c.programa.terneira.id}: {c.data_avaliacao} | Status: {c.status_checkpoint}")

# 6. CONFORMIDADES
print("\n6. CONFORMIDADES CALCULADAS:")
print("-" * 80)

for t_id in [277, 292]:
    confs = ResultadoConformidade.objects.filter(animal__id=t_id)
    confs_ok = confs.filter(resultado='conforme').count()
    confs_nao = confs.filter(resultado='nao_conforme').count()
    confs_ausente = confs.filter(resultado='dado_ausente').count()
    
    print(f"\n   Terneira {t_id}:")
    print(f"     - Total: {confs.count()}")
    print(f"     - Conformes: {confs_ok}")
    print(f"     - Não-conformes: {confs_nao}")
    print(f"     - Dado ausente: {confs_ausente}")

# 7. METAS REPRODUTIVAS
print("\n7. METAS REPRODUTIVAS (EMBRAPA):")
print("-" * 80)

metas = MetaReprodutiva.objects.all()
print(f"   Total de metas: {metas.count()}")
for m in metas:
    print(f"     • {m.nome}")
    print(f"       - Peso 1ª IA: {m.peso_minimo_kg} kg ({m.percentual_peso_adulto}% de {m.peso_adulto_medio_kg}kg)")
    print(f"       - Idade alvo: {m.idade_alvo_meses} meses")
    print(f"       - GMD mínimo: {m.gmd_minimo_recria} kg/dia")

# RESUMO FINAL
print("\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)

print(f"\n✅ Terneiras: {terneiras.count()} cadastradas")
print(f"✅ Vacas: {vacas.count()} cadastradas")
print(f"✅ Partos: {partos.count()} registrados")
print(f"✅ Colostragens: {Colostragem.objects.all().count()} registradas")
print(f"✅ Pesagens: {Pesagem.objects.all().count()} registradas")
print(f"✅ Desaleitamentos: {Desaleitamento.objects.all().count()} registrados")
print(f"✅ Checkpoints: {checkpoints.count()} realizados")
print(f"✅ Conformidades: {ResultadoConformidade.objects.all().count()} calculadas")
print(f"✅ Banco de colostro: {banco.count()} lotes")
print(f"✅ Metas reprodutivas: {metas.count()} (EMBRAPA)")

print("\n" + "=" * 80)
print("🎯 SISTEMA PRONTO PARA TESTES!")
print("=" * 80)
