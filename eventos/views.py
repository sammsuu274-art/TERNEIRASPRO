from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from animais.models import Animal, CicloReprodutivo
from .models import (
    Parto, Colostragem, CuraUmbigo, Pesagem,
    OcorrenciaSanitaria, Vacinacao, Desaleitamento, BancoColostro,
)
from .forms import (
    PartoForm, ColostragemmForm, CuraUmbigoForm, PesagemForm, PesagemComplementarForm,
    OcorrenciaSanitariaForm, EncerrarOcorrenciaForm,
    VacinacaoForm, DesaleitamentoForm, BancoColostroForm,
)
from core.decorators import papel_minimo_required, admin_only, admin_ou_tecnico


def _prop(request):
    return request.propriedade_ativa


def _get_terneira(request, pk):
    return get_object_or_404(Animal, pk=pk, propriedade=_prop(request))


# ─── PARTO ────────────────────────────────────────────────────────────────────

@login_required
@admin_ou_tecnico
def registrar_parto(request, ciclo_pk):
    prop = _prop(request)
    ciclo = get_object_or_404(CicloReprodutivo, pk=ciclo_pk, vaca__propriedade=prop)

    if hasattr(ciclo, 'parto'):
        messages.warning(request, 'Este ciclo já possui um parto registrado.')
        return redirect('animais:detalhe_vaca', pk=ciclo.vaca.pk)

    if request.method == 'POST':
        # Dados da terneira
        identificacao = request.POST.get('identificacao', '').strip()
        sexo = request.POST.get('sexo', 'F')
        raca = request.POST.get('raca', ciclo.vaca.raca)

        form = PartoForm(request.POST)
        if form.is_valid() and identificacao:
            # Cria o animal nascido
            animal = Animal.objects.create(
                propriedade=prop,
                identificacao=identificacao,
                sexo=sexo,
                raca=raca,
                categoria='terneira' if sexo == 'F' else 'bezerro',
                data_nascimento=form.cleaned_data['data_parto'],
                mae=ciclo.vaca,
                pai_identificacao=ciclo.touro_semen or '',
            )
            # Cria o parto
            parto = form.save(commit=False)
            parto.ciclo = ciclo
            parto.terneira = animal
            parto.registrado_por = request.user
            parto.save()

            # Atualiza situação do ciclo
            ciclo.situacao = 'encerrado_parto'
            ciclo.save()

            # Cria programa de acompanhamento para fêmeas
            if sexo == 'F':
                from programas.models import ProgramaAcompanhamento
                ProgramaAcompanhamento.objects.create(
                    terneira=animal,
                    data_inicio=form.cleaned_data['data_parto'],
                )

            # ── Avaliação de conformidade do parto (dias secos + pré-parto)
            from indicadores.avaliadores import avaliar_evento_parto
            avaliar_evento_parto(parto)

            messages.success(request, f'Parto registrado. Animal {identificacao} criado.')
            if sexo == 'F':
                return redirect('animais:detalhe_terneira', pk=animal.pk)
            return redirect('animais:detalhe_vaca', pk=ciclo.vaca.pk)
    else:
        form = PartoForm()

    return render(request, 'eventos/form_parto.html', {
        'form': form,
        'ciclo': ciclo,
    })


# ─── COLOSTRAGEM ─────────────────────────────────────────────────────────────

@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def registrar_colostragem(request, terneira_pk):
    prop = _prop(request)
    terneira = _get_terneira(request, terneira_pk)

    # Calcular meta de volume (10% do peso vivo)
    meta_volume = None
    if hasattr(terneira, 'parto_origem') and terneira.parto_origem and terneira.parto_origem.peso_nascimento:
        meta_volume = int(terneira.parto_origem.peso_nascimento * 100)  # 10% convertido para ml
    elif terneira.pesagens.exists():
        primeira_pesagem = terneira.pesagens.order_by('data').first()
        if primeira_pesagem.peso_kg:
            meta_volume = int(primeira_pesagem.peso_kg * 100)  # 10% convertido para ml

    if request.method == 'POST':
        form = ColostragemmForm(request.POST, propriedade=prop)
        if form.is_valid():
            col = form.save(commit=False)
            col.terneira = terneira
            col.responsavel = request.user
            col.save()
            # ── Avaliação de conformidade da colostragem (tempo, volume, brix)
            from indicadores.avaliadores import avaliar_evento_colostragem
            avaliar_evento_colostragem(col)
            messages.success(request, 'Colostragem registrada.')
            return redirect('animais:detalhe_terneira', pk=terneira_pk)
    else:
        from django.utils import timezone
        form = ColostragemmForm(
            propriedade=prop,
            initial={'data_hora': timezone.now().strftime('%Y-%m-%dT%H:%M')},
        )

    colostragens = terneira.colostragens.order_by('data_hora')
    return render(request, 'eventos/form_colostragem.html', {
        'form': form,
        'terneira': terneira,
        'colostragens': colostragens,
        'meta_volume': meta_volume,
    })


@login_required
@admin_ou_tecnico
def editar_colostragem(request, pk):
    """Permite edição limitada de colostragem com recálculo de conformidades."""
    prop = _prop(request)
    col = get_object_or_404(Colostragem, pk=pk, terneira__propriedade=prop)
    
    # Só permite edição nas primeiras 24h após registro
    from django.utils import timezone
    if (timezone.now() - col.created_at).total_seconds() > 24 * 3600:
        messages.error(request, 'Colostragem só pode ser editada nas primeiras 24 horas.')
        return redirect('animais:detalhe_terneira', pk=col.terneira.pk)
    
    if request.method == 'POST':
        form = ColostragemmForm(request.POST, instance=col, propriedade=prop)
        if form.is_valid():
            form.save()
            
            # Recalcular conformidades
            from indicadores.models import ResultadoConformidade
            ResultadoConformidade.objects.filter(
                animal=col.terneira,
                evento_tipo='colostragem',
                evento_id=col.pk
            ).delete()
            
            from indicadores.avaliadores import avaliar_evento_colostragem
            avaliar_evento_colostragem(col)
            
            messages.success(request, 'Colostragem atualizada e conformidades recalculadas.')
            return redirect('animais:detalhe_terneira', pk=col.terneira.pk)
    else:
        form = ColostragemmForm(instance=col, propriedade=prop)
    
    return render(request, 'eventos/form_colostragem.html', {
        'form': form,
        'terneira': col.terneira,
        'editando': True,
        'colostragem': col,
    })


def lista_colostragens(request, terneira_pk):
    terneira = _get_terneira(request, terneira_pk)
    return render(request, 'eventos/lista_colostragens.html', {
        'terneira': terneira,
        'colostragens': terneira.colostragens.order_by('data_hora'),
    })


@login_required
@admin_only
def excluir_colostragem(request, pk):
    """Permite exclusão de colostragem com confirmação."""
    prop = _prop(request)
    col = get_object_or_404(Colostragem, pk=pk, terneira__propriedade=prop)
    
    if request.method == 'POST':
        terneira_pk = col.terneira.pk
        
        # Remover conformidades relacionadas
        from indicadores.models import ResultadoConformidade
        ResultadoConformidade.objects.filter(
            animal=col.terneira,
            evento_tipo='colostragem',
            evento_id=col.pk
        ).delete()
        
        col.delete()
        messages.success(request, 'Colostragem excluída com sucesso.')
        return redirect('animais:detalhe_terneira', pk=terneira_pk)
    
    return render(request, 'eventos/confirmar_exclusao.html', {
        'objeto': col,
        'tipo': 'Colostragem',
        'detalhes': f'{col.volume_ml}ml em {col.data_hora.strftime("%d/%m/%Y %H:%M")}',
        'animal': col.terneira,
    })


# ─── UMBIGO ───────────────────────────────────────────────────────────────────

@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def registrar_cura_umbigo(request, terneira_pk):
    terneira = _get_terneira(request, terneira_pk)

    if request.method == 'POST':
        form = CuraUmbigoForm(request.POST)
        if form.is_valid():
            cura = form.save(commit=False)
            cura.terneira = terneira
            cura.responsavel = request.user
            cura.save()
            # ── Avaliação de conformidade do umbigo (tempo)
            from indicadores.avaliadores import avaliar_evento_cura_umbigo
            avaliar_evento_cura_umbigo(cura)
            messages.success(request, 'Cura de umbigo registrada.')
            return redirect('animais:detalhe_terneira', pk=terneira_pk)
    else:
        from django.utils import timezone
        form = CuraUmbigoForm(
            initial={'data_hora': timezone.now().strftime('%Y-%m-%dT%H:%M')}
        )

    return render(request, 'eventos/form_umbigo.html', {
        'form': form,
        'terneira': terneira,
        'historico': terneira.curas_umbigo.order_by('data_hora'),
    })


# ─── PESAGEM ──────────────────────────────────────────────────────────────────

