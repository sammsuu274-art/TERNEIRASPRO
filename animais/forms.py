from django import forms
from .models import Animal, Lote, CicloReprodutivo, MovimentacaoLote


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'identificacao', 'nome', 'sexo', 'raca', 'raca_descricao',
            'data_nascimento', 'mae', 'pai_identificacao', 'observacoes',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'raca_descricao': forms.TextInput(attrs={'placeholder': 'Detalhe raça quando Mestiça ou Outra'}),
        }

    def __init__(self, *args, propriedade=None, categoria_inicial=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.categoria_inicial = categoria_inicial
        if propriedade:
            self.fields['mae'].queryset = Animal.objects.filter(
                propriedade=propriedade, sexo='F',
            ).order_by('identificacao')
        self.fields['mae'].required = False
        self.fields['mae'].empty_label = '— Sem mãe registrada —'
        # Data: converte para o formato do input
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%Y-%m-%d')


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nome', 'tipo', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }


class CicloReprodutivoForm(forms.ModelForm):
    class Meta:
        model = CicloReprodutivo
        fields = [
            'numero_lactacao', 'data_cobertura', 'touro_semen',
            'data_previsao_parto', 'data_secagem', 'tratamento_secagem',
            'data_entrada_pre_parto', 'lote_pre_parto',
            'ecc_entrada_pre_parto', 'observacoes',
        ]
        widgets = {
            'data_cobertura': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_previsao_parto': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_secagem': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_entrada_pre_parto': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            self.fields['lote_pre_parto'].queryset = Lote.objects.filter(
                propriedade=propriedade, tipo='pre_parto', ativo=True,
            )
        self.fields['lote_pre_parto'].required = False
        self.fields['lote_pre_parto'].empty_label = '— Selecione o lote —'


class MovimentacaoLoteForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoLote
        fields = ['data', 'lote', 'motivo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'motivo': forms.TextInput(attrs={'placeholder': 'Ex: Mudança de categoria, critério de manejo...'}),
        }
        labels = {
            'lote': 'Lote destino',
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            self.fields['lote'].queryset = Lote.objects.filter(
                propriedade=propriedade, ativo=True,
            ).order_by('nome')
        self.fields['lote'].empty_label = '— Selecione o lote destino —'
