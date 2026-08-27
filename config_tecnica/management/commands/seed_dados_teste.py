"""
Comando: python manage.py seed_dados_teste --propriedade 1

Gera dados realistas de teste:
- 30 vacas matrizes (diversas raças)
- 20 vacas em ciclo reprodutivo (pré-parto, secagem)
- ~50 partos com terneiras e bezerros
- Colostragens, curas de umbigo, pesagens, ocorrências sanitárias
- Programas de acompanhamento e projeções
"""

import random
from datetime import date, timedelta, datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone


RACAS_FEMEAS = ['holandes', 'jersey', 'girolando', 'mestaca', 'pardo_suico']
RACAS_PESOS_NASCIMENTO = {
    'holandes': (38, 46),
    'jersey': (22, 28),
    'girolando': (32, 40),
    'mestaca': (28, 38),
    'pardo_suico': (36, 44),
}
NOMES_VACAS = [
    'Mimosa', 'Bela', 'Estrela', 'Rosa', 'Flor', 'Princesa', 'Diana', 'Aurora',
    'Lua', 'Sol', 'Branca', 'Negra', 'Pinta', 'Malhada', 'Caramela', 'Dourada',
    'Cristal', 'Perola', 'Safira', 'Rubi', 'Jade', 'Opala', 'Topazio', 'Ametista',
    'Violeta', 'Margarida', 'Girassol', 'Orquidea', 'Gardenia', 'Bromélia',
]
TOUROS = [
    'Campeão 4750', 'Destaque FIV', 'Supremo J34', 'Rei do Vale 2200',
    'Atleta 8820', 'Fenômeno 1100', 'Ouro Negro 550',
]


def rand_date(inicio, fim):
    delta = (fim - inicio).days
    if delta <= 0:
        return inicio
    return inicio + timedelta(days=random.randint(0, delta))


def rand_decimal(minv, maxv, casas=2):
    return round(random.uniform(minv, maxv), casas)


