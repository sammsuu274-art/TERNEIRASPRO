from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Protocolo, MetaDesenvolvimento, PontoMetaDesenvolvimento,
    MetaReprodutiva, ReferencialTecnico, CriterioConformidade,
)
from .forms import ProtocoloForm, MetaDesenvolvimentoForm, MetaReprodutivaForm, CriterioConformidadeForm
from core.decorators import admin_ou_tecnico


def _prop(request):
    return request.propriedade_ativa


def painel_config(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    ctx = {
        'n_protocolos': Protocolo.objects.filter(propriedade=prop, vigencia_fim__isnull=True).count(),
        'n_metas': MetaDesenvolvimento.objects.filter(propriedade=prop, ativa=True).count(),
        'n_metas_rep': MetaReprodutiva.objects.filter(propriedade=prop, ativa=True).count(),
        'n_referenciais': ReferencialTecnico.objects.filter(ativo=True).count(),
        'n_criterios': CriterioConformidade.objects.filter(propriedade=prop, ativo=True, vigencia_fim__isnull=True).count(),
    }
    return render(request, 'config_tecnica/painel.html', ctx)


def lista_protocolos(request):
    prop = _prop(request)
    protocolos = Protocolo.objects.filter(propriedade=prop).order_by('nome', '-versao')
    return render(request, 'config_tecnica/lista_protocolos.html', {'protocolos': protocolos})


@admin_ou_tecnico
def novo_protocolo(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = ProtocoloForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.propriedade = prop
            p.criado_por = request.user
            p.save()
            messages.success(request, 'Protocolo criado.')
            return redirect('config_tecnica:lista_protocolos')
    else:
        form = ProtocoloForm()
    return render(request, 'config_tecnica/form_protocolo.html', {'form': form})


def lista_metas(request):
    prop = _prop(request)
    metas = MetaDesenvolvimento.objects.filter(propriedade=prop).prefetch_related('pontos')
    return render(request, 'config_tecnica/lista_metas.html', {'metas': metas})


@admin_ou_tecnico
def nova_meta(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = MetaDesenvolvimentoForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.propriedade = prop
            m.save()
            messages.success(request, 'Meta de desenvolvimento criada.')
            return redirect('config_tecnica:detalhe_meta', pk=m.pk)
    else:
        form = MetaDesenvolvimentoForm()
    return render(request, 'config_tecnica/form_meta.html', {'form': form})


def detalhe_meta(request, pk):
    prop = _prop(request)
    meta = get_object_or_404(MetaDesenvolvimento, pk=pk, propriedade=prop)
    pontos = meta.pontos.order_by('tipo', 'idade_dias')

    if request.method == 'POST':
        # Adicionar ponto
        from .forms import PontoMetaForm
        form_ponto = PontoMetaForm(request.POST)
        if form_ponto.is_valid():
            p = form_ponto.save(commit=False)
            p.meta = meta
            p.save()
            messages.success(request, 'Ponto adicionado.')
            return redirect('config_tecnica:detalhe_meta', pk=pk)
    else:
        from .forms import PontoMetaForm
        form_ponto = PontoMetaForm()

    return render(request, 'config_tecnica/detalhe_meta.html', {
        'meta': meta,
        'pontos': pontos,
        'form_ponto': form_ponto,
    })


def lista_metas_reprodutivas(request):
    prop = _prop(request)
    metas = MetaReprodutiva.objects.filter(propriedade=prop)
    return render(request, 'config_tecnica/lista_metas_reprodutivas.html', {'metas': metas})


@admin_ou_tecnico
def nova_meta_reprodutiva(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = MetaReprodutivaForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.propriedade = prop
            m.save()
            messages.success(request, 'Meta reprodutiva criada.')
            return redirect('config_tecnica:lista_metas_reprodutivas')
    else:
        form = MetaReprodutivaForm()
    return render(request, 'config_tecnica/form_meta_reprodutiva.html', {'form': form})


def lista_referenciais(request):
    referenciais = ReferencialTecnico.objects.filter(ativo=True).order_by('indicador')
    return render(request, 'config_tecnica/lista_referenciais.html', {'referenciais': referenciais})


def lista_criterios(request):
    prop = _prop(request)
    criterios = CriterioConformidade.objects.filter(
        propriedade=prop
    ).order_by('codigo', '-vigencia_inicio')
    return render(request, 'config_tecnica/lista_criterios.html', {'criterios': criterios})


@admin_ou_tecnico
def novo_criterio(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = CriterioConformidadeForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.propriedade = prop
            c.save()
            messages.success(request, f'Critério "{c.descricao}" criado.')
            return redirect('config_tecnica:lista_criterios')
    else:
        from django.utils import timezone
        form = CriterioConformidadeForm(
            initial={'vigencia_inicio': timezone.now().date().strftime('%Y-%m-%d')}
        )
    return render(request, 'config_tecnica/form_criterio.html', {'form': form, 'titulo': 'Novo Critério'})


@admin_ou_tecnico
def editar_criterio(request, pk):
    prop = _prop(request)
    criterio = get_object_or_404(CriterioConformidade, pk=pk, propriedade=prop)
    if request.method == 'POST':
        form = CriterioConformidadeForm(request.POST, instance=criterio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Critério atualizado.')
            return redirect('config_tecnica:lista_criterios')
    else:
        form = CriterioConformidadeForm(instance=criterio)
    return render(request, 'config_tecnica/form_criterio.html', {
        'form': form,
        'titulo': f'Editar — {criterio.descricao}',
        'criterio': criterio,
    })
