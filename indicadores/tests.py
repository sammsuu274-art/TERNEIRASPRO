"""
Testes dos avaliadores de conformidade C1-C7
Rede de segurança para mudanças futuras no sistema
"""

from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.test import TestCase
from django.utils import timezone

from core.models import Propriedade
from accounts.models import Usuario, UsuarioPerfil
from animais.models import Animal, CicloReprodutivo
from eventos.models import Parto, Colostragem, CuraUmbigo, Pesagem
from config_tecnica.models import CriterioConformidade, MetaDesenvolvimento, PontoMetaDesenvolvimento
from indicadores.models import ResultadoConformidade
from indicadores.avaliadores import (
    avaliar_evento_parto, avaliar_evento_colostragem, 
    avaliar_evento_cura_umbigo, avaliar_evento_pesagem
)


class BaseConformidadeTest(TestCase):
    """Base class com setup comum para testes de conformidade"""
    
    def setUp(self):
        """Setup comum: propriedade, usuário, vaca e critérios padrão"""
        
        # Propriedade
        self.propriedade = Propriedade.objects.create(
            nome='Fazenda Teste BEA',
            ativa=True
        )
        
        # Usuário
        self.usuario = Usuario.objects.create_user(
            username='teste_bea',
            password='123'
        )
        UsuarioPerfil.objects.create(
            usuario=self.usuario,
            propriedade=self.propriedade,
            papel='admin',
            ativo=True
        )
        
        # Vaca mãe
        self.vaca = Animal.objects.create(
            propriedade=self.propriedade,
            identificacao='VACA-001',
            sexo='F',
            categoria='vaca',
            raca='holandes',
            data_nascimento=date(2022, 1, 15),
            situacao='ativa'
        )
        
        # Ciclo reprodutivo
        self.ciclo = CicloReprodutivo.objects.create(
            vaca=self.vaca,
            numero_lactacao=2,
            data_cobertura=date(2024, 3, 1),
            data_secagem=date(2024, 10, 1),  # 60 dias antes do parto
            data_entrada_pre_parto=date(2024, 11, 10),  # 21 dias antes
            situacao='gestando'
        )
        
        # Terneira nascida
        self.terneira = Animal.objects.create(
            propriedade=self.propriedade,
            identificacao='TERN-001', 
            sexo='F',
            categoria='terneira',
            raca='holandes',
            data_nascimento=date(2024, 12, 1),
            mae=self.vaca,
            situacao='ativa'
        )
        
        # Critérios de conformidade padrão
        self._criar_criterios_padrao()
        
        # Meta de desenvolvimento
        self._criar_meta_desenvolvimento()
        
    def _criar_criterios_padrao(self):
        """Cria critérios C1-C7 com valores padrão Embrapa"""
        criterios = [
            ('colostragem_tempo', 2.0, 'horas'),  # C1
            ('colostragem_volume_relativo', 10.0, '%'),  # C2  
            ('colostragem_brix', 22.0, '%'),  # C3
            ('umbigo_tempo', 6.0, 'horas'),  # C4
            ('dias_secos_minimo', 45.0, 'dias'),  # C5a
            ('dias_secos_maximo', 75.0, 'dias'),  # C5b
            ('dias_pre_parto_minimo', 21.0, 'dias'),  # C6
        ]
        
        for codigo, valor, unidade in criterios:
            CriterioConformidade.objects.create(
                propriedade=self.propriedade,
                codigo=codigo,
                valor_limite=Decimal(str(valor)),
                unidade=unidade,
                escopo_raca='todas',
                vigencia_inicio=date(2024, 1, 1),
                ativo=True
            )
            
    def _criar_meta_desenvolvimento(self):
        """Cria meta de desenvolvimento para C7 (peso por idade)"""
        self.meta = MetaDesenvolvimento.objects.create(
            propriedade=self.propriedade,
            nome='Holandês Padrão Teste',
            raca='holandes',
            vigencia_inicio=date(2024, 1, 1),
            ativa=True
        )
        
        # Pontos da curva (idade_dias, peso_min, peso_ideal)
        pontos = [
            (0, 35.0, 40.0),    # Nascimento
            (30, 50.0, 55.0),   # 1 mês
            (60, 70.0, 75.0),   # 2 meses
            (90, 90.0, 95.0),   # 3 meses
            (180, 150.0, 160.0) # 6 meses
        ]
        
        for idade, peso_min, peso_ideal in pontos:
            PontoMetaDesenvolvimento.objects.create(
                meta=self.meta,
                tipo='peso',
                idade_dias=idade,
                valor_minimo=Decimal(str(peso_min)),
                valor_ideal=Decimal(str(peso_ideal))
            )


