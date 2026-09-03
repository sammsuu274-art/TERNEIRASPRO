from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Usuario(AbstractUser):
    """Usuário customizado do sistema."""
    nome_completo = models.CharField('Nome completo', max_length=200, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome_completo or self.username

    def tem_consentimento_valido(self, propriedade=None):
        """Verifica se o usuário tem consentimento válido para BEA"""
        if propriedade is None:
            # Usar propriedade ativa da sessão ou primeira disponível
            perfil_ativo = self.perfis.filter(ativo=True).first()
            if not perfil_ativo:
                return False
            propriedade = perfil_ativo.propriedade
        
        if not propriedade:
            return False
            
        try:
            from bem_estar_animal.models import ConsentimentoBEA
            consentimento = self.consentimentos_bea.get(propriedade=propriedade)
            return consentimento.consentimento_dados and consentimento.consentimento_imagem
        except ConsentimentoBEA.DoesNotExist:
            return False

    def contar_visitas_periodo(self, data_inicio, data_fim):
        """Conta visitas recebidas pelo produtor no período especificado"""
        return self.visitas_recebidas_bea.filter(
            data_visita__gte=data_inicio,
            data_visita__lte=data_fim
        ).count()

    def alerta_meta_visitas(self):
        """Retorna True se produtor tem menos de 3 visitas nos últimos 6 meses"""
        from datetime import date, timedelta
        seis_meses_atras = date.today() - timedelta(days=180)
        visitas = self.contar_visitas_periodo(seis_meses_atras, date.today())
        return visitas < 3


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