@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def registrar_pesagem(request, animal_pk):
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)

    if request.method == 'POST':
        form = PesagemForm(request.POST)
        if form.is_valid():
            pesagem = form.save(commit=False)
            pesagem.animal = animal
            pesagem.responsavel = request.user
            pesagem.save()
            # ── Avaliação de conformidade do peso por idade
            from indicadores.avaliadores import avaliar_evento_pesagem
            avaliar_evento_pesagem(pesagem)
            messages.success(request, f'Pesagem registrada: {pesagem.peso_kg} kg.')
            if animal.sexo == 'F' and animal.categoria in ['terneira', 'novilha']:
                return redirect('animais:detalhe_terneira', pk=animal_pk)
            return redirect('animais:detalhe_vaca', pk=animal_pk)
    else:
        from django.utils import timezone
        form = PesagemForm(initial={'data': timezone.now().date().strftime('%Y-%m-%d')})

    pesagens = animal.pesagens.order_by('-data')[:10]
    return render(request, 'eventos/form_pesagem.html', {
        'form': form,
        'animal': animal,
        'pesagens': pesagens,
    })


def historico_pesagens(request, animal_pk):
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)
    pesagens = animal.pesagens.order_by('data')
    return render(request, 'eventos/historico_pesagens.html', {
        'animal': animal,
        'pesagens': pesagens,
    })


@login_required
@admin_only
def excluir_pesagem(request, pk):
    """Permite exclusão de pesagem com confirmação."""
    prop = _prop(request)
    pesagem = get_object_or_404(Pesagem, pk=pk, animal__propriedade=prop)
    
    if request.method == 'POST':
        animal_pk = pesagem.animal.pk
        
        # Remover conformidades relacionadas
        from indicadores.models import ResultadoConformidade
        ResultadoConformidade.objects.filter(
            animal=pesagem.animal,
            evento_tipo='pesagem',
            evento_id=pesagem.pk
        ).delete()
        
        pesagem.delete()
        messages.success(request, 'Pesagem excluída com sucesso.')
        
        if pesagem.animal.sexo == 'F' and pesagem.animal.categoria in ['terneira', 'novilha']:
            return redirect('animais:detalhe_terneira', pk=animal_pk)
        return redirect('animais:detalhe_vaca', pk=animal_pk)
    
    return render(request, 'eventos/confirmar_exclusao.html', {
        'objeto': pesagem,
        'tipo': 'Pesagem',
        'detalhes': f'{pesagem.peso_kg}kg em {pesagem.data.strftime("%d/%m/%Y")}',
        'animal': pesagem.animal,
    })


# ─── OCORRÊNCIA SANITÁRIA ─────────────────────────────────────────────────────

@login_required
@admin_ou_tecnico
def registrar_ocorrencia(request, animal_pk):
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)

    if request.method == 'POST':
        form = OcorrenciaSanitariaForm(request.POST)
        if form.is_valid():
            oc = form.save(commit=False)
            oc.animal = animal
            oc.responsavel_tecnico = request.user
            oc.save()
            messages.success(request, 'Ocorrência registrada.')
            if animal.sexo == 'F':
                return redirect('animais:detalhe_terneira', pk=animal_pk)
            return redirect('animais:detalhe_vaca', pk=animal_pk)
    else:
        from django.utils import timezone
        form = OcorrenciaSanitariaForm(initial={'data_inicio': timezone.now().date().strftime('%Y-%m-%d')})

    return render(request, 'eventos/form_ocorrencia.html', {
        'form': form,
        'animal': animal,
    })


@login_required
@admin_ou_tecnico
def encerrar_ocorrencia(request, pk):
    prop = _prop(request)
    oc = get_object_or_404(OcorrenciaSanitaria, pk=pk, animal__propriedade=prop)

    if request.method == 'POST':
        form = EncerrarOcorrenciaForm(request.POST, instance=oc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ocorrência encerrada.')
            return redirect('animais:detalhe_terneira', pk=oc.animal.pk)
    else:
        from django.utils import timezone
        form = EncerrarOcorrenciaForm(instance=oc, initial={'data_fim': timezone.now().date().strftime('%Y-%m-%d')})

    return render(request, 'eventos/form_encerrar_ocorrencia.html', {'form': form, 'ocorrencia': oc})


# ─── VACINAÇÃO ────────────────────────────────────────────────────────────────

@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def registrar_vacinacao(request, animal_pk):
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)

    if request.method == 'POST':
        form = VacinacaoForm(request.POST)
        if form.is_valid():
            vac = form.save(commit=False)
            vac.animal = animal
            vac.responsavel = request.user
            vac.save()
            messages.success(request, 'Vacinação registrada.')
            return redirect('animais:detalhe_terneira', pk=animal_pk)
    else:
        from django.utils import timezone
        form = VacinacaoForm(initial={'data': timezone.now().date().strftime('%Y-%m-%d')})

    return render(request, 'eventos/form_vacinacao.html', {'form': form, 'animal': animal})


# ─── DESALEITAMENTO ───────────────────────────────────────────────────────────

