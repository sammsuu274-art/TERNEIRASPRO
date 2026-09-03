from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta


def dashboard(request):
    # Verificar se o usuário está autenticado
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if not request.propriedade_ativa:
        # Superusuário sem propriedade = primeiro acesso
        if request.user.is_superuser:
            return redirect('core:primeiro_acesso')
        # Usuário comum sem vínculo
        from accounts.models import UsuarioPerfil
        perfis = UsuarioPerfil.objects.filter(
            usuario=request.user, ativo=True
        ).select_related('propriedade')
        if not perfis.exists():
            return render(request, 'sem_propriedade.html')
        return render(request, 'selecionar_propriedade.html', {'perfis': perfis})

    prop = request.propriedade_ativa
    hoje = timezone.now().date()
    periodo = int(request.GET.get('periodo', 90))
    inicio_periodo = hoje - timedelta(days=periodo)

    ctx = {
        'periodo': periodo,
        'hoje': hoje,
    }

    ctx.update(_alertas_criticos(prop, hoje))
    ctx.update(_alertas_operacionais(prop, hoje))
    ctx.update(_status_desempenho(prop, inicio_periodo, hoje))
    ctx.update(_status_conformidade(prop, inicio_periodo, hoje))
    ctx.update(_status_sanitario(prop, inicio_periodo, hoje))
    ctx.update(_status_reprodutivo(prop))
    
    # Dados de tendência
    tendencia_data = _tendencia(prop, hoje)
    
    # Buscar metas/referenciais para os gráficos
    metas_data = _buscar_metas_graficos(prop)
    
    # Converte dados para JSON válido
    import json
    json_data = {}
    for key, value in tendencia_data.items():
        if isinstance(value, list):
            json_data[key + '_json'] = json.dumps(value)
    
    # Adiciona metas ao JSON
    for key, value in metas_data.items():
        if value is not None:
            json_data[key + '_json'] = json.dumps(value)
    
    ctx.update(tendencia_data)
    ctx.update(metas_data)
    ctx.update(json_data)

    return render(request, 'dashboard.html', ctx)


# ---------------------------------------------------------------------------
# ZONA 1-A — ALERTAS CRÍTICOS
# ---------------------------------------------------------------------------

