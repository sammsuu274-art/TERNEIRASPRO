from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from animais.models import Animal
from eventos.models import (
    Colostragem, CuraUmbigo, OcorrenciaSanitaria, Pesagem,
    ProtocoloAlimentar, Desaleitamento
)
from .models import (
    AmbienteBEA, ComportamentoBEA, DietaSolidaBEA, VisitaPresencialBEA,
    ConsentimentoBEA, EvidenciasBEA, JornadaProCampo, PlanoAcaoBEA
)
from .forms import (
    AmbienteBEAForm, ComportamentoBEAForm, VisitaPresencialBEAForm,
    ConsentimentoBEAForm, EvidenciasBEAForm,
    PlanoAcaoBEAForm, AlterarStatusAcaoForm,
)
from core.decorators import papel_minimo_required, admin_ou_tecnico


def _prop(request):
    return request.propriedade_ativa


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    # Jornadas
    jornadas = JornadaProCampo.objects.filter(propriedade=prop)
    jornadas_ativas = jornadas.filter(status='em_andamento').count()
    jornadas_concluidas = jornadas.filter(status='concluida').count()

    # Visitas
    visitas = VisitaPresencialBEA.objects.filter(propriedade=prop)
    total_visitas = visitas.count()
    visitas_baseline = visitas.filter(tipo_visita='baseline').count()
    visitas_acompanhamento = visitas.filter(tipo_visita='acompanhamento').count()

    # Plano de ação
    acoes = PlanoAcaoBEA.objects.filter(jornada__propriedade=prop)
    total_acoes = acoes.count()
    acoes_pendentes = acoes.filter(status='pendente').count()
    acoes_andamento = acoes.filter(status='em_andamento').count()
    acoes_concluidas = acoes.filter(status='concluido').count()
    acoes_atrasadas = sum(1 for a in acoes.filter(status__in=['pendente', 'em_andamento'])
                         if a.esta_atrasada)

    # Avaliações de ambiente
    total_ambiente = AmbienteBEA.objects.filter(terneira__propriedade=prop).count()
    total_comportamento = ComportamentoBEA.objects.filter(terneira__propriedade=prop).count()
    total_evidencias = EvidenciasBEA.objects.count()
    total_consentimentos = ConsentimentoBEA.objects.filter(propriedade=prop).count()

    # Jornada mais recente para exibição rápida
    jornada_atual = jornadas.filter(status='em_andamento').order_by('-data_inicio').first()

    context = {
        'propriedade': prop,
        # Jornadas
        'jornadas_ativas': jornadas_ativas,
        'jornadas_concluidas': jornadas_concluidas,
        'total_jornadas': jornadas.count(),
        # Visitas
        'total_visitas': total_visitas,
        'visitas_baseline': visitas_baseline,
        'visitas_acompanhamento': visitas_acompanhamento,
        # Plano de ação
        'total_acoes': total_acoes,
        'acoes_pendentes': acoes_pendentes,
        'acoes_andamento': acoes_andamento,
        'acoes_concluidas': acoes_concluidas,
        'acoes_atrasadas': acoes_atrasadas,
        # Avaliações
        'total_ambiente': total_ambiente,
        'total_comportamento': total_comportamento,
        'total_evidencias': total_evidencias,
        'total_consentimentos': total_consentimentos,
        # Jornada atual
        'jornada_atual': jornada_atual,
        # Ações abertas recentes (para lista no dashboard)
        'acoes_abertas_recentes': acoes.filter(
            status__in=['pendente', 'em_andamento']
        ).select_related('jornada', 'responsavel').order_by('prazo')[:5],
    }
    return render(request, 'bem_estar_animal/dashboard.html', context)


# ─── JORNADAS PROCAMPO ─────────────────────────────────────────────────────────