@login_required
@admin_ou_tecnico
def registrar_desaleitamento(request, terneira_pk):
    terneira = _get_terneira(request, terneira_pk)

    if hasattr(terneira, 'desaleitamento'):
        messages.info(request, 'Esta terneira já foi desaleitada.')
        return redirect('animais:detalhe_terneira', pk=terneira_pk)

    if request.method == 'POST':
        form = DesaleitamentoForm(request.POST)
        if form.is_valid():
            d = form.save(commit=False)
            d.terneira = terneira
            d.responsavel = request.user
            d.save()
            # Atualiza categoria para novilha
            terneira.categoria = 'novilha'
            terneira.save(update_fields=['categoria'])
            messages.success(request, 'Desaleitamento registrado. Categoria atualizada para Novilha.')
            return redirect('animais:detalhe_terneira', pk=terneira_pk)
    else:
        from django.utils import timezone
        form = DesaleitamentoForm(initial={'data': timezone.now().date().strftime('%Y-%m-%d')})

    return render(request, 'eventos/form_desaleitamento.html', {'form': form, 'terneira': terneira})


# ─── BANCO DE COLOSTRO ────────────────────────────────────────────────────────

@login_required
def lista_banco_colostro(request):
    prop = _prop(request)
    if not prop:
        return redirect('/')
    banco = BancoColostro.objects.filter(propriedade=prop).order_by('-data_coleta')
    return render(request, 'eventos/lista_banco_colostro.html', {'banco': banco})


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def novo_banco_colostro(request):
    prop = _prop(request)
    if request.method == 'POST':
        form = BancoColostroForm(request.POST, propriedade=prop)
        if form.is_valid():
            b = form.save(commit=False)
            b.propriedade = prop
            b.save()
            messages.success(request, 'Colostro registrado no banco.')
            return redirect('eventos:lista_banco_colostro')
    else:
        from django.utils import timezone
        form = BancoColostroForm(
            propriedade=prop,
            initial={'data_coleta': timezone.now().date().strftime('%Y-%m-%d')},
        )
    return render(request, 'eventos/form_banco_colostro.html', {'form': form})


# ─── MOVIMENTAÇÃO DE LOTES ─────────────────────────────────────────────────────

@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor')
def mover_animal_lote(request, animal_pk):
    """Permite movimentar animal entre lotes."""
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)
    
    from animais.models import Lote, MovimentacaoLote
    from animais.forms import MovimentacaoLoteForm
    
    if request.method == 'POST':
        form = MovimentacaoLoteForm(request.POST, propriedade=prop)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.animal = animal
            mov.registrado_por = request.user
            mov.save()
            messages.success(request, f'{animal.identificacao} movido para {mov.lote.nome}.')
            if animal.sexo == 'F' and animal.categoria in ['terneira', 'novilha']:
                return redirect('animais:detalhe_terneira', pk=animal_pk)
            return redirect('animais:detalhe_vaca', pk=animal_pk)
    else:
        from django.utils import timezone
        form = MovimentacaoLoteForm(
            propriedade=prop,
            initial={'data': timezone.now().date().strftime('%Y-%m-%d')}
        )
    
    # Histórico de movimentações
    historico = MovimentacaoLote.objects.filter(
        animal=animal
    ).select_related('lote').order_by('-data')[:10]
    
    return render(request, 'eventos/form_movimentacao_lote.html', {
        'form': form,
        'animal': animal,
        'historico': historico,
    })


@login_required
@papel_minimo_required('admin', 'tecnico', 'produtor', 'auxiliar')
def registrar_pesagem_complementar(request, animal_pk):
    """Formulário com medições complementares opcionais."""
    prop = _prop(request)
    animal = get_object_or_404(Animal, pk=animal_pk, propriedade=prop)

    if request.method == 'POST':
        form = PesagemComplementarForm(request.POST)
        if form.is_valid():
            pesagem = form.save(commit=False)
            pesagem.animal = animal
            pesagem.responsavel = request.user
            pesagem.save()
            from indicadores.avaliadores import avaliar_evento_pesagem
            avaliar_evento_pesagem(pesagem)
            messages.success(request, f'Pesagem complementar registrada: {pesagem.peso_kg} kg.')
            if animal.sexo == 'F' and animal.categoria in ['terneira', 'novilha']:
                return redirect('animais:detalhe_terneira', pk=animal_pk)
            return redirect('animais:detalhe_vaca', pk=animal_pk)
    else:
        from django.utils import timezone
        form = PesagemComplementarForm(initial={'data': timezone.now().date().strftime('%Y-%m-%d')})

    pesagens = animal.pesagens.order_by('-data')[:10]
    return render(request, 'eventos/form_pesagem_complementar.html', {
        'form': form,
        'animal': animal,
        'pesagens': pesagens,
    })