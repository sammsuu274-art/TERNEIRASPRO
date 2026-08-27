from django import forms
from .models import Protocolo, MetaDesenvolvimento, PontoMetaDesenvolvimento, MetaReprodutiva


class ProtocoloForm(forms.ModelForm):
    class Meta:
        model = Protocolo
        fields = ['nome', 'categoria', 'descricao', 'versao', 'vigencia_inicio', 'vigencia_fim']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'vigencia_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class MetaDesenvolvimentoForm(forms.ModelForm):
    class Meta:
        model = MetaDesenvolvimento
        fields = ['nome', 'raca', 'fonte', 'vigencia_inicio', 'vigencia_fim', 'ativa']
        widgets = {
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'vigencia_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class PontoMetaForm(forms.ModelForm):
    class Meta:
        model = PontoMetaDesenvolvimento
        fields = ['tipo', 'idade_dias', 'valor_minimo', 'valor_ideal', 'valor_maximo', 'observacoes']


class MetaReprodutivaForm(forms.ModelForm):
    class Meta:
        model = MetaReprodutiva
        fields = [
            'nome', 'raca', 'peso_adulto_medio_kg', 'percentual_peso_adulto',
            'peso_minimo_kg', 'ecc_minimo', 'idade_minima_meses', 'idade_alvo_meses',
            'gmd_minimo_recria', 'vigencia_inicio', 'vigencia_fim', 'ativa', 'observacoes',
        ]
        widgets = {
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'vigencia_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }


from .models import CriterioConformidade


class CriterioConformidadeForm(forms.ModelForm):
    class Meta:
        model = CriterioConformidade
        fields = [
            'codigo', 'descricao_custom', 'valor_limite', 'unidade',
            'escopo_raca', 'vigencia_inicio', 'vigencia_fim',
            'referencial_base', 'ativo',
        ]
        widgets = {
            'descricao_custom': forms.TextInput(attrs={'placeholder': 'Deixe em branco para usar descrição padrão'}),
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'vigencia_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