def _alertas_criticos(prop, hoje):
    from animais.models import Animal
    from eventos.models import Parto, Colostragem, OcorrenciaSanitaria
    from indicadores.services import classificar_peso_vs_meta
    from config_tecnica.models import MetaDesenvolvimento

    alertas_criticos = []

    # A1 — Terneira sem colostragem após 2h do nascimento
    partos_recentes = Parto.objects.filter(
        ciclo__vaca__propriedade=prop,
        data_parto=hoje,
    ).select_related('terneira')

    for parto in partos_recentes:
        if not parto.hora_parto:
            continue
        tem_colostro = Colostragem.objects.filter(terneira=parto.terneira).exists()
        if tem_colostro:
            continue
        from datetime import datetime
        hora_nasc = timezone.make_aware(datetime.combine(parto.data_parto, parto.hora_parto))
        horas_desde = (timezone.now() - hora_nasc).total_seconds() / 3600
        if horas_desde >= 2:
            alertas_criticos.append({
                'tipo': 'colostragem_pendente',
                'icone': 'bi-droplet-half',
                'titulo': 'Colostragem pendente',
                'detalhe': f'{parto.terneira.identificacao} — {horas_desde:.1f}h sem colostro',
                'url': f'/eventos/colostragem/{parto.terneira.pk}/',
                'gravidade': 'critico',
            })

    # A2 — Ocorrência sanitária ativa há mais de 7 dias
    ocorrencias_antigas = OcorrenciaSanitaria.objects.filter(
        animal__propriedade=prop,
        data_fim__isnull=True,
        data_inicio__lte=hoje - timedelta(days=7),
    ).select_related('animal').order_by('data_inicio')[:10]

    for oc in ocorrencias_antigas:
        dias = (hoje - oc.data_inicio).days
        alertas_criticos.append({
            'tipo': 'ocorrencia_aberta',
            'icone': 'bi-heart-pulse',
            'titulo': f'{oc.get_tipo_display()} sem resolução',
            'detalhe': f'{oc.animal.identificacao} — {dias} dias em aberto',
            'url': f'/eventos/sanitario/{oc.pk}/encerrar/',
            'gravidade': 'critico',
        })

    # A3 — Terneiras abaixo de 90% do peso mínimo da curva
    terneiras_criticas = []
    terneiras_ativas = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha'],
        situacao='ativa',
        sexo='F',
    ).prefetch_related('pesagens')

    for terneira in terneiras_ativas:
        if not terneira.data_nascimento:
            continue
        ultima = terneira.pesagens.order_by('-data').first()
        if not ultima:
            continue
        meta = MetaDesenvolvimento.objects.filter(
            propriedade=prop, raca=terneira.raca, ativa=True,
        ).prefetch_related('pontos').first()
        if not meta:
            continue
        pontos = list(meta.pontos.filter(tipo='peso').order_by('idade_dias').values('idade_dias', 'valor_minimo'))
        if len(pontos) < 2:
            continue
        idade = terneira.idade_dias
        peso_min = _interpolar_simples(pontos, idade)
        if peso_min and float(ultima.peso_kg) < peso_min * 0.90:
            percentual = round(float(ultima.peso_kg) / peso_min * 100, 1)
            terneiras_criticas.append({
                'animal': terneira,
                'peso_atual': ultima.peso_kg,
                'peso_minimo': round(peso_min, 1),
                'percentual': percentual,
                'desvio': round(float(ultima.peso_kg) - peso_min, 1),
            })

    for t in terneiras_criticas[:5]:
        alertas_criticos.append({
            'tipo': 'peso_critico',
            'icone': 'bi-graph-down-arrow',
            'titulo': 'Peso crítico — abaixo de 90% da curva',
            'detalhe': f"{t['animal'].identificacao} — {t['peso_atual']}kg ({t['percentual']}% do mínimo)",
            'url': f"/animais/{t['animal'].pk}/",
            'gravidade': 'critico',
        })

    # A4 — Mortes recentes (últimos 7 dias)
    mortes_recentes = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha', 'bezerro'],
        situacao='morta',
        data_saida__gte=hoje - timedelta(days=7),
    ).order_by('-data_saida')[:5]

    for animal in mortes_recentes:
        alertas_criticos.append({
            'tipo': 'morte_recente',
            'icone': 'bi-x-circle',
            'titulo': 'Morte registrada',
            'detalhe': f'{animal.identificacao} — {animal.data_saida}',
            'url': f'/animais/{animal.pk}/',
            'gravidade': 'critico',
        })

    return {
        'alertas_criticos': alertas_criticos,
        'terneiras_criticas_detalhe': terneiras_criticas[:10],
    }


# ---------------------------------------------------------------------------
# ZONA 1-B — ALERTAS OPERACIONAIS
# ---------------------------------------------------------------------------

def _alertas_operacionais(prop, hoje):
    from animais.models import Animal, CicloReprodutivo
    from eventos.models import Parto, CuraUmbigo
    from programas.models import ProgramaAcompanhamento

    alertas_operacionais = []

    # A5 — Checkpoints de 6 meses pendentes
    programas_ativos = ProgramaAcompanhamento.objects.filter(
        terneira__propriedade=prop,
        status='em_andamento',
    ).select_related('terneira')

    checkpoints_pendentes = [p for p in programas_ativos if p.checkpoint_pendente]
    if checkpoints_pendentes:
        alertas_operacionais.append({
            'tipo': 'checkpoint_pendente',
            'icone': 'bi-clipboard2-pulse',
            'titulo': f'{len(checkpoints_pendentes)} checkpoint(s) de 6 meses pendente(s)',
            'detalhe': ', '.join(p.terneira.identificacao for p in checkpoints_pendentes[:3])
                       + ('...' if len(checkpoints_pendentes) > 3 else ''),
            'url': '/programas/',
            'gravidade': 'atencao',
            'lista': checkpoints_pendentes,
        })

    # A6 — Terneiras/novilhas sem pesagem nos últimos 30 dias
    sem_pesagem = []
    terneiras = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha'],
        situacao='ativa',
        sexo='F',
    ).prefetch_related('pesagens')

    for t in terneiras:
        ultima = t.pesagens.order_by('-data').first()
        if not ultima or (hoje - ultima.data).days > 30:
            dias = (hoje - ultima.data).days if ultima else None
            sem_pesagem.append({'animal': t, 'dias': dias})

    if sem_pesagem:
        alertas_operacionais.append({
            'tipo': 'sem_pesagem',
            'icone': 'bi-clipboard-data',
            'titulo': f'{len(sem_pesagem)} animal(is) sem pesagem nos últimos 30 dias',
            'detalhe': ', '.join(i['animal'].identificacao for i in sem_pesagem[:3])
                       + ('...' if len(sem_pesagem) > 3 else ''),
            'url': '/animais/',
            'gravidade': 'atencao',
            'lista': sem_pesagem[:10],
        })

    # A7 — Partos previstos nos próximos 7 dias sem pré-parto
    ciclos_sem_pre_parto = CicloReprodutivo.objects.filter(
        vaca__propriedade=prop,
        situacao='gestando',
        data_previsao_parto__range=(hoje, hoje + timedelta(days=7)),
        data_entrada_pre_parto__isnull=True,
    ).select_related('vaca')[:10]

    for ciclo in ciclos_sem_pre_parto:
        alertas_operacionais.append({
            'tipo': 'parto_sem_pre_parto',
            'icone': 'bi-calendar-event',
            'titulo': 'Parto previsto sem pré-parto registrado',
            'detalhe': f'{ciclo.vaca.identificacao} — prev. {ciclo.data_previsao_parto}',
            'url': f'/animais/vacas/{ciclo.vaca.pk}/',
            'gravidade': 'atencao',
        })

    # A9 — Umbigo sem cura nas primeiras horas
    partos_sem_umbigo = Parto.objects.filter(
        ciclo__vaca__propriedade=prop,
        data_parto=hoje,
    ).select_related('terneira')

    for parto in partos_sem_umbigo:
        if not parto.hora_parto:
            continue
        tem_cura = CuraUmbigo.objects.filter(terneira=parto.terneira).exists()
        if tem_cura:
            continue
        from datetime import datetime
        hora_nasc = timezone.make_aware(datetime.combine(parto.data_parto, parto.hora_parto))
        horas = (timezone.now() - hora_nasc).total_seconds() / 3600
        if horas >= 2:
            alertas_operacionais.append({
                'tipo': 'umbigo_pendente',
                'icone': 'bi-bandaid',
                'titulo': 'Cura de umbigo pendente',
                'detalhe': f'{parto.terneira.identificacao} — {horas:.1f}h sem cura',
                'url': f'/eventos/umbigo/{parto.terneira.pk}/',
                'gravidade': 'atencao',
            })

    # A10 — Novilhas com trajetória desfavorável
    from programas.models import ProjecaoReprodutiva
    desfavoraveis = ProjecaoReprodutiva.objects.filter(
        terneira__propriedade=prop,
        terneira__situacao='ativa',
        status_trajetoria='desfavoravel',
    ).select_related('terneira').order_by('-data_calculo')

    # Pega apenas a projeção mais recente por animal
    vistos = set()
    for proj in desfavoraveis:
        if proj.terneira_id in vistos:
            continue
        vistos.add(proj.terneira_id)
        alertas_operacionais.append({
            'tipo': 'trajetoria_desfavoravel',
            'icone': 'bi-graph-down',
            'titulo': 'Trajetória reprodutiva desfavorável',
            'detalhe': f"{proj.terneira.identificacao} — projeção {proj.data_calculo}",
            'url': f'/animais/{proj.terneira.pk}/',
            'gravidade': 'atencao',
        })
        if len(vistos) >= 5:
            break

    return {'alertas_operacionais': alertas_operacionais}


# ---------------------------------------------------------------------------
# ZONA 2-A — STATUS DE DESEMPENHO
# ---------------------------------------------------------------------------

