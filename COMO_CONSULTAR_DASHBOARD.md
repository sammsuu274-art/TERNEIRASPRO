# 📊 COMO CONSULTAR TODAS AS MÉTRICAS DO DASHBOARD

## Guia Completo: De Onde Vêm os Dados

---

## 🎯 ZONA 2 — DESEMPENHO

### 1. **Terneiras ativas**

**O que é:** Número de fêmeas em categoria terneira ou novilha, com situação ativa

**Como o dashboard calcula:**
```python
Animal.objects.filter(
    propriedade=prop,
    categoria__in=['terneira', 'novilha'],
    situacao='ativa',
    sexo='F',
).count()
```

**Como consultar diretamente (Django shell):**
```python
from animais.models import Animal
from core.models import Propriedade

prop = Propriedade.objects.get(nome='Rodrigues')

# Total terneiras+novilhas ativas
ativas = Animal.objects.filter(
    propriedade=prop,
    categoria__in=['terneira', 'novilha'],
    situacao='ativa',
    sexo='F',
).count()

print(f"Terneiras ativas: {ativas}")

# Listar cada uma
for t in Animal.objects.filter(propriedade=prop, categoria__in=['terneira', 'novilha'], situacao='ativa', sexo='F'):
    print(f"  {t.identificacao} - {t.categoria}")
```

**Período:** Último valor (sem período, mostra ATIVAS agora)

**Por que tinha 0 antes:** Dashboard buscava só `categoria='terneira'`, mas após desaleitamento viram `categoria='novilha'`

---

### 2. **Novilhas em recria**

**O que é:** Fêmeas em categoria novilha (já desaleitadas) com situação ativa

**Como o dashboard calcula:**
```python
Animal.objects.filter(
    propriedade=prop,
    categoria='novilha',
    situacao='ativa',
    sexo='F',
).count()
```

**Como consultar:**
```python
novilhas = Animal.objects.filter(
    propriedade=prop,
    categoria='novilha',
    situacao='ativa',
    sexo='F',
)

print(f"Novilhas em recria: {novilhas.count()}")
for n in novilhas:
    print(f"  {n.identificacao} - {n.data_nascimento}")
```

---

### 3. **Nascimentos (no período)**

**O que é:** Quantidade de partos registrados no período (padrão: 90 dias)

**Como o dashboard calcula:**
```python
from eventos.models import Parto
from datetime import timedelta
from django.utils import timezone

hoje = timezone.now().date()
periodo = 90  # dias
inicio_periodo = hoje - timedelta(days=periodo)

n_nascimentos = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
).count()
```

**Como consultar:**
```python
from eventos.models import Parto
from datetime import timedelta
from django.utils import timezone

prop = Propriedade.objects.get(nome='Rodrigues')
hoje = timezone.now().date()
inicio_periodo = hoje - timedelta(days=90)

partos = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
)

print(f"Nascimentos (90d): {partos.count()}")
for p in partos:
    print(f"  {p.terneira.identificacao} - {p.data_parto}")
```

**⚠️ POR QUE TEM SOMENTE 3:**
- Dashboard filtra por `data_parto__range=(inicio_periodo, hoje)`
- Período padrão = 90 dias (últimos 3 meses)
- Seus partos foram criados com datas espalhadas em 6 meses
- A maioria ficou FORA do período de 90 dias!
- Solução: Clique no link "Ver todos" ou mude o período para 180 ou 30 dias

---

### 4. **Fêmeas / Machos**

**O que é:** Separação de nascimentos por sexo no período

**Como o dashboard calcula:**
```python
n_femeas = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
    terneira__sexo='F',
).count()

n_machos = n_nascimentos - n_femeas
```

**Como consultar:**
```python
femeas = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
    terneira__sexo='F',
).count()

machos = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
).count() - femeas

print(f"Fêmeas: {femeas}")
print(f"Machos: {machos}")
```

---

### 5. **GMD médio aleitamento**

**O que é:** Ganho Médio Diário (kg/dia) durante aleitamento

**Como o dashboard calcula:**
```python
gmds = []
terneiras_aleitamento = Animal.objects.filter(
    propriedade=prop,
    categoria__in=['terneira', 'novilha'],
    situacao='ativa',
    sexo='F',
).prefetch_related('pesagens')

for t in terneiras_aleitamento:
    pesagens = list(t.pesagens.order_by('data'))
    if len(pesagens) >= 2:
        gmd = calcular_gmd(
            float(pesagens[0].peso_kg), 
            float(pesagens[-1].peso_kg),
            pesagens[0].data, 
            pesagens[-1].data,
        )
        if gmd is not None:
            gmds.append(gmd)

gmd_medio = round(sum(gmds) / len(gmds), 3) if gmds else None
```

