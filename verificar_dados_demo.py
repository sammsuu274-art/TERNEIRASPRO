#!/usr/bin/env python
"""Verificar dados DEMO existentes no banco"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_terneiras.settings')
django.setup()

from animais.models import Animal
from core.models import Propriedade
from accounts.models import Usuario, UsuarioPerfil

print('=== VERIFICAÇÃO DE DADOS DEMO EXISTENTES ===\n')

# Propriedades
propriedades = Propriedade.objects.all()
print(f'Propriedades: {propriedades.count()}')
for p in propriedades:
    print(f'  - ID:{p.id} | {p.nome}')

print()

# Usuários
usuarios = Usuario.objects.all()
print(f'Usuários: {usuarios.count()}')
for u in usuarios[:10]:
    perfis = u.perfis.all()
    papeis = ', '.join([p.papel for p in perfis]) if perfis.exists() else 'sem perfil'
    print(f'  - ID:{u.id} | {u.email} | Username: {u.username} | Papéis: {papeis}')

print()

# Terneiras DEMO
terneiras = Animal.objects.filter(identificacao__contains='DEMO').order_by('data_nascimento')
print(f'Terneiras DEMO: {terneiras.count()}')
for t in terneiras:
    print(f'  - ID:{t.id} | {t.identificacao} | Nasc: {t.data_nascimento} | Cat: {t.categoria}')
    if hasattr(t, 'propriedade') and t.propriedade:
        print(f'    Propriedade: {t.propriedade.nome}')

print('\n=== FIM DA VERIFICAÇÃO ===')