def _status_desempenho(prop, inicio_periodo, hoje):
    from animais.models import Animal
    from eventos.models import Parto
    from indicadores.services import calcular_gmd

    # Incluir terneira E novilha (terneira após desaleitamento)
    n_terneiras_ativas = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha'],
        situacao='ativa',
        sexo='F',
    ).count()

    n_novilhas_ativas = Animal.objects.filter(
        propriedade=prop,
        categoria='novilha',
        situacao='ativa',
        sexo='F',
    ).count()

    n_nascimentos = Parto.objects.filter(
        ciclo__vaca__propriedade=prop,
        data_parto__range=(inicio_periodo, hoje),
    ).count()

    n_femeas = Parto.objects.filter(
        ciclo__vaca__propriedade=prop,
        data_parto__range=(inicio_periodo, hoje),
        terneira__sexo='F',
    ).count()

    n_machos = n_nascimentos - n_femeas

    # GMD médio no aleitamento — inclui terneira E novilha (que já foi terneira)
    from eventos.models import Desaleitamento
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
                float(pesagens[0].peso_kg), float(pesagens[-1].peso_kg),
                pesagens[0].data, pesagens[-1].data,
            )
            if gmd is not None:
                gmds.append(gmd)

    gmd_medio = round(sum(gmds) / len(gmds), 3) if gmds else None
    gmd_n = len(gmds)

    return {
        'n_terneiras_ativas': n_terneiras_ativas,
        'n_novilhas_ativas': n_novilhas_ativas,
        'n_nascimentos': n_nascimentos,
        'n_femeas': n_femeas,
        'n_machos': n_machos,
        'gmd_medio': gmd_medio,
        'gmd_n': gmd_n,
    }


# ---------------------------------------------------------------------------
# ZONA 2-B — STATUS DE CONFORMIDADE
# ---------------------------------------------------------------------------

def _status_conformidade(prop, inicio_periodo, hoje):
    from indicadores.models import ResultadoConformidade

    def _taxa(codigo_like):
        """Calcula taxa de conformidade para critérios cujo código começa com o prefixo."""
        qs = ResultadoConformidade.objects.filter(
            animal__propriedade=prop,
            data_evento__range=(inicio_periodo, hoje),
            criterio__codigo__startswith=codigo_like,
        )
        total = qs.filter(resultado__in=['conforme', 'nao_conforme']).count()
        conformes = qs.filter(resultado='conforme').count()
        sem_dado = qs.filter(resultado='dado_ausente').count()
        if total == 0:
            return {'percentual': None, 'total': 0, 'conformes': 0, 'sem_dado': sem_dado, 'confiavel': False}
        return {
            'percentual': round(conformes / total * 100, 1),
            'total': total,
            'conformes': conformes,
            'sem_dado': sem_dado,
            'confiavel': total >= 5,
        }

    def _taxa_peso():
        """Taxa de conformidade de peso por idade (usa meta_desenvolvimento em vez de criterio)."""
        qs = ResultadoConformidade.objects.filter(
            animal__propriedade=prop,
            data_evento__range=(inicio_periodo, hoje),
            criterio__isnull=True,
            meta_desenvolvimento__isnull=False,
        )
        total = qs.filter(resultado__in=['conforme', 'nao_conforme']).count()
        conformes = qs.filter(resultado='conforme').count()
        if total == 0:
            return {'percentual': None, 'total': 0, 'conformes': 0, 'confiavel': False}
        return {
            'percentual': round(conformes / total * 100, 1),
            'total': total,
            'conformes': conformes,
            'confiavel': total >= 5,
        }

    def _taxa_dias(codigo):
        qs = ResultadoConformidade.objects.filter(
            animal__propriedade=prop,
            data_evento__range=(inicio_periodo, hoje),
            criterio__codigo=codigo,
        )
        total = qs.filter(resultado__in=['conforme', 'nao_conforme']).count()
        conformes = qs.filter(resultado='conforme').count()
        sem_dado = qs.filter(resultado='dado_ausente').count()
        if total == 0:
            return {'percentual': None, 'total': 0, 'conformes': 0, 'sem_dado': sem_dado, 'confiavel': False}
        return {
            'percentual': round(conformes / total * 100, 1),
            'total': total,
            'conformes': conformes,
            'sem_dado': sem_dado,
            'confiavel': total >= 5,
        }

    return {
        'conf_colostro_tempo': _taxa('colostragem_tempo'),
        'conf_colostro_volume': _taxa('colostragem_volume'),
        'conf_colostro_brix': _taxa('colostragem_brix'),
        'conf_umbigo': _taxa('umbigo_tempo'),
        'conf_dias_secos_min': _taxa_dias('dias_secos_minimo'),
        'conf_dias_pre_parto': _taxa_dias('dias_pre_parto_minimo'),
        'conf_peso_idade': _taxa_peso(),
    }


# ---------------------------------------------------------------------------
# ZONA 2-C — STATUS SANITÁRIO
# ---------------------------------------------------------------------------

def _status_sanitario(prop, inicio_periodo, hoje):
    from animais.models import Animal
    from eventos.models import Parto, OcorrenciaSanitaria
    from indicadores.services import calcular_incidencia, calcular_mortalidade

    n_nascimentos = Parto.objects.filter(
        ciclo__vaca__propriedade=prop,
        data_parto__range=(inicio_periodo, hoje),
    ).count()

    mortes = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha', 'bezerro'],
        situacao='morta',
        data_saida__range=(inicio_periodo, hoje),
    ).count()

    terneiras_ids = Animal.objects.filter(
        propriedade=prop,
        categoria__in=['terneira', 'novilha'],
        situacao='ativa',
        sexo='F',
    ).values_list('id', flat=True)

    n_base = len(terneiras_ids)

    diarreia = OcorrenciaSanitaria.objects.filter(
        animal__in=terneiras_ids,
        tipo='diarreia',
        data_inicio__range=(inicio_periodo, hoje),
    ).values('animal').distinct().count()

    pneumonia = OcorrenciaSanitaria.objects.filter(
        animal__in=terneiras_ids,
        tipo='pneumonia',
        data_inicio__range=(inicio_periodo, hoje),
    ).values('animal').distinct().count()

    onfalite = OcorrenciaSanitaria.objects.filter(
        animal__in=terneiras_ids,
        tipo='onfalite',
        data_inicio__range=(inicio_periodo, hoje),
    ).values('animal').distinct().count()

    return {
        'mortalidade': calcular_mortalidade(n_nascimentos, mortes),
        'n_mortes': mortes,
        'inc_diarreia': calcular_incidencia(n_base, diarreia),
        'inc_pneumonia': calcular_incidencia(n_base, pneumonia),
        'inc_onfalite': calcular_incidencia(n_base, onfalite),
        'n_diarreia': diarreia,
        'n_pneumonia': pneumonia,
        'n_onfalite': onfalite,
    }


# ---------------------------------------------------------------------------
# ZONA 2-D — STATUS REPRODUTIVO
# ---------------------------------------------------------------------------

def _status_reprodutivo(prop):
    from animais.models import Animal
    from programas.models import ProgramaAcompanhamento, CheckpointSesMeses, ProjecaoReprodutiva

    n_novilhas = Animal.objects.filter(
        propriedade=prop, categoria='novilha',
        situacao='ativa', sexo='F',
    ).count()

    # Trajetórias das projeções mais recentes por animal
    from django.db.models import Max
    ultimas_proj = ProjecaoReprodutiva.objects.filter(
        terneira__propriedade=prop,
        terneira__situacao='ativa',
    ).values('terneira').annotate(ultima=Max('data_calculo'))

    favoravel = atencao = desfavoravel = insuficiente = 0
    for item in ultimas_proj:
        proj = ProjecaoReprodutiva.objects.filter(
            terneira_id=item['terneira'],
            data_calculo=item['ultima'],
        ).first()
        if proj:
            if proj.status_trajetoria == 'favoravel':
                favoravel += 1
            elif proj.status_trajetoria == 'atencao':
                atencao += 1
            elif proj.status_trajetoria == 'desfavoravel':
                desfavoravel += 1
            else:
                insuficiente += 1

    n_sem_projecao = n_novilhas - (favoravel + atencao + desfavoravel + insuficiente)

    # Checkpoints realizados vs. total de programas
    n_checkpoints = CheckpointSesMeses.objects.filter(
        programa__terneira__propriedade=prop,
    ).count()

    return {
        'n_novilhas': n_novilhas,
        'traj_favoravel': favoravel,
        'traj_atencao': atencao,
        'traj_desfavoravel': desfavoravel,
        'traj_insuficiente': insuficiente,
        'n_sem_projecao': max(n_sem_projecao, 0),
        'n_checkpoints': n_checkpoints,
    }