**Fórmula GMD:**
```
GMD = (Peso Final - Peso Inicial) / Dias Decorridos
```

**Como consultar:**
```python
from indicadores.services import calcular_gmd

terneiras = Animal.objects.filter(
    propriedade=prop,
    categoria__in=['terneira', 'novilha'],
    situacao='ativa',
    sexo='F',
).prefetch_related('pesagens')

gmds = []
for t in terneiras:
    pesagens = list(t.pesagens.order_by('data'))
    if len(pesagens) >= 2:
        gmd = calcular_gmd(
            float(pesagens[0].peso_kg),
            float(pesagens[-1].peso_kg),
            pesagens[0].data,
            pesagens[-1].data,
        )
        if gmd:
            gmds.append(gmd)
            print(f"{t.identificacao}: {gmd:.3f} kg/dia")

if gmds:
    media = sum(gmds) / len(gmds)
    print(f"\nGMD Médio: {media:.3f} kg/dia (n={len(gmds)})")
```

**Por que estava vazio:** Dashboard não achava pesagens porque buscava só `terneira`

---

## 🏥 ZONA 2 — SANITÁRIO

### 6. **Mortalidade (%)**

**O que é:** Taxa de óbitos em relação a nascimentos

**Como o dashboard calcula:**
```python
# Total nascimentos no período
n_nascimentos = Parto.objects.filter(
    ciclo__vaca__propriedade=prop,
    data_parto__range=(inicio_periodo, hoje),
).count()

# Óbitos (animais com situacao='morta')
n_mortos = Animal.objects.filter(
    propriedade=prop,
    situacao='morta',
).count()

mortalidade_pct = (n_mortos / n_nascimentos * 100) if n_nascimentos > 0 else 0
```

**Como consultar:**
```python
from animais.models import Animal
from eventos.models import Parto

partos_totais = Parto.objects.filter(ciclo__vaca__propriedade=prop).count()
mortos = Animal.objects.filter(propriedade=prop, situacao='morta').count()

mortalidade = (mortos / partos_totais * 100) if partos_totais > 0 else 0

print(f"Nascimentos: {partos_totais}")
print(f"Óbitos: {mortos}")
print(f"Mortalidade: {mortalidade:.1f}%")

# Listar mortos
for m in Animal.objects.filter(propriedade=prop, situacao='morta'):
    print(f"  {m.identificacao} - motivo: {m.motivo_saida}")
```

---

### 7. **Morbidade (diarreia, pneumonia, etc.)**

**O que é:** Taxa de incidência de doenças

**Como o dashboard calcula:**
```python
from eventos.models import OcorrenciaSanitaria

# Diarreia
n_diarreia = OcorrenciaSanitaria.objects.filter(
    animal__propriedade=prop,
    tipo='diarreia',
    data_inicio__range=(inicio_periodo, hoje),
).count()

# Total terneiras no período
n_terneiras = Animal.objects.filter(
    propriedade=prop,
    categoria__in=['terneira', 'novilha'],
    data_nascimento__range=(inicio_periodo, hoje),
).count()

incidencia_diarreia = (n_diarreia / n_terneiras * 100) if n_terneiras > 0 else 0
```

**Como consultar:**
```python
from eventos.models import OcorrenciaSanitaria

ocorrencias = OcorrenciaSanitaria.objects.filter(
    animal__propriedade=prop,
    data_inicio__range=(inicio_periodo, hoje),
).values('tipo').annotate(count=Count('tipo'))

for oc in ocorrencias:
    print(f"{oc['tipo']}: {oc['count']} casos")

# Detalhar diarreia
diarreias = OcorrenciaSanitaria.objects.filter(
    animal__propriedade=prop,
    tipo='diarreia',
    data_inicio__range=(inicio_periodo, hoje),
)

for d in diarreias:
    print(f"  {d.animal.identificacao} - {d.data_inicio} - {d.resultado}")
```

---

## 📋 ZONA 2 — CONFORMIDADE DE PROTOCOLOS

### 8-14. **C1-C7: Conformidades**

**O que são:**
- **C1:** Colostragem tempo ≤ 2h
- **C2:** Colostragem volume ≥ 10% peso vivo
- **C3:** Colostragem Brix ≥ 22%
- **C4:** Umbigo tempo ≤ 1h
- **C5:** Dias secos mínimo 45-75 dias
- **C6:** Dias pré-parto ≥ 21 dias
- **C7:** Peso por idade conforme meta

