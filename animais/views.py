from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Animal, Lote, MovimentacaoLote, CicloReprodutivo
from .forms import AnimalForm, LoteForm, CicloReprodutivoForm
from programas.models import ProgramaAcompanhamento


def _prop(request):
    return request.propriedade_ativa


# ─── TERNEIRAS ────────────────────────────────────────────────────────────────

def lista_terneiras(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    qs = Animal.objects.filter(
        propriedade=prop,
        sexo='F',
        categoria__in=['terneira', 'novilha'],
    ).order_by('-data_nascimento')

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(identificacao__icontains=q) | Q(nome__icontains=q))

    situacao = request.GET.get('situacao', 'ativa')
    qs = qs.filter(situacao=situacao)

    return render(request, 'animais/lista_terneiras.html', {
        'terneiras': qs,
        'q': q,
        'situacao': situacao,
    })


def nova_terneira(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    if request.method == 'POST':
        form = AnimalForm(request.POST, propriedade=prop, categoria_inicial='terneira')
        if form.is_valid():
            animal = form.save(commit=False)
            animal.propriedade = prop
            animal.categoria = 'terneira'
            animal.save()
            # Cria programa de acompanhamento automaticamente
            if animal.data_nascimento:
                ProgramaAcompanhamento.objects.create(
                    terneira=animal,
                    data_inicio=animal.data_nascimento,
                )
            messages.success(request, f'Terneira {animal.identificacao} cadastrada.')
            return redirect('animais:detalhe_terneira', pk=animal.pk)
    else:
        form = AnimalForm(propriedade=prop, categoria_inicial='terneira')

    return render(request, 'animais/form_animal.html', {
        'form': form,
        'titulo': 'Nova Terneira',
        'cancelar_url': 'animais:lista_terneiras',
    })


def detalhe_terneira(request, pk):
    prop = _prop(request)
    terneira = get_object_or_404(Animal, pk=pk, propriedade=prop)

    pesagens = terneira.pesagens.order_by('data')
    ocorrencias = terneira.ocorrencias_sanitarias.order_by('-data_inicio')
    vacinacoes = terneira.vacinacoes.order_by('-data')
    colostragens = terneira.colostragens.order_by('data_hora')
    curas_umbigo = terneira.curas_umbigo.order_by('data_hora')
    movimentacoes = terneira.movimentacoes.select_related('lote').order_by('-data')

    programa = getattr(terneira, 'programa_acompanhamento', None)
    checkpoint = getattr(programa, 'checkpoint', None) if programa else None
    desaleitamento = getattr(terneira, 'desaleitamento', None)
    parto_origem = getattr(terneira, 'parto_origem', None)

    # GMD
    from indicadores.services import calcular_gmd, calcular_gmd_periodo, classificar_peso_vs_meta
    from config_tecnica.models import MetaDesenvolvimento

    gmd_total = None
    gmd_recente = None
    classificacao_peso = None

    pesagens_list = list(pesagens)
    if len(pesagens_list) >= 2:
        primeiro = pesagens_list[0]
        ultimo = pesagens_list[-1]
        gmd_total = calcular_gmd(
            float(primeiro.peso_kg), float(ultimo.peso_kg),
            primeiro.data, ultimo.data,
        )
        gmd_recente = calcular_gmd_periodo(pesagens_list, 30)

    # Meta da raça
    meta = MetaDesenvolvimento.objects.filter(
        propriedade=prop, raca=terneira.raca, ativa=True
    ).prefetch_related('pontos').first()
    peso_meta_hoje = None
    if meta and terneira.idade_dias and pesagens_list:
        pontos = list(meta.pontos.filter(tipo='peso').order_by('idade_dias').values('idade_dias', 'valor_ideal'))
        idade = terneira.idade_dias
        for i in range(len(pontos) - 1):
            if pontos[i]['idade_dias'] <= idade <= pontos[i+1]['idade_dias']:
                frac = (idade - pontos[i]['idade_dias']) / (pontos[i+1]['idade_dias'] - pontos[i]['idade_dias'])
                peso_meta_hoje = float(pontos[i]['valor_ideal']) + frac * (float(pontos[i+1]['valor_ideal']) - float(pontos[i]['valor_ideal']))
                break
        if peso_meta_hoje and pesagens_list:
            classificacao_peso = classificar_peso_vs_meta(float(pesagens_list[-1].peso_kg), peso_meta_hoje)

    # Dados gráfico
    grafico_datas = [str(p.data) for p in pesagens_list]
    grafico_pesos = [float(p.peso_kg) for p in pesagens_list]
    grafico_meta = []
    if meta and terneira.data_nascimento:
        pontos_meta = list(meta.pontos.filter(tipo='peso').order_by('idade_dias').values('idade_dias', 'valor_ideal'))
        for p_data in pesagens_list:
            idade = (p_data.data - terneira.data_nascimento).days
            pm = None
            for i in range(len(pontos_meta) - 1):
                if pontos_meta[i]['idade_dias'] <= idade <= pontos_meta[i+1]['idade_dias']:
                    frac = (idade - pontos_meta[i]['idade_dias']) / (pontos_meta[i+1]['idade_dias'] - pontos_meta[i]['idade_dias'])
                    pm = float(pontos_meta[i]['valor_ideal']) + frac * (float(pontos_meta[i+1]['valor_ideal']) - float(pontos_meta[i]['valor_ideal']))
                    break
            grafico_meta.append(round(pm, 1) if pm else None)

    return render(request, 'animais/detalhe_terneira.html', {
        'terneira': terneira,
        'parto_origem': parto_origem,
        'pesagens': pesagens_list,
        'ocorrencias': ocorrencias,
        'vacinacoes': vacinacoes,
        'colostragens': colostragens,
        'curas_umbigo': curas_umbigo,
        'movimentacoes': movimentacoes,
        'programa': programa,
        'checkpoint': checkpoint,
        'desaleitamento': desaleitamento,
        'gmd_total': gmd_total,
        'gmd_recente': gmd_recente,
        'classificacao_peso': classificacao_peso,
        'peso_meta_hoje': peso_meta_hoje,
        'grafico_datas': grafico_datas,
        'grafico_pesos': grafico_pesos,
        'grafico_meta': grafico_meta,
    })


def editar_terneira(request, pk):
    prop = _prop(request)
    terneira = get_object_or_404(Animal, pk=pk, propriedade=prop)

    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=terneira, propriedade=prop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados.')
            return redirect('animais:detalhe_terneira', pk=pk)
    else:
        form = AnimalForm(instance=terneira, propriedade=prop)

    return render(request, 'animais/form_animal.html', {
        'form': form,
        'titulo': f'Editar — {terneira.identificacao}',
        'cancelar_url': 'animais:detalhe_terneira',
        'cancelar_pk': pk,
    })


# ─── VACAS ────────────────────────────────────────────────────────────────────

def lista_vacas(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    qs = Animal.objects.filter(
        propriedade=prop,
        sexo='F',
        categoria='vaca',
        situacao='ativa',
    ).order_by('identificacao')

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(identificacao__icontains=q) | Q(nome__icontains=q))

    return render(request, 'animais/lista_vacas.html', {'vacas': qs, 'q': q})


def nova_vaca(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    if request.method == 'POST':
        form = AnimalForm(request.POST, propriedade=prop, categoria_inicial='vaca')
        if form.is_valid():
            animal = form.save(commit=False)
            animal.propriedade = prop
            animal.categoria = 'vaca'
            animal.save()
            messages.success(request, f'Vaca {animal.identificacao} cadastrada.')
            return redirect('animais:detalhe_vaca', pk=animal.pk)
    else:
        form = AnimalForm(propriedade=prop, categoria_inicial='vaca')

    return render(request, 'animais/form_animal.html', {
        'form': form,
        'titulo': 'Nova Vaca / Matriz',
        'cancelar_url': 'animais:lista_vacas',
    })


def detalhe_vaca(request, pk):
    prop = _prop(request)
    vaca = get_object_or_404(Animal, pk=pk, propriedade=prop)
    ciclos = vaca.ciclos_reprodutivos.order_by('-data_previsao_parto')
    filhos = vaca.filhos.order_by('-data_nascimento')
    return render(request, 'animais/detalhe_vaca.html', {
        'vaca': vaca,
        'ciclos': ciclos,
        'filhos': filhos,
    })


# ─── LOTES ────────────────────────────────────────────────────────────────────

def lista_lotes(request):
    prop = _prop(request)
    lotes = Lote.objects.filter(propriedade=prop, ativo=True)
    return render(request, 'animais/lista_lotes.html', {'lotes': lotes})


def novo_lote(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.propriedade = prop
            lote.save()
            messages.success(request, f'Lote {lote.nome} criado.')
            return redirect('animais:lista_lotes')
    else:
        form = LoteForm()
    return render(request, 'animais/form_lote.html', {'form': form})


def detalhe_lote(request, pk):
    prop = _prop(request)
    lote = get_object_or_404(Lote, pk=pk, propriedade=prop)
    movs = MovimentacaoLote.objects.filter(lote=lote).select_related('animal').order_by('-data')
    # Animais atualmente no lote
    from django.db.models import OuterRef, Subquery
    animais_no_lote = Animal.objects.filter(
        propriedade=prop,
        situacao='ativa',
        movimentacoes__lote=lote,
    ).distinct()
    return render(request, 'animais/detalhe_lote.html', {
        'lote': lote,
        'movimentacoes': movs[:50],
        'animais': animais_no_lote,
    })


# ─── CICLO REPRODUTIVO ────────────────────────────────────────────────────────

def novo_ciclo(request, vaca_pk):
    prop = _prop(request)
    vaca = get_object_or_404(Animal, pk=vaca_pk, propriedade=prop)

    if request.method == 'POST':
        form = CicloReprodutivoForm(request.POST, propriedade=prop)
        if form.is_valid():
            ciclo = form.save(commit=False)
            ciclo.vaca = vaca
            ciclo.save()
            messages.success(request, 'Ciclo reprodutivo registrado.')
            return redirect('animais:detalhe_vaca', pk=vaca_pk)
    else:
        form = CicloReprodutivoForm(propriedade=prop)

    return render(request, 'animais/form_ciclo.html', {
        'form': form,
        'vaca': vaca,
    })