# ---------------------------------------------------------------------------
# ZONA 3 — TENDÊNCIA (últimos 6 meses)
# ---------------------------------------------------------------------------

def _tendencia(prop, hoje):
    from indicadores.models import ResultadoConformidade
    from animais.models import Animal
    from eventos.models import OcorrenciaSanitaria, Parto
    from indicadores.services import calcular_gmd

    meses = []
    labels = []

    for i in range(5, -1, -1):
        # Cada ponto = 1 mês
        fim = hoje.replace(day=1) - timedelta(days=1) if i > 0 else hoje
        for _ in range(i):
            fim = fim.replace(day=1) - timedelta(days=1)
        inicio = fim.replace(day=1)
        meses.append((inicio, fim))
        labels.append(inicio.strftime('%b/%y'))

    # T1 — Taxa de colostragem no tempo por mês
    t1_data = []
    for inicio, fim in meses:
        qs = ResultadoConformidade.objects.filter(
            animal__propriedade=prop,
            data_evento__range=(inicio, fim),
            criterio__codigo='colostragem_tempo',
        )
        total = qs.filter(resultado__in=['conforme', 'nao_conforme']).count()
        conformes = qs.filter(resultado='conforme').count()
        t1_data.append(round(conformes / total * 100, 1) if total > 0 else None)

    # T2 — GMD médio por mês de nascimento (terneiras nascidas naquele mês)
    t2_data = []
    for inicio, fim in meses:
        partos = Parto.objects.filter(
            ciclo__vaca__propriedade=prop,
            data_parto__range=(inicio, fim),
            terneira__sexo='F',
        ).select_related('terneira')
        gmds = []
        for parto in partos:
            pesagens = list(parto.terneira.pesagens.order_by('data'))
            if len(pesagens) >= 2:
                gmd = calcular_gmd(
                    float(pesagens[0].peso_kg), float(pesagens[-1].peso_kg),
                    pesagens[0].data, pesagens[-1].data,
                )
                if gmd is not None:
                    gmds.append(gmd)
        t2_data.append(round(sum(gmds) / len(gmds), 3) if gmds else None)

    # T3 — Incidência de diarreia + pneumonia por mês
    t3_diarreia = []
    t3_pneumonia = []
    for inicio, fim in meses:
        terneiras_ids = list(Animal.objects.filter(
            propriedade=prop,
            categoria__in=['terneira', 'novilha'],
            sexo='F',
        ).values_list('id', flat=True))
        n_base = max(len(terneiras_ids), 1)
        n_diarreia = OcorrenciaSanitaria.objects.filter(
            animal__in=terneiras_ids, tipo='diarreia',
            data_inicio__range=(inicio, fim),
        ).values('animal').distinct().count()
        n_pneumonia = OcorrenciaSanitaria.objects.filter(
            animal__in=terneiras_ids, tipo='pneumonia',
            data_inicio__range=(inicio, fim),
        ).values('animal').distinct().count()
        t3_diarreia.append(round(n_diarreia / n_base * 100, 1))
        t3_pneumonia.append(round(n_pneumonia / n_base * 100, 1))

    # T4 — % terneiras dentro da curva por coorte mensal
    t4_data = []
    for inicio, fim in meses:
        qs = ResultadoConformidade.objects.filter(
            animal__propriedade=prop,
            animal__data_nascimento__range=(inicio, fim),
            criterio__isnull=True,
            meta_desenvolvimento__isnull=False,
            resultado__in=['conforme', 'nao_conforme'],
        )
        total = qs.count()
        conformes = qs.filter(resultado='conforme').count()
        t4_data.append(round(conformes / total * 100, 1) if total > 0 else None)

    return {
        'tendencia_labels': labels,
        'tendencia_colostro': t1_data,
        'tendencia_gmd': t2_data,
        'tendencia_diarreia': t3_diarreia,
        'tendencia_pneumonia': t3_pneumonia,
        'tendencia_curva_peso': t4_data,
    }


