"""
Comando para limpar todos os dados fictícios do sistema,
mantendo apenas a estrutura base (propriedades, usuários e configurações).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from animais.models import Animal, Lote, MovimentacaoLote, CicloReprodutivo
from eventos.models import (
    Parto, Colostragem, CuraUmbigo, Pesagem, OcorrenciaSanitaria,
    Vacinacao, Desaleitamento, BancoColostro, ProtocoloAlimentar,
    RegistroAlimentacaoDiario
)
from programas.models import (
    ProgramaAcompanhamento, CheckpointSesMeses, ProjecaoReprodutiva, CoberturaIA
)
from indicadores.models import ResultadoConformidade


class Command(BaseCommand):
    help = 'Limpa todos os dados de teste/fictícios do sistema (animais, eventos, programas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão dos dados (obrigatório para executar)',
        )
        parser.add_argument(
            '--propriedade',
            type=int,
            help='ID da propriedade específica (opcional - se omitido, limpa todas)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  ATENÇÃO: Este comando irá EXCLUIR todos os dados de animais, eventos e programas!\n'
                )
            )
            self.stdout.write('Para executar, use: python manage.py limpar_dados_teste --confirmar\n')
            self.stdout.write('Para limpar apenas uma propriedade: python manage.py limpar_dados_teste --confirmar --propriedade 1\n')
            return

        prop_id = options.get('propriedade')
        
        if prop_id:
            self.stdout.write(f'\n🗑️  Limpando dados da propriedade ID={prop_id}...\n')
            filtro = {'propriedade_id': prop_id}
            filtro_animal = {'propriedade_id': prop_id}
        else:
            self.stdout.write('\n🗑️  Limpando dados de TODAS as propriedades...\n')
            filtro = {}
            filtro_animal = {}

        # Contadores
        totais = {}

        # 1. Resultados de Conformidade
        count = ResultadoConformidade.objects.filter(animal__propriedade_id=prop_id).count() if prop_id else ResultadoConformidade.objects.count()
        ResultadoConformidade.objects.filter(animal__propriedade_id=prop_id).delete() if prop_id else ResultadoConformidade.objects.all().delete()
        totais['ResultadoConformidade'] = count
        self.stdout.write(f'  ✓ {count} resultados de conformidade removidos')

        # 2. Programas
        count = ProjecaoReprodutiva.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else ProjecaoReprodutiva.objects.count()
        ProjecaoReprodutiva.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else ProjecaoReprodutiva.objects.all().delete()
        totais['ProjecaoReprodutiva'] = count
        self.stdout.write(f'  ✓ {count} projeções reprodutivas removidas')

        count = CoberturaIA.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else CoberturaIA.objects.count()
        CoberturaIA.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else CoberturaIA.objects.all().delete()
        totais['CoberturaIA'] = count
        self.stdout.write(f'  ✓ {count} coberturas/IA removidas')

        count = CheckpointSesMeses.objects.filter(programa__terneira__propriedade_id=prop_id).count() if prop_id else CheckpointSesMeses.objects.count()
        CheckpointSesMeses.objects.filter(programa__terneira__propriedade_id=prop_id).delete() if prop_id else CheckpointSesMeses.objects.all().delete()
        totais['CheckpointSesMeses'] = count
        self.stdout.write(f'  ✓ {count} checkpoints de 6 meses removidos')

        count = ProgramaAcompanhamento.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else ProgramaAcompanhamento.objects.count()
        ProgramaAcompanhamento.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else ProgramaAcompanhamento.objects.all().delete()
        totais['ProgramaAcompanhamento'] = count
        self.stdout.write(f'  ✓ {count} programas de acompanhamento removidos')

        # 3. Eventos
        count = RegistroAlimentacaoDiario.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else RegistroAlimentacaoDiario.objects.count()
        RegistroAlimentacaoDiario.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else RegistroAlimentacaoDiario.objects.all().delete()
        totais['RegistroAlimentacaoDiario'] = count
        self.stdout.write(f'  ✓ {count} registros de alimentação removidos')

        count = ProtocoloAlimentar.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else ProtocoloAlimentar.objects.count()
        ProtocoloAlimentar.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else ProtocoloAlimentar.objects.all().delete()
        totais['ProtocoloAlimentar'] = count
        self.stdout.write(f'  ✓ {count} protocolos alimentares removidos')

        count = Desaleitamento.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else Desaleitamento.objects.count()
        Desaleitamento.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else Desaleitamento.objects.all().delete()
        totais['Desaleitamento'] = count
        self.stdout.write(f'  ✓ {count} desaleitamentos removidos')

        count = Vacinacao.objects.filter(animal__propriedade_id=prop_id).count() if prop_id else Vacinacao.objects.count()
        Vacinacao.objects.filter(animal__propriedade_id=prop_id).delete() if prop_id else Vacinacao.objects.all().delete()
        totais['Vacinacao'] = count
        self.stdout.write(f'  ✓ {count} vacinações removidas')

        count = OcorrenciaSanitaria.objects.filter(animal__propriedade_id=prop_id).count() if prop_id else OcorrenciaSanitaria.objects.count()
        OcorrenciaSanitaria.objects.filter(animal__propriedade_id=prop_id).delete() if prop_id else OcorrenciaSanitaria.objects.all().delete()
        totais['OcorrenciaSanitaria'] = count
        self.stdout.write(f'  ✓ {count} ocorrências sanitárias removidas')

        count = Pesagem.objects.filter(animal__propriedade_id=prop_id).count() if prop_id else Pesagem.objects.count()
        Pesagem.objects.filter(animal__propriedade_id=prop_id).delete() if prop_id else Pesagem.objects.all().delete()
        totais['Pesagem'] = count
        self.stdout.write(f'  ✓ {count} pesagens removidas')

        count = CuraUmbigo.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else CuraUmbigo.objects.count()
        CuraUmbigo.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else CuraUmbigo.objects.all().delete()
        totais['CuraUmbigo'] = count
        self.stdout.write(f'  ✓ {count} curas de umbigo removidas')

        count = Colostragem.objects.filter(terneira__propriedade_id=prop_id).count() if prop_id else Colostragem.objects.count()
        Colostragem.objects.filter(terneira__propriedade_id=prop_id).delete() if prop_id else Colostragem.objects.all().delete()
        totais['Colostragem'] = count
        self.stdout.write(f'  ✓ {count} colostragens removidas')

        count = Parto.objects.filter(ciclo__vaca__propriedade_id=prop_id).count() if prop_id else Parto.objects.count()
        Parto.objects.filter(ciclo__vaca__propriedade_id=prop_id).delete() if prop_id else Parto.objects.all().delete()
        totais['Parto'] = count
        self.stdout.write(f'  ✓ {count} partos removidos')

        count = BancoColostro.objects.filter(**filtro).count()
        BancoColostro.objects.filter(**filtro).delete()
        totais['BancoColostro'] = count
        self.stdout.write(f'  ✓ {count} lotes do banco de colostro removidos')

        # 4. Animais e estrutura
        count = CicloReprodutivo.objects.filter(vaca__propriedade_id=prop_id).count() if prop_id else CicloReprodutivo.objects.count()
        CicloReprodutivo.objects.filter(vaca__propriedade_id=prop_id).delete() if prop_id else CicloReprodutivo.objects.all().delete()
        totais['CicloReprodutivo'] = count
        self.stdout.write(f'  ✓ {count} ciclos reprodutivos removidos')

        count = MovimentacaoLote.objects.filter(animal__propriedade_id=prop_id).count() if prop_id else MovimentacaoLote.objects.count()
        MovimentacaoLote.objects.filter(animal__propriedade_id=prop_id).delete() if prop_id else MovimentacaoLote.objects.all().delete()
        totais['MovimentacaoLote'] = count
        self.stdout.write(f'  ✓ {count} movimentações de lote removidas')

        count = Animal.objects.filter(**filtro_animal).count()
        Animal.objects.filter(**filtro_animal).delete()
        totais['Animal'] = count
        self.stdout.write(f'  ✓ {count} animais removidos')

        # Lotes mantém estrutura mas sem animais
        self.stdout.write(f'  ℹ️  Lotes mantidos (estrutura preservada)')

        # Resumo final
        total_registros = sum(totais.values())
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Limpeza concluída! {total_registros} registros removidos no total.\n'
            )
        )
        
        self.stdout.write('📊 Resumo por tipo:')
        for modelo, count in totais.items():
            if count > 0:
                self.stdout.write(f'   • {modelo}: {count}')

        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Mantidos: Propriedades, Usuários, Vínculos, Lotes, Protocolos, Metas e Referenciais\n'
            )
        )
