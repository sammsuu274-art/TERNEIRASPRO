from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, UsuarioPerfil


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados adicionais', {'fields': ('nome_completo', 'telefone')}),
    )
    list_display = ('username', 'nome_completo', 'email', 'is_active', 'is_staff')


@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'propriedade', 'papel', 'ativo')
    list_filter = ('papel', 'ativo', 'propriedade')
