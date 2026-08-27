from django import forms
from .models import CheckpointSesMeses, CoberturaIA


class CheckpointForm(forms.ModelForm):
    class Meta:
        model = CheckpointSesMeses
        fields = [
            'data_avaliacao', 'idade_dias',
            'peso_kg', 'peso_meta_kg', 'percentual_meta',
            'gmd_total', 'gmd_30_dias',
            'altura_cm', 'perimetro_toracico_cm', 'ecc',
            'diarreia_ocorrencias', 'pneumonia_ocorrencias', 'onfalite_ocorrencias',
            'total_tratamentos', 'doenca_ativa', 'desaleitada',
            'consumo_concentrado_adequado',
            'status_checkpoint', 'crescimento_estrutural',
            'status_trajetoria', 'indicadores_trajetoria',
            'observacoes', 'recomendacoes',
        ]
        widgets = {
            'data_avaliacao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'indicadores_trajetoria': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'recomendacoes': forms.Textarea(attrs={'rows': 3}),
        }


class CoberturaIAForm(forms.ModelForm):
    class Meta:
        model = CoberturaIA
        fields = [
            'data', 'tipo', 'touro_semen',
            'peso_na_ia_kg', 'ecc_na_ia',
            'numero_servico', 'observacoes',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }
