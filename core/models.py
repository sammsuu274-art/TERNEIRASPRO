from django.db import models


class Propriedade(models.Model):
    nome = models.CharField('Nome da propriedade', max_length=200)
    municipio = models.CharField('Município', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    responsavel_tecnico = models.CharField('Responsável técnico', max_length=200, blank=True)
    contato = models.CharField('Contato', max_length=100, blank=True)
    ativa = models.BooleanField('Ativa', default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Propriedade'
        verbose_name_plural = 'Propriedades'
        ordering = ['nome']

    def __str__(self):
        return self.nome