class Command(BaseCommand):
    help = 'Gera dados de teste realistas para a propriedade'

    def add_arguments(self, parser):
        parser.add_argument('--propriedade', type=int, default=1)
        parser.add_argument('--limpar', action='store_true',
                            help='Remove dados de teste anteriores antes de inserir')

    def handle(self, *args, **options):
        from core.models import Propriedade
        from accounts.models import Usuario
        from animais.models import Animal, Lote, CicloReprodutivo, MovimentacaoLote
        from eventos.models import (
            Parto, Colostragem, CuraUmbigo, Pesagem,
            OcorrenciaSanitaria, Vacinacao, Desaleitamento, BancoColostro,
        )
        from programas.models import ProgramaAcompanhamento

        try:
            prop = Propriedade.objects.get(pk=options['propriedade'])
        except Propriedade.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Propriedade {options["propriedade"]} não encontrada.'))
            return

        admin = Usuario.objects.filter(is_superuser=True).first()
        hoje = date.today()

        if options['limpar']:
            self._limpar(prop)
            self.stdout.write('Dados anteriores removidos.')

        self.stdout.write(f'Gerando dados para: {prop.nome}')

        # Lotes
        lotes = self._criar_lotes(prop)
        self.stdout.write(f'  Lotes: {len(lotes)} criados')

        # Vacas matrizes
        vacas = self._criar_vacas(prop, lotes, admin)
        self.stdout.write(f'  Vacas matrizes: {len(vacas)} criadas')

        # Banco de colostro
        banco = self._criar_banco_colostro(prop, vacas)
        self.stdout.write(f'  Banco de colostro: {len(banco)} entradas')

        # Ciclos e partos (passados — terneiras já nascidas)
        partos_realizados = self._criar_partos_passados(prop, vacas, lotes, banco, admin, hoje)
        self.stdout.write(f'  Partos realizados: {partos_realizados} (terneiras + bezerros)')

        # Ciclos em gestação (pré-parto / secagem)
        em_gestacao = self._criar_gestacoes_ativas(prop, vacas, lotes, hoje)
        self.stdout.write(f'  Gestações ativas: {em_gestacao}')

        self.stdout.write(self.style.SUCCESS(
            f'\nConcluído! Acesse http://127.0.0.1:8000 para ver os dados.'
        ))

    def _limpar(self, prop):
        from animais.models import Animal, Lote, MovimentacaoLote, CicloReprodutivo
        from eventos.models import (
            Parto, Colostragem, CuraUmbigo, Pesagem,
            OcorrenciaSanitaria, Vacinacao, Desaleitamento, BancoColostro,
        )
        from programas.models import (
            ProgramaAcompanhamento, CheckpointSesMeses,
            ProjecaoReprodutiva, CoberturaIA,
        )
        # Remove na ordem correta (FK)
        CoberturaIA.objects.filter(terneira__propriedade=prop).delete()
        ProjecaoReprodutiva.objects.filter(terneira__propriedade=prop).delete()
        CheckpointSesMeses.objects.filter(
            programa__terneira__propriedade=prop).delete()
        ProgramaAcompanhamento.objects.filter(
            terneira__propriedade=prop).delete()
        Desaleitamento.objects.filter(terneira__propriedade=prop).delete()
        OcorrenciaSanitaria.objects.filter(animal__propriedade=prop).delete()
        Vacinacao.objects.filter(animal__propriedade=prop).delete()
        Pesagem.objects.filter(animal__propriedade=prop).delete()
        CuraUmbigo.objects.filter(terneira__propriedade=prop).delete()
        Colostragem.objects.filter(terneira__propriedade=prop).delete()
        Parto.objects.filter(ciclo__vaca__propriedade=prop).delete()
        CicloReprodutivo.objects.filter(vaca__propriedade=prop).delete()
        BancoColostro.objects.filter(propriedade=prop).delete()
        MovimentacaoLote.objects.filter(animal__propriedade=prop).delete()
        Animal.objects.filter(propriedade=prop).delete()
        Lote.objects.filter(propriedade=prop).delete()

    def _criar_lotes(self, prop):
        from animais.models import Lote
        tipos = [
            ('Pré-Parto', 'pre_parto'),
            ('Maternidade', 'maternidade'),
            ('Aleitamento A', 'aleitamento'),
            ('Aleitamento B', 'aleitamento'),
            ('Pós-Desaleitamento', 'pos_desaleitamento'),
            ('Recria 1', 'recria'),
            ('Recria 2', 'recria'),
            ('Vacas Lactação', 'vacas'),
            ('Vacas Secas', 'secas'),
        ]
        lotes = {}
        for nome, tipo in tipos:
            lote, _ = Lote.objects.get_or_create(
                propriedade=prop, nome=nome,
                defaults={'tipo': tipo, 'ativo': True},
            )
            lotes[tipo] = lotes.get(tipo) or lote
            lotes[nome] = lote
        return lotes

    def _criar_vacas(self, prop, lotes, admin):
        from animais.models import Animal, MovimentacaoLote
        vacas = []
        hoje = date.today()
        for i, nome in enumerate(NOMES_VACAS):
            raca = random.choice(RACAS_FEMEAS)
            brinco = f'V{1000 + i:04d}'
            nasc = hoje - timedelta(days=random.randint(730, 2920))  # 2–8 anos
            vaca, created = Animal.objects.get_or_create(
                propriedade=prop, identificacao=brinco,
                defaults={
                    'nome': nome, 'sexo': 'F', 'raca': raca,
                    'categoria': 'vaca', 'data_nascimento': nasc,
                    'situacao': 'ativa',
                },
            )
            if created:
                lote = lotes.get('Vacas Lactação')
                if lote:
                    MovimentacaoLote.objects.create(
                        animal=vaca, lote=lote,
                        data=nasc + timedelta(days=random.randint(400, 600)),
                        registrado_por=admin,
                    )
            vacas.append(vaca)
        return vacas

    def _criar_banco_colostro(self, prop, vacas):
        from eventos.models import BancoColostro
        banco = []
        hoje = date.today()
        for i in range(15):
            vaca = random.choice(vacas)
            data_col = hoje - timedelta(days=random.randint(5, 180))
            brix = rand_decimal(18, 32, 1)
            volume = random.randint(1500, 4000)
            congelado = random.random() > 0.3
            status = 'disponivel' if random.random() > 0.4 else 'utilizado'
            b = BancoColostro.objects.create(
                propriedade=prop,
                data_coleta=data_col,
                vaca_origem=vaca,
                brix=brix,
                volume_ml=volume,
                congelado=congelado,
                data_congelamento=data_col if congelado else None,
                lote=f'BC{i+1:03d}',
                validade=data_col + timedelta(days=365) if congelado else None,
                local_armazenamento='Freezer Maternidade' if congelado else 'Geladeira',
                status=status,
            )
            banco.append(b)
        return banco

    def _criar_partos_passados(self, prop, vacas, lotes, banco, admin, hoje):
        from animais.models import Animal, CicloReprodutivo, MovimentacaoLote
        from eventos.models import (
            Parto, Colostragem, CuraUmbigo, Pesagem,
            OcorrenciaSanitaria, Vacinacao, Desaleitamento,
        )
        from programas.models import ProgramaAcompanhamento
        from indicadores.avaliadores import (
            avaliar_evento_parto, avaliar_evento_colostragem,
            avaliar_evento_cura_umbigo, avaliar_evento_pesagem,
        )

        total = 0
        vacas_para_parto = random.sample(vacas, min(25, len(vacas)))

        for idx, vaca in enumerate(vacas_para_parto):
            # Partos recentes: 10 de julho/agosto 2026 (terneiras novas)
            # Partos históricos: 15 de janeiro a junho 2026 (novilhas + histórico gráficos)
            if idx < 10:
                inicio = date(2026, 7, 1)
                fim = hoje - timedelta(days=1)
            else:
                inicio = date(2026, 1, 1)
                fim = date(2026, 6, 30)
            data_parto = rand_date(inicio, fim)
            raca = vaca.raca
            lactacao = random.randint(1, 5)

            # Ciclo reprodutivo
            data_secagem = data_parto - timedelta(days=random.randint(40, 85))
            data_pre_parto = data_parto - timedelta(days=random.randint(14, 35))

            ciclo = CicloReprodutivo.objects.create(
                vaca=vaca,
                numero_lactacao=lactacao,
                data_cobertura=data_parto - timedelta(days=280),
                touro_semen=random.choice(TOUROS),
                data_previsao_parto=data_parto + timedelta(days=random.randint(-3, 3)),
                data_secagem=data_secagem,
                tratamento_secagem=random.choice(['Vaca Seca Total', 'Secagem Seletiva']),
                data_entrada_pre_parto=data_pre_parto,
                lote_pre_parto=lotes.get('Pré-Parto'),
                ecc_entrada_pre_parto=rand_decimal(2.5, 4.0, 1),
                situacao='encerrado_parto',
            )

            # Sexo do filhote (55% fêmeas, 45% machos)
            sexo = 'F' if random.random() < 0.55 else 'M'
            categoria = 'terneira' if sexo == 'F' else 'bezerro'
            brinco = f'T{2000 + idx:04d}' if sexo == 'F' else f'B{3000 + idx:04d}'
            peso_min, peso_max = RACAS_PESOS_NASCIMENTO.get(raca, (30, 42))
            peso_nasc = rand_decimal(peso_min, peso_max, 1)

            # Cria o animal
            filhote = Animal.objects.create(
                propriedade=prop,
                identificacao=brinco,
                sexo=sexo,
                raca=raca,
                categoria=categoria,
                data_nascimento=data_parto,
                mae=vaca,
                pai_identificacao=ciclo.touro_semen,
                situacao='ativa',
            )

            # Parto
            hora_parto = datetime.combine(
                data_parto,
                datetime.min.time().replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59),
                ),
            )
            gemelar = random.random() < 0.05
            facilidade = random.choices([0, 1, 2, 3], weights=[65, 20, 12, 3])[0]
            parto = Parto.objects.create(
                ciclo=ciclo,
                terneira=filhote,
                data_parto=data_parto,
                hora_parto=hora_parto.time(),
                facilidade=facilidade,
                assistencia=facilidade > 0,
                gemelar=gemelar,
                peso_nascimento=peso_nasc,
                vitalidade=random.choices(
                    ['normal', 'lento', 'fraco', 'sem_vida'],
                    weights=[80, 12, 6, 2]
                )[0],
                tempo_levantar_min=random.randint(5, 90) if random.random() > 0.3 else None,
                registrado_por=admin,
            )
            avaliar_evento_parto(parto)

            if sexo == 'F':
                lote_aleit = lotes.get('Aleitamento A')
                if lote_aleit:
                    MovimentacaoLote.objects.create(
                        animal=filhote, lote=lote_aleit,
                        data=data_parto, registrado_por=admin,
                    )
                prog = ProgramaAcompanhamento.objects.create(
                    terneira=filhote, data_inicio=data_parto,
                )
                self._gerar_eventos_terneira(
                    filhote, parto, prog, banco, lotes,
                    admin, hoje, data_parto,
                    avaliar_evento_colostragem,
                    avaliar_evento_cura_umbigo,
                    avaliar_evento_pesagem,
                )
            total += 1

        return total

    def _gerar_eventos_terneira(self, filhote, parto, prog, banco,
                                lotes, admin, hoje, data_parto,
                                av_col, av_umbigo, av_pes):
        from eventos.models import (
            Colostragem, CuraUmbigo, Pesagem,
            OcorrenciaSanitaria, Vacinacao, Desaleitamento,
        )
        from django.utils import timezone as tz

        idade_hoje = (hoje - data_parto).days

        # --- COLOSTRAGEM ---
        hora_nasc = tz.make_aware(
            datetime.combine(data_parto, parto.hora_parto)
        )
        # Tempo até colostragem: maioria ≤2h, alguns atrasados
        delay_min = random.choices(
            [random.randint(30, 90),
             random.randint(90, 150),
             random.randint(150, 360),
             random.randint(360, 600)],
            weights=[60, 20, 12, 8]
        )[0]
        hora_col1 = hora_nasc + timedelta(minutes=delay_min)
        brix_colostro = rand_decimal(18, 32, 1)
        # Escolhe origem
        banco_disp = [b for b in banco if b.status == 'disponivel']
        if banco_disp and random.random() < 0.3:
            origem = 'banco'
            banco_lote = random.choice(banco_disp)
        else:
            origem = 'mae'
            banco_lote = None

        col1 = Colostragem.objects.create(
            terneira=filhote,
            data_hora=hora_col1,
            volume_ml=random.randint(2000, 4500),
            origem=origem,
            banco_colostro=banco_lote,
            metodo=random.choice(['mamada_direta', 'mamadeira', 'sonda']),
            brix=brix_colostro if random.random() > 0.4 else None,
            temperatura_c=rand_decimal(37.5, 39.5, 1) if random.random() > 0.5 else None,
            ingestao_confirmada=random.random() > 0.05,
            responsavel=admin,
        )
        av_col(col1)

        # 2ª colostragem (6–12h depois)
        if random.random() > 0.2:
            col2 = Colostragem.objects.create(
                terneira=filhote,
                data_hora=hora_col1 + timedelta(hours=random.randint(6, 12)),
                volume_ml=random.randint(1500, 3000),
                origem='mae',
                metodo=random.choice(['mamada_direta', 'mamadeira']),
                brix=None,
                responsavel=admin,
            )
            av_col(col2)

        # --- CURA DE UMBIGO ---
        delay_umbigo = random.choices(
            [random.randint(15, 60),
             random.randint(60, 120),
             random.randint(120, 240)],
            weights=[70, 20, 10]
        )[0]
        hora_umbigo = hora_nasc + timedelta(minutes=delay_umbigo)
        tem_onfalite = random.random() < 0.08
        cura = CuraUmbigo.objects.create(
            terneira=filhote,
            data_hora=hora_umbigo,
            produto=random.choice(['Iodo 7%', 'Iodo 5%', 'Clorexidina 0,5%']),
            concentracao=random.choice(['7%', '5%', '0,5%']),
            metodo_aplicacao='imersão',
            coto_seco=not tem_onfalite,
            inchaço=tem_onfalite and random.random() > 0.5,
            secrecao=tem_onfalite,
            suspeita_onfalite=tem_onfalite,
            responsavel=admin,
        )
        av_umbigo(cura)
        if random.random() > 0.6 and idade_hoje > 1:
            CuraUmbigo.objects.create(
                terneira=filhote,
                data_hora=hora_nasc + timedelta(hours=random.randint(18, 36)),
                produto='Iodo 7%', concentracao='7%',
                metodo_aplicacao='imersão',
                coto_seco=random.random() > 0.3,
                responsavel=admin,
            )

        # --- PESAGENS ---
        marcos = [0, 30, 60, 90, 120, 150, 180, 240, 300, 360]
        peso_atual = float(parto.peso_nascimento or rand_decimal(
            *RACAS_PESOS_NASCIMENTO.get(filhote.raca, (30, 42)), 1))

        for dias in marcos:
            if dias > idade_hoje:
                break
            data_pes = data_parto + timedelta(days=dias)
            # Variação realista de GMD
            if dias > 0:
                gmd = rand_decimal(0.55, 0.95, 3)
                peso_atual += gmd * (dias - (marcos[marcos.index(dias) - 1]
                                             if marcos.index(dias) > 0 else 0))
            peso_com_erro = rand_decimal(peso_atual * 0.97, peso_atual * 1.03, 1)
            pes = Pesagem.objects.create(
                animal=filhote,
                data=data_pes,
                peso_kg=Decimal(str(max(peso_com_erro, 10))),
                metodo=random.choice(['balanca_digital', 'balanca_mecanica', 'fita_toracica']),
                altura_garupa_cm=rand_decimal(65, 115, 1) if random.random() > 0.4 else None,
                perimetro_toracico_cm=rand_decimal(60, 140, 1) if random.random() > 0.5 else None,
                ecc=rand_decimal(2.0, 4.0, 1) if random.random() > 0.6 else None,
                responsavel=admin,
            )
            av_pes(pes)

        # --- OCORRÊNCIAS SANITÁRIAS ---
        if idade_hoje >= 3:
            # Diarreia neonatal (0-21 dias) — ~25% das terneiras
            if random.random() < 0.25:
                inicio_diag = data_parto + timedelta(days=random.randint(3, 14))
                if inicio_diag <= hoje:
                    duracao = random.randint(3, 8)
                    fim_diag = inicio_diag + timedelta(days=duracao)
                    OcorrenciaSanitaria.objects.create(
                        animal=filhote,
                        tipo='diarreia',
                        data_inicio=inicio_diag,
                        temperatura_retal=rand_decimal(38.5, 40.5, 1),
                        sinais_clinicos='Fezes líquidas amareladas, desidratação leve',
                        diagnostico='Diarreia neonatal',
                        conduta='Reidratação oral + eletrólitos',
                        medicamento=random.choice(['Ringer Lactato', 'SRO', 'Aminoácidos']),
                        dose='2L 3x/dia',
                        data_fim=fim_diag if fim_diag <= hoje else None,
                        resultado='cura' if fim_diag <= hoje else '',
                        responsavel_tecnico=admin,
                    )

            # Pneumonia (~15% das terneiras > 30 dias)
            if idade_hoje > 30 and random.random() < 0.15:
                inicio_pneu = data_parto + timedelta(days=random.randint(20, min(60, idade_hoje - 3)))
                duracao_pneu = random.randint(5, 12)
                fim_pneu = inicio_pneu + timedelta(days=duracao_pneu)
                OcorrenciaSanitaria.objects.create(
                    animal=filhote,
                    tipo='pneumonia',
                    data_inicio=inicio_pneu,
                    temperatura_retal=rand_decimal(39.5, 41.2, 1),
                    sinais_clinicos='Tosse, corrimento nasal, respiração acelerada',
                    diagnostico='Pneumonia bacteriana',
                    conduta='Antibioticoterapia sistêmica',
                    medicamento=random.choice(['Florfenicol', 'Enrofloxacina', 'Oxitetraciclina']),
                    dose=random.choice(['20 mg/kg', '5 mg/kg', '10 mg/kg']),
                    duracao_tratamento_dias=random.randint(3, 7),
                    data_fim=fim_pneu if fim_pneu <= hoje else None,
                    resultado='cura' if fim_pneu <= hoje else '',
                    responsavel_tecnico=admin,
                )

            # Onfalite (~8% nas primeiras 2 semanas)
            if tem_onfalite and idade_hoje >= 3:
                inicio_onf = data_parto + timedelta(days=random.randint(2, 7))
                OcorrenciaSanitaria.objects.create(
                    animal=filhote,
                    tipo='onfalite',
                    data_inicio=inicio_onf,
                    temperatura_retal=rand_decimal(39.0, 40.5, 1),
                    sinais_clinicos='Umbigo edemaciado, secreção purulenta',
                    diagnostico='Onfalite',
                    conduta='Limpeza local + antibiótico sistêmico',
                    medicamento='Penicilina G Benzatina',
                    dose='20.000 UI/kg',
                    data_fim=inicio_onf + timedelta(days=7) if (inicio_onf + timedelta(days=7)) <= hoje else None,
                    resultado='cura' if (inicio_onf + timedelta(days=7)) <= hoje else '',
                    responsavel_tecnico=admin,
                )

        # --- VACINAÇÕES ---
        if idade_hoje >= 30:
            Vacinacao.objects.create(
                animal=filhote,
                data=data_parto + timedelta(days=30),
                vacina='Clostridiose polivalente',
                fabricante=random.choice(['Hipra', 'Zoetis', 'MSD']),
                dose='2ml IM',
                via='IM',
                responsavel=admin,
            )
        if idade_hoje >= 60:
            Vacinacao.objects.create(
                animal=filhote,
                data=data_parto + timedelta(days=60),
                vacina='IBR/BVD/PI3',
                fabricante=random.choice(['Hipra', 'Zoetis', 'Boehringer']),
                dose='5ml SC',
                via='SC',
                responsavel=admin,
            )

        # --- DESALEITAMENTO (terneiras > 65 dias) ---
        if idade_hoje > 65:
            idade_desaleit = random.randint(56, min(90, idade_hoje - 5))
            data_desaleit = data_parto + timedelta(days=idade_desaleit)
            pes_desaleit = Pesagem.objects.filter(
                animal=filhote, data__lte=data_desaleit
            ).order_by('-data').first()
            peso_desaleit = pes_desaleit.peso_kg if pes_desaleit else rand_decimal(65, 110, 1)
            Desaleitamento.objects.create(
                terneira=filhote,
                data=data_desaleit,
                metodo=random.choice(['abrupto', 'gradual', 'step_down']),
                peso_kg=peso_desaleit,
                consumo_concentrado_adequado=random.random() > 0.2,
                doenca_ativa=False,
                responsavel=admin,
            )
            filhote.categoria = 'novilha'
            filhote.save(update_fields=['categoria'])
            lote_pos = lotes.get('Pós-Desaleitamento')
            if lote_pos:
                from animais.models import MovimentacaoLote
                MovimentacaoLote.objects.create(
                    animal=filhote, lote=lote_pos,
                    data=data_desaleit, registrado_por=admin,
                )

    def _criar_gestacoes_ativas(self, prop, vacas, lotes, hoje):
        from animais.models import CicloReprodutivo
        count = 0
        vacas_restantes = [v for v in vacas if not CicloReprodutivo.objects.filter(
            vaca=v, situacao='gestando').exists()]

        for vaca in random.sample(vacas_restantes, min(15, len(vacas_restantes))):
            # Parto previsto: agosto/2026 a julho/2027
            dias_para_parto = random.randint(1, 355)
            data_parto_prev = date(2026, 8, 1) + timedelta(days=dias_para_parto)
            data_secagem = data_parto_prev - timedelta(days=random.randint(45, 75))
            data_pre_parto = data_parto_prev - timedelta(days=random.randint(14, 30))

            ciclo = CicloReprodutivo.objects.create(
                vaca=vaca,
                numero_lactacao=random.randint(1, 4),
                data_cobertura=data_parto_prev - timedelta(days=280),
                touro_semen=random.choice(TOUROS),
                data_previsao_parto=data_parto_prev,
                data_secagem=data_secagem if data_secagem <= hoje else None,
                tratamento_secagem=random.choice(['Vaca Seca Total', 'Secagem Seletiva']),
                data_entrada_pre_parto=data_pre_parto if data_pre_parto <= hoje else None,
                lote_pre_parto=lotes.get('Pré-Parto') if data_pre_parto <= hoje else None,
                ecc_entrada_pre_parto=rand_decimal(2.5, 4.0, 1) if data_pre_parto <= hoje else None,
                situacao='gestando',
            )

            # Move vaca para lote correto
            from animais.models import MovimentacaoLote
            if data_pre_parto <= hoje and lotes.get('Pré-Parto'):
                MovimentacaoLote.objects.create(
                    animal=vaca, lote=lotes['Pré-Parto'],
                    data=data_pre_parto,
                )
            elif data_secagem <= hoje and lotes.get('Vacas Secas'):
                MovimentacaoLote.objects.create(
                    animal=vaca, lote=lotes['Vacas Secas'],
                    data=data_secagem,
                )
            count += 1

        return count