class TestConformidadeC5C6Parto(BaseConformidadeTest):
    """Testes C5 (dias secos) e C6 (dias pré-parto)"""
    
    def test_c5_c6_conformes(self):
        """C5/C6: Parto com dias secos e pré-parto adequados"""
        
        # Parto conforme (60 dias secos, 21 dias pré-parto)
        parto = Parto.objects.create(
            ciclo=self.ciclo,
            terneira=self.terneira,
            data_parto=date(2024, 12, 1),
            hora_parto=time(14, 30),
            peso_nascimento=Decimal('42.0'),
            facilidade=0,
            vitalidade='normal',
            registrado_por=self.usuario
        )
        
        # Avaliar
        avaliar_evento_parto(parto)
        
        # Verificar C5 (dias secos = 61, entre 45-75) - cálculo real: 01/12 - 01/10 = 61 dias
        c5_min = ResultadoConformidade.objects.get(
            animal=self.vaca,
            evento_tipo='Parto', 
            evento_id=parto.id,
            criterio__codigo='dias_secos_minimo'
        )
        self.assertEqual(c5_min.resultado, 'conforme')
        self.assertEqual(c5_min.valor_observado, Decimal('61.000'))  # Cálculo real: 61 dias
        self.assertEqual(c5_min.valor_referencia, Decimal('45.000'))
        
        c5_max = ResultadoConformidade.objects.get(
            animal=self.vaca,
            evento_tipo='Parto',
            evento_id=parto.id, 
            criterio__codigo='dias_secos_maximo'
        )
        self.assertEqual(c5_max.resultado, 'conforme')
        self.assertEqual(c5_max.valor_observado, Decimal('61.000'))
        self.assertEqual(c5_max.valor_referencia, Decimal('75.000'))
        
        # Verificar C6 (dias pré-parto = 21, ≥21)
        c6 = ResultadoConformidade.objects.get(
            animal=self.vaca,
            evento_tipo='Parto',
            evento_id=parto.id,
            criterio__codigo='dias_pre_parto_minimo'
        )
        self.assertEqual(c6.resultado, 'conforme')
        self.assertEqual(c6.valor_observado, 21)
        self.assertEqual(c6.valor_referencia, 21)
        
    def test_c5_dado_ausente(self):
        """C5: Parto sem data de secagem = dado ausente"""
        
        # Ciclo sem data de secagem
        ciclo_sem_secagem = CicloReprodutivo.objects.create(
            vaca=self.vaca,
            numero_lactacao=3,
            data_secagem=None,  # <- Ausente
            data_entrada_pre_parto=date(2024, 11, 10),
            situacao='gestando'
        )
        
        parto = Parto.objects.create(
            ciclo=ciclo_sem_secagem,
            terneira=self.terneira,
            data_parto=date(2024, 12, 1),
            registrado_por=self.usuario
        )
        
        avaliar_evento_parto(parto)
        
        # C5 deve ser "dado ausente"
        c5_min = ResultadoConformidade.objects.get(
            animal=self.vaca,
            evento_tipo='Parto',
            evento_id=parto.id,
            criterio__codigo='dias_secos_minimo'
        )
        self.assertEqual(c5_min.resultado, 'dado_ausente')
        self.assertIsNone(c5_min.valor_observado)
        self.assertIn('secagem não registrada', c5_min.motivo_ausencia)


