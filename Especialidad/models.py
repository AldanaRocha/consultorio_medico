from django.db import models

class Especialidad(models.Model):
    tipo = models.CharField()
    doctor = models.CharField()
    
    def __str__(self):
        return f'Especialidad: {self.tipo}  - ({self.doctor})'