# ---------------------------------------------------------------------------
# UTILITÁRIO INTERNO
# ---------------------------------------------------------------------------

def _interpolar_simples(pontos, idade_alvo):
    """Interpola valor mínimo da curva para a idade do animal."""
    for p in pontos:
        if p['idade_dias'] == idade_alvo:
            return float(p['valor_minimo'])
    for i in range(len(pontos) - 1):
        i0 = pontos[i]['idade_dias']
        i1 = pontos[i + 1]['idade_dias']
        if i0 <= idade_alvo <= i1:
            frac = (idade_alvo - i0) / (i1 - i0)
            v0 = float(pontos[i]['valor_minimo'])
            v1 = float(pontos[i + 1]['valor_minimo'])
            return round(v0 + frac * (v1 - v0), 2)
    return None


# ---------------------------------------------------------------------------
# BUSCAR METAS PARA GRÁFICOS
# ---------------------------------------------------------------------------

def _buscar_metas_graficos(prop):
    """Busca metas técnicas para exibir nos gráficos como linhas de referência."""
    from config_tecnica.models import CriterioConformidade, ReferencialTecnico
    
    metas = {}
    
    # Meta 1: Taxa de colostragem ≤ 2h - busca do referencial técnico
    try:
        ref_colostro = ReferencialTecnico.objects.filter(
            indicador='tempo_ate_colostragem',
            ativo=True
        ).first()
        # Se temos referencial de 2h como crítico, assumimos meta de 90% de conformidade
        metas['meta_colostro_tempo'] = 90.0
    except:
        metas['meta_colostro_tempo'] = 90.0
    
    # Meta 2: GMD no aleitamento - busca do referencial
    try:
        ref_gmd = ReferencialTecnico.objects.filter(
            indicador__in=['gmd_aleitamento', 'gmd_aleitamento_holandes'],
            ativo=True
        ).first()
        if ref_gmd and ref_gmd.valor_ideal:
            metas['meta_gmd'] = float(ref_gmd.valor_ideal)
        else:
            metas['meta_gmd'] = 0.75  # Fallback para Holandês padrão
    except:
        metas['meta_gmd'] = 0.75
    
    # Meta 3: Incidência sanitária - busca dos referenciais
    try:
        ref_diarreia = ReferencialTecnico.objects.filter(
            indicador='incidencia_diarreia',
            ativo=True
        ).first()
        metas['meta_diarreia'] = float(ref_diarreia.valor_ideal) if ref_diarreia and ref_diarreia.valor_ideal else 15.0
        
        ref_pneumonia = ReferencialTecnico.objects.filter(
            indicador='incidencia_pneumonia', 
            ativo=True
        ).first()
        metas['meta_pneumonia'] = float(ref_pneumonia.valor_ideal) if ref_pneumonia and ref_pneumonia.valor_ideal else 10.0
    except:
        metas['meta_diarreia'] = 15.0
        metas['meta_pneumonia'] = 10.0
    
    # Meta 4: % terneiras na curva de peso - configurável
    try:
        # Busca critério específico para conformidade de peso
        criterio_peso = CriterioConformidade.objects.filter(
            propriedade=prop,
            codigo='peso_por_idade',
            ativo=True
        ).first()
        # Meta de conformidade geral para peso/idade
        metas['meta_curva_peso'] = 80.0  # 80% é uma meta técnica razoável
    except:
        metas['meta_curva_peso'] = 80.0
    
    return metas
