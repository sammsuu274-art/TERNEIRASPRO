from django import forms
from .models import Propriedade


class PropriedadeForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ['nome', 'municipio', 'estado', 'responsavel_tecnico', 'contato']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da fazenda ou propriedade'}),
            'municipio': forms.TextInput(attrs={'placeholder': 'Município'}),
            'estado': forms.TextInput(attrs={'placeholder': 'UF', 'maxlength': 2}),
            'responsavel_tecnico': forms.TextInput(attrs={'placeholder': 'Nome do responsável técnico (opcional)'}),
            'contato': forms.TextInput(attrs={'placeholder': 'Telefone ou e-mail (opcional)'}),
        }


class PropriedadeEditForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ['nome', 'municipio', 'estado', 'responsavel_tecnico', 'contato', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da fazenda ou propriedade'}),
            'municipio': forms.TextInput(attrs={'placeholder': 'Município'}),
            'estado': forms.TextInput(attrs={'placeholder': 'UF', 'maxlength': 2}),
            'responsavel_tecnico': forms.TextInput(attrs={'placeholder': 'Nome do responsável técnico (opcional)'}),
            'contato': forms.TextInput(attrs={'placeholder': 'Telefone ou e-mail (opcional)'}),
        }


class NovoUsuarioForm(forms.Form):
    username = forms.CharField(label='Login (usuário)', max_length=150)
    nome_completo = forms.CharField(label='Nome completo', max_length=200)
    email = forms.EmailField(label='E-mail', required=False)
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('senha') != cleaned.get('confirmar_senha'):
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned

    def clean_username(self):
        from accounts.models import Usuario
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este login já está em uso.')
        return username

    def save(self):
        from accounts.models import Usuario
        data = self.cleaned_data
        user = Usuario.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['senha'],
        )
        user.nome_completo = data.get('nome_completo', '')
        user.telefone = data.get('telefone', '')
        user.save()
        return user


class EditarUsuarioForm(forms.Form):
    nome_completo = forms.CharField(label='Nome completo', max_length=200)
    email = forms.EmailField(label='E-mail', required=False)
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    ativo = forms.BooleanField(label='Ativo', required=False)
    nova_senha = forms.CharField(
        label='Nova senha', widget=forms.PasswordInput, required=False,
        help_text='Deixe em branco para não alterar',
    )

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        initial = {}
        if instance:
            initial = {
                'nome_completo': instance.nome_completo,
                'email': instance.email,
                'telefone': instance.telefone,
                'ativo': instance.is_active,
            }
        super().__init__(*args, initial=initial, **kwargs)

    def save(self):
        data = self.cleaned_data
        self.instance.nome_completo = data['nome_completo']
        self.instance.email = data.get('email', '')
        self.instance.telefone = data.get('telefone', '')
        self.instance.is_active = data.get('ativo', True)
        if data.get('nova_senha'):
            self.instance.set_password(data['nova_senha'])
        self.instance.save()
        return self.instance


class VinculoForm(forms.Form):
    usuario = forms.ModelChoiceField(
        label='Usuário',
        queryset=None,
        empty_label='— Selecione o usuário —',
    )
    propriedade = forms.ModelChoiceField(
        label='Propriedade',
        queryset=None,
        empty_label='— Selecione a propriedade —',
    )
    papel = forms.ChoiceField(
        label='Papel',
        choices=[
            ('admin', 'Administrador'),
            ('tecnico', 'Técnico'),
            ('produtor', 'Produtor'),
            ('auxiliar', 'Auxiliar de campo'),
        ],
    )
    ativo = forms.BooleanField(label='Ativo', required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Usuario
        self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True).order_by('nome_completo', 'username')
        self.fields['propriedade'].queryset = Propriedade.objects.filter(ativa=True).order_by('nome')

    def clean(self):
        cleaned = super().clean()
        from accounts.models import UsuarioPerfil
        usuario = cleaned.get('usuario')
        propriedade = cleaned.get('propriedade')
        if usuario and propriedade:
            if UsuarioPerfil.objects.filter(usuario=usuario, propriedade=propriedade).exists():
                raise forms.ValidationError(f'{usuario} já está vinculado a {propriedade}.')
        return cleaned

    def save(self):
        from accounts.models import UsuarioPerfil
        data = self.cleaned_data
        return UsuarioPerfil.objects.create(
            usuario=data['usuario'],
            propriedade=data['propriedade'],
            papel=data['papel'],
            ativo=data.get('ativo', True),
        )
