from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from animais.models import Animal
from .models import ProgramaAcompanhamento, CheckpointSesMeses, ProjecaoReprodutiva, CoberturaIA
from .forms import CheckpointForm, CoberturaIAForm
from indicadores.services import (
    calcular_gmd, calcular_gmd_periodo, classificar_peso_vs_meta,
    projetar_data_reprodutiva, classificar_trajetoria,
)


def _prop(request):
    return request.propriedade_ativa


def lista_programas(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    status = request.GET.get('status', 'em_andamento')
    programas = ProgramaAcompanhamento.objects.filter(
        terneira__propriedade=prop,
        status=status,
    ).select_related('terneira').order_by('-data_inicio')

    # Enriquece com dados calculados
    dados = []
    for p in programas:
        ultima_pesagem = p.terneira.pesagens.order_by('-data').first()
        checkpoint = getattr(p, 'checkpoint', None)
        dados.append({
            'programa': p,
            'ultima_pesagem': ultima_pesagem,
            'checkpoint': checkpoint,
            'checkpoint_pendente': p.checkpoint_pendente,
        })

    return render(request, 'programas/lista_programas.html', {
        'dados': dados,
        'status': status,
    })


def detalhe_programa(request, pk):
    prop = _prop(request)
    programa = get_object_or_404(ProgramaAcompanhamento, pk=pk, terneira__propriedade=prop)
    terneira = programa.terneira
    pesagens = list(terneira.pesagens.order_by('data'))
    checkpoint = getattr(programa, 'checkpoint', None)

    gmd_total = None
    gmd_recente = None
    if len(pesagens) >= 2:
        gmd_total = calcular_gmd(
            float(pesagens[0].peso_kg), float(pesagens[-1].peso_kg),
            pesagens[0].data, pesagens[-1].data,
        )
        gmd_recente = calcular_gmd_periodo(pesagens, 30)

    return render(request, 'programas/detalhe_programa.html', {
        'programa': programa,
        'terneira': terneira,
        'pesagens': pesagens,
        'checkpoint': checkpoint,
        'gmd_total': gmd_total,
        'gmd_recente': gmd_recente,
    })


def checkpoint_ses_meses(request, pk):
    prop = _prop(request)
    programa = get_object_or_404(ProgramaAcompanhamento, pk=pk, terneira__propriedade=prop)
    terneira = programa.terneira

    if hasattr(programa, 'checkpoint'):
        return redirect('programas:detalhe_checkpoint', pk=programa.checkpoint.pk)

    # Calcula tudo automaticamente antes de exibir o formulário
    pesagens = list(terneira.pesagens.order_by('data'))
    hoje = timezone.now().date()
    idade_dias = (hoje - terneira.data_nascimento).days if terneira.data_nascimento else None

    # Pesos
    ultima_pesagem = pesagens[-1] if pesagens else None
    peso_atual = float(ultima_pesagem.peso_kg) if ultima_pesagem else None

    # GMDs
    gmd_total = None
    gmd_30d = None
    if len(pesagens) >= 2:
        gmd_total = calcular_gmd(
            float(pesagens[0].peso_kg), float(pesagens[-1].peso_kg),
            pesagens[0].data, pesagens[-1].data,
        )
        gmd_30d = calcular_gmd_periodo(pesagens, 30)

    # Meta de peso
    from config_tecnica.models import MetaDesenvolvimento, MetaReprodutiva
    meta = MetaDesenvolvimento.objects.filter(
        propriedade=prop, raca=terneira.raca, ativa=True
    ).prefetch_related('pontos').first()

    peso_meta = None
    percentual_meta = None
    if meta and idade_dias:
        pontos = list(meta.pontos.filter(tipo='peso').order_by('idade_dias').values('idade_dias', 'valor_ideal'))
        for i in range(len(pontos) - 1):
            if pontos[i]['idade_dias'] <= idade_dias <= pontos[i+1]['idade_dias']:
                frac = (idade_dias - pontos[i]['idade_dias']) / (pontos[i+1]['idade_dias'] - pontos[i]['idade_dias'])
                peso_meta = float(pontos[i]['valor_ideal']) + frac * (float(pontos[i+1]['valor_ideal']) - float(pontos[i]['valor_ideal']))
                break
        if peso_meta and peso_atual:
            percentual_meta = round(peso_atual / peso_meta * 100, 1)

    # Ocorrências sanitárias
    from eventos.models import OcorrenciaSanitaria
    ocorrencias = OcorrenciaSanitaria.objects.filter(animal=terneira)
    diarreia = ocorrencias.filter(tipo='diarreia').count()
    pneumonia = ocorrencias.filter(tipo='pneumonia').count()
    onfalite = ocorrencias.filter(tipo='onfalite').count()
    total_tratamentos = ocorrencias.exclude(medicamento='').count()
    doenca_ativa = ocorrencias.filter(data_fim__isnull=True).exists()

    # Desaleitamento
    desaleitada = hasattr(terneira, 'desaleitamento')

    # Status checkpoint
    if percentual_meta is not None:
        if percentual_meta >= 100:
            status_checkpoint = 'adequado'
        elif percentual_meta >= 90:
            status_checkpoint = 'atencao'
        else:
            status_checkpoint = 'critico'
    else:
        status_checkpoint = 'pendente'

    # Meta reprodutiva para projeção
    meta_rep = MetaReprodutiva.objects.filter(
        propriedade=prop, raca=terneira.raca, ativa=True
    ).first()

    trajetoria = {'status': 'insuficiente', 'motivos': ['Dados insuficientes']}
    if gmd_30d and peso_atual and meta_rep and meta_rep.peso_alvo_calculado and terneira.data_nascimento:
        idade_alvo_dias = (meta_rep.idade_alvo_meses or 13) * 30
        data_alvo = terneira.data_nascimento.replace(year=terneira.data_nascimento.year) + \
                    __import__('datetime').timedelta(days=idade_alvo_dias)
        trajetoria = classificar_trajetoria(
            peso_atual=peso_atual,
            peso_alvo=float(meta_rep.peso_alvo_calculado),
            gmd_recente=gmd_30d,
            gmd_minimo_necessario=float(meta_rep.gmd_minimo_recria) if meta_rep.gmd_minimo_recria else None,
            data_referencia=hoje,
            data_alvo=data_alvo,
        )

    dados_iniciais = {
        'data_avaliacao': hoje.strftime('%Y-%m-%d'),
        'idade_dias': idade_dias,
        'peso_kg': peso_atual,
        'peso_meta_kg': round(peso_meta, 1) if peso_meta else None,
        'percentual_meta': percentual_meta,
        'gmd_total': gmd_total,
        'gmd_30_dias': gmd_30d,
        'diarreia_ocorrencias': diarreia,
        'pneumonia_ocorrencias': pneumonia,
        'onfalite_ocorrencias': onfalite,
        'total_tratamentos': total_tratamentos,
        'doenca_ativa': doenca_ativa,
        'desaleitada': desaleitada,
        'status_checkpoint': status_checkpoint,
        'status_trajetoria': trajetoria['status'],
        'indicadores_trajetoria': '\n'.join(trajetoria['motivos']),
    }

    if request.method == 'POST':
        form = CheckpointForm(request.POST)
        if form.is_valid():
            cp = form.save(commit=False)
            cp.programa = programa
            cp.responsavel = request.user
            cp.save()
            # Atualiza status do programa
            programa.status = 'encerrado'
            programa.save(update_fields=['status'])
            messages.success(request, 'Checkpoint de 6 meses registrado.')
            return redirect('programas:detalhe_checkpoint', pk=cp.pk)
    else:
        form = CheckpointForm(initial=dados_iniciais)

    return render(request, 'programas/form_checkpoint.html', {
        'form': form,
        'programa': programa,
        'terneira': terneira,
        'dados_calculados': dados_iniciais,
        'trajetoria': trajetoria,
    })


def detalhe_checkpoint(request, pk):
    prop = _prop(request)
    cp = get_object_or_404(CheckpointSesMeses, pk=pk, programa__terneira__propriedade=prop)
    terneira = cp.programa.terneira

    # Projeção mais recente
    projecao = terneira.projecoes_reprodutivas.order_by('-data_calculo').first()

    return render(request, 'programas/detalhe_checkpoint.html', {
        'cp': cp,
        'terneira': terneira,
        'projecao': projecao,
    })


def projecao_reprodutiva(request, terneira_pk):
    prop = _prop(request)
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=prop)
    pesagens = list(terneira.pesagens.order_by('data'))

    from config_tecnica.models import MetaReprodutiva
    meta_rep = MetaReprodutiva.objects.filter(
        propriedade=prop, raca=terneira.raca, ativa=True
    ).first()

    projecao = None
    erro = None

    if not meta_rep:
        erro = 'Nenhuma meta reprodutiva configurada para esta raça.'
    elif len(pesagens) < 2:
        erro = 'São necessárias pelo menos 2 pesagens para calcular a projeção.'
    else:
        gmd = calcular_gmd_periodo(pesagens, 60) or calcular_gmd(
            float(pesagens[0].peso_kg), float(pesagens[-1].peso_kg),
            pesagens[0].data, pesagens[-1].data,
        )
        peso_atual = float(pesagens[-1].peso_kg)
        peso_alvo = float(meta_rep.peso_alvo_calculado or meta_rep.peso_minimo_kg or 0)
        hoje = timezone.now().date()

        if gmd and gmd > 0 and peso_alvo > 0:
            data_est = projetar_data_reprodutiva(hoje, peso_atual, peso_alvo, gmd)
            idade_est = None
            if data_est and terneira.data_nascimento:
                idade_est = round((data_est - terneira.data_nascimento).days / 30.44, 1)

            idade_alvo_dias = (meta_rep.idade_alvo_meses or 13) * 30
            data_alvo = terneira.data_nascimento + __import__('datetime').timedelta(days=idade_alvo_dias) if terneira.data_nascimento else None

            traj = classificar_trajetoria(
                peso_atual=peso_atual,
                peso_alvo=peso_alvo,
                gmd_recente=gmd,
                gmd_minimo_necessario=float(meta_rep.gmd_minimo_recria) if meta_rep.gmd_minimo_recria else None,
                data_referencia=hoje,
                data_alvo=data_alvo,
            )

            projecao = ProjecaoReprodutiva.objects.create(
                terneira=terneira,
                meta_reprodutiva=meta_rep,
                data_calculo=hoje,
                peso_atual_kg=peso_atual,
                peso_alvo_kg=peso_alvo,
                gmd_projetado=gmd,
                data_estimada=data_est,
                idade_estimada_meses=idade_est,
                status_trajetoria=traj['status'],
                observacoes='\n'.join(traj['motivos']),
            )
        else:
            erro = 'GMD insuficiente para projeção confiável.'

    return render(request, 'programas/projecao_reprodutiva.html', {
        'terneira': terneira,
        'projecao': projecao,
        'meta_rep': meta_rep,
        'erro': erro,
    })