@login_required
def lista_jornadas(request):
    """Lista todas as jornadas ProCampo da propriedade"""
    prop = _prop(request)
    if not prop:
        return redirect('/')
    
    jornadas = JornadaProCampo.objects.filter(
        propriedade=prop
    ).select_related('supervisor', 'produtor', 'propriedade').order_by('-data_inicio')
    
    return render(request, 'bem_estar_animal/lista_jornadas.html', {
        'jornadas': jornadas,
        'propriedade': prop,
    })


@login_required
@admin_ou_tecnico
def nova_jornada(request):
    """Cria uma nova jornada ProCampo"""
    prop = _prop(request)
    if not prop:
        return redirect('/')
    
    # TODO: Implementar formulário de criação
    messages.info(request, 'Formulário de nova jornada em desenvolvimento.')
    return redirect('bem_estar_animal:lista_jornadas')


@login_required
def detalhe_jornada(request, pk):
    """Exibe detalhes completos de uma jornada"""
    prop = _prop(request)
    if not prop:
        return redirect('/')
    
    jornada = get_object_or_404(JornadaProCampo, pk=pk, propriedade=prop)
    
    # Buscar ações do plano agrupadas por situação
    acoes_pendentes = jornada.plano_acao.filter(status='pendente').order_by('prazo')
    acoes_andamento = jornada.plano_acao.filter(status='em_andamento').order_by('prazo')
    acoes_concluidas = jornada.plano_acao.filter(status='concluido').order_by('-data_conclusao')
    
    return render(request, 'bem_estar_animal/detalhe_jornada.html', {
        'jornada': jornada,
        'propriedade': prop,
        'acoes_pendentes': acoes_pendentes,
        'acoes_andamento': acoes_andamento,
        'acoes_concluidas': acoes_concluidas,
    })


@login_required
def diagnostico_jornada(request, pk):
    """Exibe o diagnóstico inicial da jornada (baseline) com classificações automáticas"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    jornada = get_object_or_404(JornadaProCampo, pk=pk, propriedade=prop)

    # Terneiras ativas da propriedade (base do diagnóstico)
    terneiras = Animal.objects.filter(
        propriedade=prop, categoria='terneira'
    ).order_by('identificacao')

    # ── SAÚDE ────────────────────────────────────────────────────────────────
    # Últimas colostragens (com Brix) para classificação
    colostragens_recentes = Colostragem.objects.filter(
        terneira__propriedade=prop,
        brix__isnull=False
    ).select_related('terneira').order_by('-data_hora')[:20]

    # Ocorrências sanitárias recentes
    ocorrencias_recentes = OcorrenciaSanitaria.objects.filter(
        animal__propriedade=prop
    ).select_related('animal').order_by('-data_inicio')[:20]

    # Curas de umbigo
    curas_recentes = CuraUmbigo.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data_hora')[:20]

    # ── AMBIENTE ─────────────────────────────────────────────────────────────
    ambientes_recentes = AmbienteBEA.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data_avaliacao')[:10]

    # ── COLOSTRAGEM E ALEITAMENTO ─────────────────────────────────────────────
    protocolos_recentes = ProtocoloAlimentar.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data_inicio')[:10]

    # ── ÁGUA E DIETA SÓLIDA ───────────────────────────────────────────────────
    dietas_recentes = DietaSolidaBEA.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data_avaliacao')[:10]

    # ── DESALEITAMENTO ────────────────────────────────────────────────────────
    desaleitamentos_recentes = Desaleitamento.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data')[:10]

    # ── COMPORTAMENTO ─────────────────────────────────────────────────────────
    comportamentos_recentes = ComportamentoBEA.objects.filter(
        terneira__propriedade=prop
    ).select_related('terneira').order_by('-data_avaliacao')[:10]

    return render(request, 'bem_estar_animal/diagnostico_jornada.html', {
        'jornada': jornada,
        'propriedade': prop,
        'terneiras': terneiras,
        # Saúde
        'colostragens_recentes': colostragens_recentes,
        'ocorrencias_recentes': ocorrencias_recentes,
        'curas_recentes': curas_recentes,
        # Ambiente
        'ambientes_recentes': ambientes_recentes,
        # Colostragem e aleitamento
        'protocolos_recentes': protocolos_recentes,
        # Água e dieta sólida
        'dietas_recentes': dietas_recentes,
        # Desaleitamento
        'desaleitamentos_recentes': desaleitamentos_recentes,
        # Comportamento
        'comportamentos_recentes': comportamentos_recentes,
    })


@login_required
def avaliacao_jornada(request, pk):
    """Registra uma nova avaliação na jornada"""
    prop = _prop(request)
    if not prop:
        return redirect('/')
    
    jornada = get_object_or_404(JornadaProCampo, pk=pk, propriedade=prop)
    
    # TODO: Implementar formulário de avaliação
    messages.info(request, 'Formulário de avaliação em desenvolvimento.')
    return redirect('bem_estar_animal:detalhe_jornada', pk=pk)


# ─── PLANO DE AÇÃO ─────────────────────────────────────────────────────────────

@login_required
def lista_planos_acao(request):
    """Lista todas as ações do plano BEA com filtros"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    acoes = PlanoAcaoBEA.objects.filter(
        jornada__propriedade=prop
    ).select_related('jornada', 'responsavel').order_by('prazo', '-prioridade')

    # Filtro por status
    status_filtro = request.GET.get('status', '')
    if status_filtro:
        acoes = acoes.filter(status=status_filtro)

    # Filtro por domínio
    dominio_filtro = request.GET.get('dominio', '')
    if dominio_filtro:
        acoes = acoes.filter(dominio__icontains=dominio_filtro)

    # Contagens para resumo
    todas = PlanoAcaoBEA.objects.filter(jornada__propriedade=prop)
    contagens = {
        'total': todas.count(),
        'pendente': todas.filter(status='pendente').count(),
        'em_andamento': todas.filter(status='em_andamento').count(),
        'concluido': todas.filter(status='concluido').count(),
        'cancelado': todas.filter(status='cancelado').count(),
    }

    return render(request, 'bem_estar_animal/lista_planos_acao.html', {
        'acoes': acoes,
        'propriedade': prop,
        'status_filtro': status_filtro,
        'dominio_filtro': dominio_filtro,
        'contagens': contagens,
    })