class TestConformidadeC1C2C3Colostragem(BaseConformidadeTest):
    """Testes C1 (tempo), C2 (volume) e C3 (Brix) da colostragem"""
    
    def setUp(self):
        super().setUp()
        
        # Parto com hora conhecida
        self.parto = Parto.objects.create(
            ciclo=self.ciclo,
            terneira=self.terneira,
            data_parto=date(2024, 12, 1),
            hora_parto=time(14, 30),  # 14:30
            peso_nascimento=Decimal('42.0'),  # 4.2L recomendados (10%)
            facilidade=0,
            vitalidade='normal',
            registrado_por=self.usuario
        )
    
    def test_c1_c2_c3_conformes(self):
        """C1/C2/C3: Colostragem ideal (1h, volume 10%, Brix 24%)"""
        
        colostragem = Colostragem.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 15, 30, tzinfo=timezone.get_current_timezone()),  # 1h após parto
            volume_ml=4200,  # 10% de 42kg
            origem='mae',
            metodo='mamadeira',
            brix=Decimal('24.0'),  # >22%
            ingestao_confirmada=True,
            responsavel=self.usuario
        )
        
        avaliar_evento_colostragem(colostragem)
        
        # C1: Tempo ≤ 2h (1h = conforme)
        c1 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id,
            criterio__codigo='colostragem_tempo'
        )
        self.assertEqual(c1.resultado, 'conforme')
        self.assertEqual(float(c1.valor_observado), 1.0)
        self.assertEqual(float(c1.valor_referencia), 2.0)
        
        # Verificar C2 (volume ≥ 10% - avaliador salva volume absoluto vs meta em ml)
        c2 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id,
            criterio__codigo='colostragem_volume_relativo'
        )
        self.assertEqual(c2.resultado, 'conforme')
        self.assertEqual(float(c2.valor_observado), 4200.0)  # Volume fornecido
        self.assertEqual(float(c2.valor_referencia), 4200.0) # Meta: 42kg * 10% = 4.2L = 4200ml
        
        # C3: Brix ≥ 22% (24% = conforme)
        c3 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Colostragem', 
            evento_id=colostragem.id,
            criterio__codigo='colostragem_brix'
        )
        self.assertEqual(c3.resultado, 'conforme')
        self.assertEqual(float(c3.valor_observado), 24.0)
        self.assertEqual(float(c3.valor_referencia), 22.0)
        
    def test_c1_nao_conforme_tempo_tardio(self):
        """C1: Colostragem após 2h = não conforme"""
        
        colostragem = Colostragem.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 17, 0, tzinfo=timezone.get_current_timezone()),  # 2.5h após parto
            volume_ml=4200,
            origem='mae',
            metodo='mamadeira',
            brix=Decimal('24.0'),
            responsavel=self.usuario
        )
        
        avaliar_evento_colostragem(colostragem)
        
        c1 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id,
            criterio__codigo='colostragem_tempo'
        )
        self.assertEqual(c1.resultado, 'nao_conforme')
        self.assertEqual(float(c1.valor_observado), 2.5)
        
    def test_c3_dado_ausente_brix(self):
        """C3: Colostragem sem Brix = deve criar resultado dado_ausente"""

        colostragem = Colostragem.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 15, 30, tzinfo=timezone.get_current_timezone()),
            volume_ml=4200,
            origem='mae',
            metodo='mamadeira',
            brix=None,  # <- Ausente
            responsavel=self.usuario
        )

        avaliar_evento_colostragem(colostragem)

        # C3 deve criar exatamente 1 resultado com dado_ausente
        resultados_brix = ResultadoConformidade.objects.filter(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id,
            criterio__codigo='colostragem_brix'
        )
        self.assertEqual(resultados_brix.count(), 1, "Avaliador Brix deve criar 1 resultado dado_ausente quando valor é None")
        resultado = resultados_brix.first()
        self.assertEqual(resultado.resultado, 'dado_ausente')
        self.assertIsNone(resultado.valor_observado)
        self.assertEqual(float(resultado.valor_referencia), 22.0)
        self.assertIn('Brix não medido', resultado.motivo_ausencia)


class TestConformidadeC4CuraUmbigo(BaseConformidadeTest):
    """Testes C4 (tempo até cura de umbigo)"""
    
    def setUp(self):
        super().setUp()
        
        self.parto = Parto.objects.create(
            ciclo=self.ciclo,
            terneira=self.terneira,
            data_parto=date(2024, 12, 1),
            hora_parto=time(14, 30),
            peso_nascimento=Decimal('42.0'),
            registrado_por=self.usuario
        )
    
    def test_c4_conforme_cura_rapida(self):
        """C4: Cura de umbigo em 2h = conforme (≤6h)"""
        
        cura = CuraUmbigo.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 16, 30, tzinfo=timezone.get_current_timezone()),  # 2h após parto
            produto='Iodo 7%',
            metodo_aplicacao='imersão',
            coto_seco=True,
            responsavel=self.usuario
        )
        
        avaliar_evento_cura_umbigo(cura)
        
        c4 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='CuraUmbigo',
            evento_id=cura.id,
            criterio__codigo='umbigo_tempo'
        )
        self.assertEqual(c4.resultado, 'conforme')
        self.assertEqual(float(c4.valor_observado), 2.0)
        self.assertEqual(float(c4.valor_referencia), 6.0)
        
    def test_c4_nao_conforme_cura_tardia(self):
        """C4: Cura de umbigo após 6h = não conforme"""
        
        cura = CuraUmbigo.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 22, 0, tzinfo=timezone.get_current_timezone()),  # 7.5h após parto
            produto='Iodo 7%',
            responsavel=self.usuario
        )
        
        avaliar_evento_cura_umbigo(cura)
        
        c4 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='CuraUmbigo',
            evento_id=cura.id,
            criterio__codigo='umbigo_tempo'
        )
        self.assertEqual(c4.resultado, 'nao_conforme')
        self.assertEqual(float(c4.valor_observado), 7.5)