def lista_aptas_reproducao(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    from config_tecnica.models import MetaReprodutiva
    novilhas = Animal.objects.filter(
        propriedade=prop,
        sexo='F',
        categoria='novilha',
        situacao='ativa',
    ).prefetch_related('pesagens', 'projecoes_reprodutivas').order_by('-data_nascimento')

    aptas = []
    atencao = []
    for n in novilhas:
        ultima_pesagem = n.pesagens.order_by('-data').first()
        ultima_projecao = n.projecoes_reprodutivas.order_by('-data_calculo').first()
        meta = MetaReprodutiva.objects.filter(
            propriedade=prop, raca=n.raca, ativa=True
        ).first()
        item = {
            'animal': n,
            'ultima_pesagem': ultima_pesagem,
            'projecao': ultima_projecao,
            'meta': meta,
        }
        if ultima_projecao:
            if ultima_projecao.status_trajetoria == 'favoravel':
                aptas.append(item)
            else:
                atencao.append(item)
        else:
            atencao.append(item)

    return render(request, 'programas/lista_aptas.html', {
        'aptas': aptas,
        'atencao': atencao,
    })


def registrar_cobertura_ia(request, terneira_pk):
    prop = _prop(request)
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=prop)

    if request.method == 'POST':
        form = CoberturaIAForm(request.POST)
        if form.is_valid():
            ia = form.save(commit=False)
            ia.terneira = terneira
            ia.responsavel = request.user
            ia.save()
            # Atualiza categoria para vaca
            terneira.categoria = 'vaca'
            terneira.save(update_fields=['categoria'])
            messages.success(request, 'Cobertura/IA registrada.')
            return redirect('animais:detalhe_terneira', pk=terneira_pk)
    else:
        form = CoberturaIAForm(initial={'data': timezone.now().date().strftime('%Y-%m-%d')})

    return render(request, 'programas/form_ia.html', {'form': form, 'terneira': terneira})
