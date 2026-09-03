from django import forms
from .models import AmbienteBEA, ComportamentoBEA, VisitaPresencialBEA, ConsentimentoBEA, EvidenciasBEA, PlanoAcaoBEA, JornadaProCampo


class PlanoAcaoBEAForm(forms.ModelForm):
    class Meta:
        model = PlanoAcaoBEA
        fields = [
            'jornada', 'dominio', 'indicador', 'situacao_encontrada',
            'acao_recomendada', 'responsavel', 'prazo', 'prioridade',
            'status', 'data_conclusao', 'resultado_obtido', 'observacoes',
        ]
        widgets = {
            'jornada': forms.Select(attrs={'class': 'form-select'}),
            'dominio': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Ex: Saúde, Ambiente, Nutrição, Comportamento'}),
            'indicador': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Ex: Brix sérico baixo, cama suja'}),
            'situacao_encontrada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acao_recomendada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'prazo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_conclusao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resultado_obtido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AlterarStatusAcaoForm(forms.ModelForm):
    class Meta:
        model = PlanoAcaoBEA
        fields = ['status', 'data_conclusao', 'resultado_obtido']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_conclusao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resultado_obtido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



class AmbienteBEAForm(forms.ModelForm):
    class Meta:
        model = AmbienteBEA
        fields = [
            'data_avaliacao', 'local_paricao', 'tipo_alojamento',
            'dimensao_baia_m2', 'numero_animais_baia',
            'tipo_cama', 'profundidade_cama_cm', 'score_sujidade',
            'tem_aquecimento', 'tem_sombra', 'tem_ventilacao', 'cortinas_adequadas',
            'freq_lavagem_mamadeiras', 'freq_lavagem_bebedouros',
            'produto_higiene', 'observacoes',
        ]
        widgets = {
            'data_avaliacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'local_paricao': forms.Select(attrs={'class': 'form-select'}),
            'tipo_alojamento': forms.Select(attrs={'class': 'form-select'}),
            'dimensao_baia_m2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'numero_animais_baia': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_cama': forms.TextInput(attrs={'class': 'form-control'}),
            'profundidade_cama_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_sujidade': forms.Select(attrs={'class': 'form-select'}),
            'freq_lavagem_mamadeiras': forms.Select(attrs={'class': 'form-select'}),
            'freq_lavagem_bebedouros': forms.Select(attrs={'class': 'form-select'}),
            'produto_higiene': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ComportamentoBEAForm(forms.ModelForm):
    class Meta:
        model = ComportamentoBEA
        fields = [
            'data_avaliacao',
            'estimulo_6h', 'continuidade_diaria',
            'idade_agrupamento_dias', 'tipo_agrupamento', 'tem_enriquecimento',
            'mocacao_realizada', 'mocacao_idade_semanas', 'mocacao_metodo',
            'protocolo_dor_anestesia', 'protocolo_dor_analgesia',
            'remocao_tetas_realizada', 'protocolo_dor_tetas',
            'observacoes',
        ]
        widgets = {
            'data_avaliacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'idade_agrupamento_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_agrupamento': forms.Select(attrs={'class': 'form-select'}),
            'mocacao_idade_semanas': forms.NumberInput(attrs={'class': 'form-control'}),
            'mocacao_metodo': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class VisitaPresencialBEAForm(forms.ModelForm):
    class Meta:
        model = VisitaPresencialBEA
        fields = ['data_visita', 'responsavel_tecnico', 'produtor_visitado', 'observacoes_gerais']
        widgets = {
            'data_visita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'responsavel_tecnico': forms.Select(attrs={'class': 'form-select'}),
            'produtor_visitado': forms.Select(attrs={'class': 'form-select'}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ConsentimentoBEAForm(forms.ModelForm):
    class Meta:
        model = ConsentimentoBEA
        fields = [
            'produtor', 'data_consentimento',
            'consentimento_dados', 'consentimento_imagem',
            'responsavel_coleta', 'observacoes',
        ]
        widgets = {
            'data_consentimento': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'produtor': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_coleta': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EvidenciasBEAForm(forms.ModelForm):
    class Meta:
        model = EvidenciasBEA
        fields = ['tipo_evidencia', 'arquivo', 'descricao', 'content_type', 'object_id']
        widgets = {
            'tipo_evidencia': forms.Select(attrs={'class': 'form-select'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'object_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }
