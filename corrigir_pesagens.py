import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

import datetime
from decimal import Decimal
from animais.models import Animal
from eventos.models import Pesagem, Parto
from indicadores.avaliadores import avaliar_evento_pesagem
from indicadores.models import ResultadoConformidade

terneira = Animal.objects.get(id=277)

# ─── PASSO 1: corrigir peso_nascimento no parto para 43kg
parto = terneira.parto_origem
print(f"Peso nascimento no parto: {parto.peso_nascimento}kg → corrigindo para 43kg")
parto.peso_nascimento = Decimal('43.0')
parto.save()
print("  ✓ Parto atualizado.\n")

# ─── PASSO 2: remover pesagem de 15/08 (peso de nascimento não é pesagem de acompanhamento)
pesagem_15 = Pesagem.objects.filter(animal=terneira, data=datetime.date(2026, 8, 15)).first()
if pesagem_15:
    ResultadoConformidade.objects.filter(
        animal=terneira, evento_tipo='pesagem', evento_id=pesagem_15.id
    ).delete()
    pesagem_15.delete()
    print("Pesagem de 15/08 (43kg) removida — peso de nascimento fica registrado no parto.\n")
else:
    print("Pesagem de 15/08 não encontrada.\n")

# ─── PASSO 3: corrigir todas as pesagens de 16/08 a 24/08
# Base: nasceu 43kg
# Dia 1 (16/08): queda fisiológica ~2% → 42.2kg
# A partir daí: GMD ~0.8 kg/dia para Holandês
correcoes = [
    (datetime.date(2026, 8, 16), Decimal('42.2'), 'Queda fisiológica normal no 1º dia — esperada em neonatos.'),
    (datetime.date(2026, 8, 17), Decimal('43.0'), 'Recuperou peso de nascimento. Boa ingestão de leite.'),
    (datetime.date(2026, 8, 18), Decimal('43.8'), 'Ganho de 0.8kg. Reflexo de sucção bem estabelecido.'),
    (datetime.date(2026, 8, 19), Decimal('44.5'), 'Ganho menor — diarreia leve iniciada. Tratamento com eletrólitos.'),
    (datetime.date(2026, 8, 20), Decimal('45.1'), 'Recuperando da diarreia. Fezes melhorando.'),
    (datetime.date(2026, 8, 21), Decimal('46.0'), 'Cura da diarreia. GMD voltando ao normal.'),
    (datetime.date(2026, 8, 22), Decimal('46.8'), 'Pesagem rotineira. Evolução adequada.'),
    (datetime.date(2026, 8, 23), Decimal('47.6'), 'Terneira ativa e alerta. Curva dentro do esperado.'),
    (datetime.date(2026, 8, 24), Decimal('48.4'), 'GMD acumulado ~0.80 kg/dia desde o nascimento.'),
]

print("Corrigindo pesagens de 16/08 a 24/08...\n")
for data, novo_peso, nova_obs in correcoes:
    p, created = Pesagem.objects.get_or_create(
        animal=terneira,
        data=data,
        defaults=dict(
            peso_kg=novo_peso,
            metodo='fita_toracica',
            responsavel=None,
            observacoes=nova_obs,
        )
    )
    if not created:
        peso_anterior = p.peso_kg
        p.peso_kg = novo_peso
        p.metodo = 'fita_toracica'
        p.observacoes = nova_obs
        p.save()
        print(f"  {data}: {peso_anterior}kg → {novo_peso}kg ✓")
    else:
        print(f"  {data}: criada {novo_peso}kg ✓")

    # Recalcular conformidade C7
    ResultadoConformidade.objects.filter(
        animal=terneira, evento_tipo='pesagem', evento_id=p.id
    ).delete()
    avaliar_evento_pesagem(p)

# ─── RESUMO
print()
print("─" * 50)
print("RESUMO FINAL — Pesagens")
print("─" * 50)
for p in Pesagem.objects.filter(animal=terneira).order_by('data'):
    idade = (p.data - terneira.data_nascimento).days
    print(f"  {p.data} (dia {idade:>2}): {p.peso_kg}kg | {p.get_metodo_display()}")

print()
print(f"Peso de nascimento no parto: {Parto.objects.get(terneira=terneira).peso_nascimento}kg")
print()
print("✅ Correção concluída.")