class TestConformidadeC7PesoIdade(BaseConformidadeTest):
    """Testes C7 (peso adequado para idade)"""
    
    def test_c7_conforme_peso_ideal(self):
        """C7: Pesagem aos 30 dias com peso ideal = conforme"""
        
        pesagem = Pesagem.objects.create(
            animal=self.terneira,
            data=date(2024, 12, 31),  # 30 dias após nascimento (01/12)
            peso_kg=Decimal('55.0'),  # Peso ideal aos 30 dias
            metodo='balanca_digital',
            responsavel=self.usuario
        )
        
        avaliar_evento_pesagem(pesagem)
        
        c7 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Pesagem',
            evento_id=pesagem.id,
            meta_desenvolvimento=self.meta
        )
        self.assertEqual(c7.resultado, 'conforme')
        self.assertEqual(float(c7.valor_observado), 55.0)
        self.assertEqual(float(c7.valor_referencia), 50.0)  # Valor mínimo aos 30d
        
    def test_c7_nao_conforme_peso_baixo(self):
        """C7: Pesagem aos 30 dias com peso abaixo do mínimo = não conforme"""
        
        pesagem = Pesagem.objects.create(
            animal=self.terneira,
            data=date(2024, 12, 31),  # 30 dias após nascimento
            peso_kg=Decimal('45.0'),  # Abaixo do mínimo (50kg)
            metodo='balanca_digital',
            responsavel=self.usuario
        )
        
        avaliar_evento_pesagem(pesagem)
        
        c7 = ResultadoConformidade.objects.get(
            animal=self.terneira,
            evento_tipo='Pesagem',
            evento_id=pesagem.id,
            meta_desenvolvimento=self.meta
        )
        self.assertEqual(c7.resultado, 'nao_conforme')
        self.assertEqual(float(c7.valor_observado), 45.0)
        self.assertEqual(float(c7.valor_referencia), 50.0)


class TestIdempotenciaAvaliadores(BaseConformidadeTest):
    """Testa se avaliadores são idempotentes (não recriam resultados)"""
    
    def test_idempotencia_colostragem(self):
        """Avaliar a mesma colostragem 2x não deve criar resultados duplicados"""
        
        # Setup parto
        parto = Parto.objects.create(
            ciclo=self.ciclo,
            terneira=self.terneira,
            data_parto=date(2024, 12, 1),
            hora_parto=time(14, 30),
            peso_nascimento=Decimal('42.0'),
            registrado_por=self.usuario
        )
        
        colostragem = Colostragem.objects.create(
            terneira=self.terneira,
            data_hora=datetime(2024, 12, 1, 15, 30, tzinfo=timezone.get_current_timezone()),
            volume_ml=4200,
            origem='mae',
            metodo='mamadeira',
            brix=Decimal('24.0'),
            responsavel=self.usuario
        )
        
        # Primeira avaliação
        avaliar_evento_colostragem(colostragem)
        count_inicial = ResultadoConformidade.objects.filter(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id
        ).count()
        
        # Segunda avaliação (deve ser idempotente)
        avaliar_evento_colostragem(colostragem)
        count_final = ResultadoConformidade.objects.filter(
            animal=self.terneira,
            evento_tipo='Colostragem',
            evento_id=colostragem.id
        ).count()
        
        self.assertEqual(count_inicial, count_final, "Avaliador deve ser idempotente")
        self.assertEqual(count_final, 3, "Deve ter exatamente C1, C2, C3")