from django.db import models
from Especialidad.models import Especialidad
from django.urls import reverse


class Turno(models.Model):
    fecha= models.DateField()
    dni= models.IntegerField()
    obrasocial = models.CharField()
    paciente = models.CharField()
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE , related_name='turno')


    class Meta:
        verbose_name = 'turno'
        verbose_name_plural = 'turnos'
    
    def __str__(self):
        return f"Nombre: {self.paciente} - Fecha: {self.fecha} - ({self.especialidad})"
    
    def get_absolute_url(self):
        return reverse('lista_turnos', kwargs={'id': self.pk})    