@login_required
@admin_ou_tecnico
def novo_plano_acao(request):
    """Cria uma nova ação no plano"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    # Pré-preencher jornada se passada via GET
    jornada_pk = request.GET.get('jornada')
    initial = {}
    if jornada_pk:
        initial['jornada'] = jornada_pk

    if request.method == 'POST':
        form = PlanoAcaoBEAForm(request.POST)
        # Filtrar jornadas da propriedade
        form.fields['jornada'].queryset = JornadaProCampo.objects.filter(
            propriedade=prop, status__in=['planejamento', 'em_andamento']
        )
        if form.is_valid():
            acao = form.save()
            messages.success(request, f'Ação "{acao.indicador}" criada com sucesso.')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('bem_estar_animal:detalhe_plano_acao', pk=acao.pk)
    else:
        form = PlanoAcaoBEAForm(initial=initial)
        form.fields['jornada'].queryset = JornadaProCampo.objects.filter(
            propriedade=prop, status__in=['planejamento', 'em_andamento']
        )

    return render(request, 'bem_estar_animal/form_plano_acao.html', {
        'form': form,
        'titulo': 'Nova Ação',
        'acao': None,
    })


@login_required
def detalhe_plano_acao(request, pk):
    """Exibe detalhes de uma ação específica"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    acao = get_object_or_404(PlanoAcaoBEA, pk=pk, jornada__propriedade=prop)

    return render(request, 'bem_estar_animal/detalhe_plano_acao.html', {
        'acao': acao,
        'propriedade': prop,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor')
def editar_plano_acao(request, pk):
    """Edita uma ação existente"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    acao = get_object_or_404(PlanoAcaoBEA, pk=pk, jornada__propriedade=prop)

    if request.method == 'POST':
        form = PlanoAcaoBEAForm(request.POST, instance=acao)
        form.fields['jornada'].queryset = JornadaProCampo.objects.filter(
            propriedade=prop
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Ação atualizada com sucesso.')
            return redirect('bem_estar_animal:detalhe_plano_acao', pk=pk)
    else:
        form = PlanoAcaoBEAForm(instance=acao)
        form.fields['jornada'].queryset = JornadaProCampo.objects.filter(
            propriedade=prop
        )

    return render(request, 'bem_estar_animal/form_plano_acao.html', {
        'form': form,
        'titulo': f'Editar — {acao.indicador}',
        'acao': acao,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor')
def alterar_situacao_acao(request, pk):
    """Altera o status de uma ação via POST"""
    prop = _prop(request)
    if not prop:
        return redirect('/')

    acao = get_object_or_404(PlanoAcaoBEA, pk=pk, jornada__propriedade=prop)

    if request.method == 'POST':
        form = AlterarStatusAcaoForm(request.POST, instance=acao)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f'Status da ação atualizado para "{acao.get_status_display()}".'
                )
            except Exception as e:
                messages.error(request, f'Erro ao atualizar: {e}')
    else:
        messages.warning(request, 'Use o formulário para alterar o status.')

    return redirect('bem_estar_animal:detalhe_plano_acao', pk=pk)


# ─── AMBIENTE BEA ──────────────────────────────────────────────────────────────

@login_required
def lista_ambiente_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    return render(request, 'bem_estar_animal/lista_ambiente.html', {
        'ambiente_list': AmbienteBEA.objects.filter(
            terneira__propriedade=prop
        ).select_related('terneira').order_by('-data_avaliacao'),
        'propriedade': prop,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def novo_ambiente_bea(request, terneira_pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=prop, categoria='terneira')

    if request.method == 'POST':
        form = AmbienteBEAForm(request.POST)
        if form.is_valid():
            ambiente = form.save(commit=False)
            ambiente.terneira = terneira
            ambiente.save()
            messages.success(request, f'Avaliação de ambiente registrada para {terneira}.')
            return redirect('bem_estar_animal:lista_ambiente')
    else:
        form = AmbienteBEAForm()

    return render(request, 'bem_estar_animal/form_ambiente.html', {
        'form': form,
        'terneira': terneira,
        'titulo': 'Nova Avaliação de Ambiente',
    })


@login_required
def detalhe_ambiente_bea(request, pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    ambiente = get_object_or_404(AmbienteBEA, pk=pk, terneira__propriedade=prop)
    return render(request, 'bem_estar_animal/detalhe_ambiente.html', {'ambiente': ambiente})


# ─── COMPORTAMENTO BEA ─────────────────────────────────────────────────────────

@login_required
def lista_comportamento_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    return render(request, 'bem_estar_animal/lista_comportamento.html', {
        'comportamento_list': ComportamentoBEA.objects.filter(
            terneira__propriedade=prop
        ).select_related('terneira').order_by('-data_avaliacao'),
        'propriedade': prop,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def novo_comportamento_bea(request, terneira_pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    terneira = get_object_or_404(Animal, pk=terneira_pk, propriedade=prop, categoria='terneira')

    if request.method == 'POST':
        form = ComportamentoBEAForm(request.POST)
        if form.is_valid():
            comportamento = form.save(commit=False)
            comportamento.terneira = terneira
            comportamento.save()
            messages.success(request, f'Avaliação de comportamento registrada para {terneira}.')
            return redirect('bem_estar_animal:lista_comportamento')
    else:
        form = ComportamentoBEAForm()

    return render(request, 'bem_estar_animal/form_comportamento.html', {
        'form': form,
        'terneira': terneira,
        'titulo': 'Nova Avaliação de Comportamento',
    })


@login_required
def detalhe_comportamento_bea(request, pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    comportamento = get_object_or_404(ComportamentoBEA, pk=pk, terneira__propriedade=prop)
    return render(request, 'bem_estar_animal/detalhe_comportamento.html', {'comportamento': comportamento})


# ─── VISITA PRESENCIAL BEA ─────────────────────────────────────────────────────

@login_required
def lista_visitas_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    return render(request, 'bem_estar_animal/lista_visitas.html', {
        'visitas_list': VisitaPresencialBEA.objects.filter(
            propriedade=prop
        ).order_by('-data_visita'),
        'propriedade': prop,
    })


@login_required
@admin_ou_tecnico
def nova_visita_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    if request.method == 'POST':
        form = VisitaPresencialBEAForm(request.POST)
        if form.is_valid():
            try:
                visita = form.save(commit=False)
                visita.propriedade = prop
                visita.save()
                messages.success(request, 'Visita presencial registrada com sucesso.')
                return redirect('bem_estar_animal:lista_visitas')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {e}')
    else:
        form = VisitaPresencialBEAForm()

    return render(request, 'bem_estar_animal/form_visita.html', {
        'form': form,
        'titulo': 'Nova Visita Presencial',
    })


@login_required
def detalhe_visita_bea(request, pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    visita = get_object_or_404(VisitaPresencialBEA, pk=pk, propriedade=prop)
    return render(request, 'bem_estar_animal/detalhe_visita.html', {'visita': visita})


# ─── CONSENTIMENTO BEA ─────────────────────────────────────────────────────────

@login_required
def lista_consentimentos_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    return render(request, 'bem_estar_animal/lista_consentimentos.html', {
        'consentimentos_list': ConsentimentoBEA.objects.filter(
            propriedade=prop
        ).order_by('-data_consentimento'),
        'propriedade': prop,
    })


@login_required
@admin_ou_tecnico
def novo_consentimento_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    if request.method == 'POST':
        form = ConsentimentoBEAForm(request.POST)
        if form.is_valid():
            try:
                consentimento = form.save(commit=False)
                consentimento.propriedade = prop
                consentimento.save()
                messages.success(request, 'Consentimento registrado com sucesso.')
                return redirect('bem_estar_animal:lista_consentimentos')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {e}')
    else:
        form = ConsentimentoBEAForm()

    return render(request, 'bem_estar_animal/form_consentimento.html', {
        'form': form,
        'titulo': 'Novo Consentimento',
    })


@login_required
def detalhe_consentimento_bea(request, pk):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    consentimento = get_object_or_404(ConsentimentoBEA, pk=pk, propriedade=prop)
    return render(request, 'bem_estar_animal/detalhe_consentimento.html', {'consentimento': consentimento})


# ─── EVIDÊNCIAS BEA ────────────────────────────────────────────────────────────

@login_required
def lista_evidencias_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    # EvidenciasBEA usa GenericFK, não filtra diretamente por propriedade no MVP
    evidencias_list = EvidenciasBEA.objects.all().order_by('-data_upload')
    return render(request, 'bem_estar_animal/lista_evidencias.html', {
        'evidencias_list': evidencias_list,
        'propriedade': prop,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor')
def nova_evidencia_bea(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')

    if request.method == 'POST':
        form = EvidenciasBEAForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                evidencia = form.save(commit=False)
                evidencia.usuario_upload = request.user
                evidencia.save()
                messages.success(request, 'Evidência registrada com sucesso.')
                return redirect('bem_estar_animal:lista_evidencias')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {e}')
    else:
        form = EvidenciasBEAForm()

    return render(request, 'bem_estar_animal/form_evidencia.html', {
        'form': form,
        'titulo': 'Nova Evidência',
    })


@login_required
def detalhe_evidencia_bea(request, pk):
    evidencia = get_object_or_404(EvidenciasBEA, pk=pk)
    return render(request, 'bem_estar_animal/detalhe_evidencia.html', {'evidencia': evidencia})
