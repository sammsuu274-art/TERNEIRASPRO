from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuário customizado do sistema."""
    nome_completo = models.CharField('Nome completo', max_length=200, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome_completo or self.username


class UsuarioPerfil(models.Model):
    PAPEL_CHOICES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('produtor', 'Produtor'),
        ('auxiliar', 'Auxiliar de campo'),
    ]

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        related_name='perfis', verbose_name='Usuário',
    )
    propriedade = models.ForeignKey(
        'core.Propriedade', on_delete=models.CASCADE,
        related_name='usuarioperfil', verbose_name='Propriedade',
    )
    papel = models.CharField('Papel', max_length=20, choices=PAPEL_CHOICES, default='auxiliar')
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuário'
        verbose_name_plural = 'Perfis de usuários'
        unique_together = ('usuario', 'propriedade')
        ordering = ['propriedade__nome', 'usuario__username']

    def __str__(self):
        return f'{self.usuario} — {self.propriedade} ({self.get_papel_display()})'
