from django import forms
from .models import (
    Parto, Colostragem, CuraUmbigo, Pesagem,
    OcorrenciaSanitaria, Vacinacao, Desaleitamento,
    BancoColostro, ProtocoloAlimentar,
)


class PartoForm(forms.ModelForm):
    class Meta:
        model = Parto
        fields = [
            'data_parto', 'hora_parto', 'facilidade', 'assistencia',
            'gemelar', 'peso_nascimento', 'vitalidade',
            'lesoes_anormalidades', 'observacoes',
        ]
        widgets = {
            'data_parto': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_parto': forms.TimeInput(attrs={'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
            'lesoes_anormalidades': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar peso obrigatório - é usado no cálculo de colostro
        self.fields['peso_nascimento'].required = True
        self.fields['peso_nascimento'].help_text = 'Necessário para calcular volume recomendado de colostro (10% do peso)'


class ColostragemmForm(forms.ModelForm):
    class Meta:
        model = Colostragem
        fields = [
            'data_hora', 'volume_ml', 'origem', 'banco_colostro',
            'metodo', 'brix', 'temperatura_c', 'ingestao_confirmada', 'observacoes',
        ]
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            from .models import BancoColostro
            self.fields['banco_colostro'].queryset = BancoColostro.objects.filter(
                propriedade=propriedade, status='disponivel',
            )
        self.fields['banco_colostro'].required = False
        self.fields['banco_colostro'].empty_label = '— Não usar banco —'
        self.fields['brix'].required = False
        self.fields['temperatura_c'].required = False


class CuraUmbigoForm(forms.ModelForm):
    class Meta:
        model = CuraUmbigo
        fields = [
            'data_hora', 'produto', 'concentracao', 'metodo_aplicacao',
            'coto_seco', 'inchaço', 'secrecao', 'odor',
            'sangramento', 'dor_palpacao', 'suspeita_onfalite', 'observacoes',
        ]
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


class PesagemForm(forms.ModelForm):
    class Meta:
        model = Pesagem
        fields = [
            'data', 'peso_kg', 'metodo', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos principais já são obrigatórios por padrão
        self.fields['peso_kg'].help_text = 'Peso atual do animal'
        self.fields['metodo'].help_text = 'Método usado para obter a medição'


class PesagemComplementarForm(forms.ModelForm):
    """Formulário para medições complementares opcionais."""
    class Meta:
        model = Pesagem
        fields = [
            'data', 'peso_kg', 'metodo',
            'altura_garupa_cm', 'perimetro_toracico_cm', 'ecc', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['peso_kg'].help_text = 'Peso atual do animal'
        self.fields['altura_garupa_cm'].help_text = 'Medição opcional - para acompanhamento detalhado'
        self.fields['perimetro_toracico_cm'].help_text = 'Medição opcional - para acompanhamento detalhado'
        self.fields['ecc'].help_text = 'Medição opcional - escala 1,0 a 5,0'


class OcorrenciaSanitariaForm(forms.ModelForm):
    class Meta:
        model = OcorrenciaSanitaria
        fields = [
            'tipo', 'data_inicio', 'temperatura_retal',
            'sinais_clinicos', 'diagnostico', 'conduta',
            'medicamento', 'dose', 'via_administracao',
            'duracao_tratamento_dias', 'observacoes',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'sinais_clinicos': forms.Textarea(attrs={'rows': 2}),
            'conduta': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


class EncerrarOcorrenciaForm(forms.ModelForm):
    class Meta:
        model = OcorrenciaSanitaria
        fields = ['data_fim', 'resultado', 'observacoes']
        widgets = {
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


class VacinacaoForm(forms.ModelForm):
    class Meta:
        model = Vacinacao
        fields = ['data', 'vacina', 'fabricante', 'lote_produto', 'dose', 'via', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


class DesaleitamentoForm(forms.ModelForm):
    class Meta:
        model = Desaleitamento
        fields = [
            'data', 'metodo', 'peso_kg',
            'consumo_concentrado_adequado', 'doenca_ativa', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


class BancoColostroForm(forms.ModelForm):
    class Meta:
        model = BancoColostro
        fields = [
            'data_coleta', 'vaca_origem', 'brix', 'volume_ml',
            'congelado', 'data_congelamento', 'lote',
            'validade', 'local_armazenamento', 'observacoes',
        ]
        widgets = {
            'data_coleta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_congelamento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'validade': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            from animais.models import Animal
            self.fields['vaca_origem'].queryset = Animal.objects.filter(
                propriedade=propriedade, sexo='F', categoria='vaca',
            )
        self.fields['vaca_origem'].required = False
        self.fields['vaca_origem'].empty_label = '— Origem não identificada —'