**Como o dashboard calcula:**
```python
from indicadores.models import ResultadoConformidade

def _taxa_conformidade(codigo_like):
    qs = ResultadoConformidade.objects.filter(
        animal__propriedade=prop,
        data_evento__range=(inicio_periodo, hoje),
        criterio__codigo__startswith=codigo_like,
    )
    
    total = qs.filter(resultado__in=['conforme', 'nao_conforme']).count()
    conformes = qs.filter(resultado='conforme').count()
    
    percentual = (conformes / total * 100) if total > 0 else None
    
    return {
        'percentual': percentual,
        'total': total,
        'conformes': conformes,
    }

# Exemplo C1 (colostragem tempo)
c1 = _taxa_conformidade('colostragem_tempo')
print(f"C1 - Colostragem tempo: {c1['percentual']}% ({c1['conformes']}/{c1['total']})")
```

**Como consultar:**
```python
from indicadores.models import ResultadoConformidade

# Total de conformidades
total = ResultadoConformidade.objects.filter(
    animal__propriedade=prop,
    data_evento__range=(inicio_periodo, hoje),
).count()

# Por resultado
conformes = ResultadoConformidade.objects.filter(
    animal__propriedade=prop,
    data_evento__range=(inicio_periodo, hoje),
    resultado='conforme',
).count()

nao_conformes = ResultadoConformidade.objects.filter(
    animal__propriedade=prop,
    data_evento__range=(inicio_periodo, hoje),
    resultado='nao_conforme',
).count()

print(f"Total: {total}")
print(f"Conformes: {conformes} ({conformes/total*100:.1f}%)")
print(f"Não conformes: {nao_conformes} ({nao_conformes/total*100:.1f}%)")

# Específica por critério
c1 = ResultadoConformidade.objects.filter(
    animal__propriedade=prop,
    data_evento__range=(inicio_periodo, hoje),
    criterio__codigo__startswith='colostragem_tempo',
)
conformes_c1 = c1.filter(resultado='conforme').count()
total_c1 = c1.filter(resultado__in=['conforme', 'nao_conforme']).count()
print(f"C1 - Colostragem tempo: {conformes_c1}/{total_c1}")
```

---

## 🔄 PERÍODO

Todos os indicadores respeitam o período selecionado (padrão: 90 dias)

**Mudar período no dashboard:**
- URL: `http://127.0.0.1:8000/?periodo=30` → últimos 30 dias
- URL: `http://127.0.0.1:8000/?periodo=180` → últimos 180 dias
- URL: `http://127.0.0.1:8000/?periodo=365` → último ano

---

## 🐍 SCRIPT PRONTO PARA COPIAR

```python
# Colar no shell e verá todos os dados do dashboard
from animais.models import Animal
from eventos.models import Parto, OcorrenciaSanitaria
from indicadores.models import ResultadoConformidade
from core.models import Propriedade
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

prop = Propriedade.objects.get(nome='Rodrigues')
hoje = timezone.now().date()
periodo = 90
inicio_periodo = hoje - timedelta(days=periodo)

print("\n=== DESEMPENHO ===")
ativas = Animal.objects.filter(prop=prop, categoria__in=['terneira', 'novilha'], situacao='ativa', sexo='F').count()
print(f"Terneiras ativas: {ativas}")

partos = Parto.objects.filter(ciclo__vaca__propriedade=prop, data_parto__range=(inicio_periodo, hoje))
print(f"Nascimentos ({periodo}d): {partos.count()}")

femeas = partos.filter(terneira__sexo='F').count()
print(f"Fêmeas/Machos: {femeas}/{partos.count()-femeas}")

print("\n=== SANITÁRIO ===")
mortos = Animal.objects.filter(propriedade=prop, situacao='morta').count()
mort_taxa = (mortos / Parto.objects.filter(ciclo__vaca__propriedade=prop).count() * 100) if Parto.objects.filter(ciclo__vaca__propriedade=prop).count() > 0 else 0
print(f"Mortalidade: {mort_taxa:.1f}%")

print("\n=== CONFORMIDADE ===")
confs = ResultadoConformidade.objects.filter(animal__propriedade=prop, data_evento__range=(inicio_periodo, hoje))
conformes = confs.filter(resultado='conforme').count()
nao_conformes = confs.filter(resultado='nao_conforme').count()
total_confs = conformes + nao_conformes
if total_confs > 0:
    print(f"Taxa conformidade: {conformes/total_confs*100:.1f}% ({conformes}/{total_confs})")
```

---

**Pronto! Agora você sabe onde cada métrica vem e como consultá-la diretamente! 🎯**
